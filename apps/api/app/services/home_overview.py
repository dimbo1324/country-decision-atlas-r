from app.repositories import home_overview as repository
from app.repositories.common import build_locale
from app.schemas.cii_matrix import CompareMatrixResponse, MatrixCell
from app.schemas.home_overview import (
    CountryOverviewCard,
    HomeKeyInsight,
    HomeLegalSourceRef,
    HomeMatrixCell,
    HomeMatrixCountry,
    HomeMatrixPreview,
    HomeMatrixScenario,
    HomeOverviewResponse,
    LatestLegalEvent,
    ScenarioWinner,
)
from app.services.cache import cache_ttl, get_cache_backend
from app.services.cache_keys import home_overview_key
from app.services.cii_matrix import build_matrix_response
from app.services.localization import overlay_localized_fields
from psycopg import Connection
from typing import Any


_CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def build_home_overview(
    connection: Connection[Any], locale: str
) -> HomeOverviewResponse:
    key = home_overview_key(locale)
    cached = get_cache_backend().get_or_set_json(
        key,
        cache_ttl(),
        lambda: _build_home_overview_uncached(connection, locale).model_dump(
            mode="json"
        ),
    )
    return HomeOverviewResponse.model_validate(cached)


def _build_home_overview_uncached(
    connection: Connection[Any], locale: str
) -> HomeOverviewResponse:
    matrix = build_matrix_response(connection, None, None, locale)
    event_rows = repository.list_latest_legal_events(connection, 5)
    event_rows = overlay_localized_fields(
        connection,
        event_rows,
        "legal_signal",
        "legal_signal_id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    countries = _countries_summary(matrix)
    winners = _scenario_winners(matrix)
    events = [_latest_event(row) for row in event_rows]
    warnings = list(matrix.quality_warnings)
    if not events:
        warnings.append("latest legal events are unavailable")
    return HomeOverviewResponse(
        locale=build_locale(event_rows, locale) if event_rows else matrix.locale,
        countries_summary=countries,
        scenario_winners=winners,
        matrix_preview=_matrix_preview(matrix),
        latest_legal_events=events,
        key_insights=_key_insights(countries, winners, events, locale),
        quality_warnings=warnings,
    )


def _countries_summary(matrix: CompareMatrixResponse) -> list[CountryOverviewCard]:
    scenarios = {scenario.slug: scenario for scenario in matrix.scenarios}
    result: list[CountryOverviewCard] = []
    for country in matrix.countries:
        scored = [
            cell
            for cell in matrix.cells
            if cell.country_slug == country.slug and cell.cii_score is not None
        ]
        best = max(scored, key=_score) if scored else None
        weakest = min(scored, key=_score) if scored else None
        average = (
            round(sum(_score(cell) for cell in scored) / len(scored), 2)
            if scored
            else None
        )
        confidences = [cell.cii_confidence for cell in scored if cell.cii_confidence]
        confidence = (
            min(confidences, key=lambda value: _CONFIDENCE_ORDER.get(value, -1))
            if confidences
            else None
        )
        result.append(
            CountryOverviewCard(
                slug=country.slug,
                name=country.name,
                iso2=country.iso2,
                best_scenario_slug=best.scenario_slug if best else None,
                best_scenario_name=(
                    scenarios[best.scenario_slug].name
                    if best and best.scenario_slug in scenarios
                    else None
                ),
                best_score=_score(best) if best else None,
                weakest_scenario_slug=weakest.scenario_slug if weakest else None,
                weakest_scenario_name=(
                    scenarios[weakest.scenario_slug].name
                    if weakest and weakest.scenario_slug in scenarios
                    else None
                ),
                weakest_score=_score(weakest) if weakest else None,
                average_score=average,
                confidence=confidence,
            )
        )
    return result


def _scenario_winners(matrix: CompareMatrixResponse) -> list[ScenarioWinner]:
    countries = {country.slug: country for country in matrix.countries}
    winners: list[ScenarioWinner] = []
    for scenario in matrix.scenarios:
        scored = sorted(
            [
                cell
                for cell in matrix.cells
                if cell.scenario_slug == scenario.slug and cell.cii_score is not None
            ],
            key=_score,
            reverse=True,
        )
        winner = scored[0] if scored else None
        runner_up = scored[1] if len(scored) > 1 else None
        winners.append(
            ScenarioWinner(
                scenario_slug=scenario.slug,
                scenario_name=scenario.name,
                winner_country_slug=winner.country_slug if winner else None,
                winner_country_name=(
                    countries[winner.country_slug].name
                    if winner and winner.country_slug in countries
                    else None
                ),
                winner_score=_score(winner) if winner else None,
                runner_up_country_slug=runner_up.country_slug if runner_up else None,
                runner_up_country_name=(
                    countries[runner_up.country_slug].name
                    if runner_up and runner_up.country_slug in countries
                    else None
                ),
                runner_up_score=_score(runner_up) if runner_up else None,
                delta=(
                    round(_score(winner) - _score(runner_up), 2)
                    if winner and runner_up
                    else None
                ),
            )
        )
    return winners


def _matrix_preview(matrix: CompareMatrixResponse) -> HomeMatrixPreview:
    return HomeMatrixPreview(
        countries=[
            HomeMatrixCountry.model_validate(item, from_attributes=True)
            for item in matrix.countries
        ],
        scenarios=[
            HomeMatrixScenario.model_validate(item, from_attributes=True)
            for item in matrix.scenarios
        ],
        cells=[
            HomeMatrixCell(
                country_slug=cell.country_slug,
                scenario_slug=cell.scenario_slug,
                score=cell.cii_score,
                confidence=cell.cii_confidence,
                score_label=cell.score_label,
            )
            for cell in matrix.cells
        ],
    )


def _latest_event(row: dict[str, Any]) -> LatestLegalEvent:
    source = None
    if row.get("source_ref_id") and row.get("source_title") and row.get("source_url"):
        source = HomeLegalSourceRef(
            id=row["source_ref_id"], title=row["source_title"], url=row["source_url"]
        )
    return LatestLegalEvent(
        country_slug=row["country_slug"],
        country_name=row["country_name"],
        event_date=row["event_date"],
        title=row["title"],
        summary=row.get("summary"),
        impact_direction=row["impact_direction"],
        impact_level=row["impact_level"],
        source=source,
    )


def _key_insights(
    countries: list[CountryOverviewCard],
    winners: list[ScenarioWinner],
    events: list[LatestLegalEvent],
    locale: str,
) -> list[HomeKeyInsight]:
    insights: list[HomeKeyInsight] = []
    scored_winners = [winner for winner in winners if winner.winner_country_slug]
    winner_slugs = {winner.winner_country_slug for winner in scored_winners}
    if scored_winners and len(winner_slugs) == 1:
        leader_slug = next(iter(winner_slugs))
        leader = next(
            (country for country in countries if country.slug == leader_slug), None
        )
        if leader:
            insights.append(
                HomeKeyInsight(
                    kind="scenario_leader",
                    title=(
                        f"{leader.name} лидирует во всех сценариях"
                        if locale == "ru"
                        else f"{leader.name} leads every scenario"
                    ),
                    summary=(
                        "Лидер имеет самый высокий доступный CII во всех сценариях MVP."
                        if locale == "ru"
                        else "The leader has the highest available CII in every MVP scenario."
                    ),
                    severity="positive",
                    target_url="/compare",
                )
            )
    for country in countries:
        if country.average_score is not None and country.average_score < 30:
            insights.append(
                HomeKeyInsight(
                    kind="low_country_average",
                    title=(
                        f"{country.name}: низкий средний CII"
                        if locale == "ru"
                        else f"{country.name}: low average CII"
                    ),
                    summary=(
                        "Средняя оценка по доступным сценариям ниже 30 и требует осторожной проверки рисков."
                        if locale == "ru"
                        else "The average across available scenarios is below 30 and warrants careful risk review."
                    ),
                    severity="risk",
                    target_url=f"/countries/{country.slug}",
                )
            )
    if not events:
        insights.append(
            HomeKeyInsight(
                kind="legal_events_missing",
                title=(
                    "Недавние правовые события недоступны"
                    if locale == "ru"
                    else "Recent legal events are unavailable"
                ),
                summary=(
                    "Лента пока не содержит событий для обзорного блока."
                    if locale == "ru"
                    else "The timeline currently has no events for the overview."
                ),
                severity="warning",
                target_url="/legal-signals",
            )
        )
    return insights


def _score(cell: MatrixCell) -> float:
    return float(cell.cii_score or 0.0)

from app.core.locales import SOURCE_LOCALE, validate_locale
from app.repositories import decision_engine as repository
from app.repositories.common import build_locale
from app.schemas.common import (
    LocaleCode,
    LocaleResolution,
    Pagination,
    source_locale_resolution,
)
from app.schemas.decision_engine import (
    CountryCardResponse,
    DecisionCompareInput,
    DecisionCompareResult,
    DecisionCountryScore,
    DecisionRunCountry,
    DecisionRunInput,
    DecisionRunResult,
    DecisionScenario,
    EvidenceListResponse,
    LegalSignalDetailResponse,
    SourceListWithLocaleResponse,
    UserStoryCreate,
    UserStoryListResponse,
    UserStoryResponse,
)
from app.schemas.sources import EvidenceItemListResponse
from psycopg import Connection
from typing import Any


CAVEAT = (
    "This MVP decision output is not legal, tax, immigration, investment, or safety advice. "
    "Use it as a structured question list and verify every claim with qualified experts."
)
CAVEAT_RU = (
    "\u042d\u0442\u043e\u0442 MVP-\u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043d\u0435 \u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f \u044e\u0440\u0438\u0434\u0438\u0447\u0435\u0441\u043a\u043e\u0439, \u043d\u0430\u043b\u043e\u0433\u043e\u0432\u043e\u0439, \u043c\u0438\u0433\u0440\u0430\u0446\u0438\u043e\u043d\u043d\u043e\u0439, "
    "\u0438\u043d\u0432\u0435\u0441\u0442\u0438\u0446\u0438\u043e\u043d\u043d\u043e\u0439 \u0438\u043b\u0438 \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u0446\u0438\u0435\u0439 \u043f\u043e \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438. \u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u0435\u0433\u043e \u043a\u0430\u043a "
    "\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0441\u043f\u0438\u0441\u043e\u043a \u0432\u043e\u043f\u0440\u043e\u0441\u043e\u0432 \u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0439\u0442\u0435 \u043a\u0430\u0436\u0434\u044b\u0439 \u0432\u044b\u0432\u043e\u0434 \u0441 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430\u043c\u0438."
)


def _locale(rows: list[dict[str, Any]], requested_locale: str) -> LocaleResolution:
    return build_locale(rows, requested_locale)


def get_country_card(
    connection: Connection[Any], country_slug: str, locale: str
) -> CountryCardResponse:
    row = repository.get_country_card(connection, country_slug, locale)
    if row is None:
        raise LookupError("Country card not found")
    return CountryCardResponse(item=row, locale=_locale([row], locale))


def get_scenario(connection: Connection[Any], slug: str, locale: str) -> dict[str, Any]:
    row = repository.get_scenario(connection, slug, locale)
    if row is None:
        raise LookupError("Scenario not found")
    return row


def list_scenario_countries(
    connection: Connection[Any], scenario_slug: str, locale: str
) -> list[DecisionCountryScore]:
    rows = repository.list_scenario_countries(connection, scenario_slug, locale)
    return _attach_breakdowns_and_sources(connection, rows, locale)


def get_country_sources(
    connection: Connection[Any], country_slug: str, locale: str, limit: int, offset: int
) -> SourceListWithLocaleResponse:
    rows = repository.list_country_sources(connection, country_slug, limit, offset)
    total = repository.count_country_sources(connection, country_slug)
    return SourceListWithLocaleResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=source_locale_resolution(locale),
    )


def list_legal_signals(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], Pagination, LocaleResolution]:
    rows = repository.list_legal_signals(
        connection, locale, country_slug, limit, offset
    )
    total = repository.count_legal_signals(connection, country_slug)
    return (
        rows,
        Pagination(limit=limit, offset=offset, total=total),
        _locale(rows, locale),
    )


def get_legal_signal(
    connection: Connection[Any], signal_id: str, locale: str
) -> LegalSignalDetailResponse:
    row = repository.get_legal_signal(connection, signal_id, locale)
    if row is None:
        raise LookupError("Legal signal not found")
    return LegalSignalDetailResponse(item=row, locale=_locale([row], locale))


def get_legal_signal_evidence(
    connection: Connection[Any], signal_id: str
) -> EvidenceListResponse:
    rows = repository.list_evidence_for_legal_signal(connection, signal_id)
    return EvidenceListResponse(
        items=rows,
        pagination=Pagination(limit=len(rows) or 1, offset=0, total=len(rows)),
    )


def get_source(connection: Connection[Any], source_id: str) -> dict[str, Any]:
    row = repository.get_source(connection, source_id)
    if row is None:
        raise LookupError("Source not found")
    return row


def get_source_evidence(
    connection: Connection[Any], source_id: str, limit: int, offset: int
) -> EvidenceItemListResponse:
    rows = repository.list_evidence_for_source(connection, source_id, limit, offset)
    total = repository.count_evidence_for_source(connection, source_id)
    return EvidenceItemListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


def list_user_stories(
    connection: Connection[Any], limit: int, offset: int
) -> UserStoryListResponse:
    rows = repository.list_user_stories(connection, limit, offset)
    total = repository.count_user_stories(connection)
    return UserStoryListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


def get_user_story(connection: Connection[Any], story_id: str) -> UserStoryResponse:
    row = repository.get_user_story(connection, story_id)
    if row is None:
        raise LookupError("User story not found")
    return UserStoryResponse(item=row)


def create_user_story(
    connection: Connection[Any], payload: UserStoryCreate
) -> UserStoryResponse:
    row = repository.create_user_story(connection, payload)
    connection.commit()
    return UserStoryResponse(item=row)


def compare_countries(
    connection: Connection[Any], payload: DecisionCompareInput
) -> DecisionCompareResult:
    locale = validate_locale(str(payload.locale))
    scenario_row = get_scenario(connection, payload.scenario_slug, locale)
    rows = repository.list_scenario_countries(connection, payload.scenario_slug, locale)
    rows = [row for row in rows if row["country_slug"] in payload.country_slugs]
    countries = _attach_breakdowns_and_sources(connection, rows, locale)
    if len(countries) != len(set(payload.country_slugs)):
        raise LookupError("One or more country scores were not found")
    recommendation_type, recommended_country, confidence = _recommend(countries)
    explanation = _compare_explanation(
        countries, recommended_country, recommendation_type, locale
    )
    return DecisionCompareResult(
        scenario=_scenario_model(scenario_row),
        countries=countries,
        recommended_country=recommended_country,
        recommendation_type=recommendation_type,
        confidence=confidence,
        explanation=explanation,
        caveat=_caveat(locale),
        locale=_locale([scenario_row], locale),
    )


def run_decision(
    connection: Connection[Any], payload: DecisionRunInput
) -> DecisionRunResult:
    locale = validate_locale(str(payload.locale))
    scenario_row = get_scenario(connection, payload.scenario_slug, locale)
    rows = repository.list_scenario_countries(connection, payload.scenario_slug, locale)
    rows = [
        row for row in rows if row["country_slug"] in payload.candidate_country_slugs
    ]
    countries = _attach_breakdowns_and_sources(connection, rows, locale)
    if not countries:
        raise LookupError("Candidate country scores were not found")
    countries = sorted(countries, key=lambda item: item.score, reverse=True)
    recommendation_type, recommended_country, confidence = _recommend(countries)
    ranked = [
        DecisionRunCountry(
            country=country,
            rank=index + 1,
            risks=_risks_for_country(country),
            key_legal_signals=repository.list_legal_signals(
                connection, locale, country.country_slug, 3, 0
            ),
            source_references=country.source_references,
        )
        for index, country in enumerate(countries)
    ]
    return DecisionRunResult(
        scenario=_scenario_model(scenario_row),
        origin_country_slug=payload.origin_country_slug,
        ranked_candidates=ranked,
        recommended_country=recommended_country,
        confidence=confidence,
        explanation=_compare_explanation(
            countries, recommended_country, recommendation_type, locale
        ),
        caveat=_caveat(locale),
        locale=_locale([scenario_row], locale),
    )


def _attach_breakdowns_and_sources(
    connection: Connection[Any], rows: list[dict[str, Any]], locale: str
) -> list[DecisionCountryScore]:
    score_ids = [str(row["id"]) for row in rows]
    breakdown_rows = repository.list_score_breakdowns(connection, score_ids)
    source_rows = repository.list_score_sources(
        connection, sorted({row["country_slug"] for row in rows})
    )
    breakdowns_by_score: dict[str, list[dict[str, Any]]] = {}
    for breakdown in breakdown_rows:
        breakdown["explanation"] = _localized_explanation(
            breakdown.get("explanation_en"),
            breakdown.get("explanation_ru"),
            locale,
        )
        breakdown["translation_status"] = _field_translation_status(
            breakdown.get("explanation_en"),
            breakdown.get("explanation_ru"),
            locale,
        )
        breakdowns_by_score.setdefault(str(breakdown["country_score_id"]), []).append(
            breakdown
        )
    sources_by_country: dict[str, list[dict[str, Any]]] = {}
    for source in source_rows:
        for row in rows:
            if source["country_id"] == row["country_id"]:
                sources_by_country.setdefault(row["country_slug"], []).append(source)
    return [
        DecisionCountryScore(
            **row,
            breakdowns=breakdowns_by_score.get(str(row["id"]), []),
            source_references=sources_by_country.get(row["country_slug"], [])[:5],
        )
        for row in rows
    ]


def _scenario_model(row: dict[str, Any]) -> DecisionScenario:
    return DecisionScenario(
        id=row["id"],
        slug=row["slug"],
        title=row["title"],
        description=row["description"],
        weights=row["weights"],
    )


def _recommend(
    countries: list[DecisionCountryScore],
) -> tuple[str, str | None, str]:
    if len(countries) < 2:
        return "winner", countries[0].country_slug if countries else None, "medium"
    ordered = sorted(countries, key=lambda item: item.score, reverse=True)
    delta = ordered[0].score - ordered[1].score
    if delta < 3:
        return "tie", None, "low"
    return "winner", ordered[0].country_slug, "medium" if delta < 10 else "high"


def _compare_explanation(
    countries: list[DecisionCountryScore],
    recommended_country: str | None,
    recommendation_type: str,
    locale: str,
) -> str:
    ordered = sorted(countries, key=lambda item: item.score, reverse=True)
    if recommendation_type == "tie" or recommended_country is None:
        if locale == LocaleCode.ru:
            return "\u0421\u0442\u0440\u0430\u043d\u044b-\u043b\u0438\u0434\u0435\u0440\u044b \u0431\u043b\u0438\u0437\u043a\u0438 \u043f\u043e \u0431\u0430\u043b\u043b\u0430\u043c, \u043f\u043e\u044d\u0442\u043e\u043c\u0443 \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u044f \u0438\u043c\u0435\u0435\u0442 \u043d\u0438\u0437\u043a\u0443\u044e \u0443\u0432\u0435\u0440\u0435\u043d\u043d\u043e\u0441\u0442\u044c."
        return "The top countries are close in score, so the recommendation is low-confidence."
    if locale == LocaleCode.ru:
        return (
            f"{recommended_country} \u0438\u043c\u0435\u0435\u0442 \u0441\u0430\u043c\u044b\u0439 \u0432\u044b\u0441\u043e\u043a\u0438\u0439 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0439 MVP-\u0431\u0430\u043b\u043b "
            f"({ordered[0].score:.1f}) \u0434\u043b\u044f \u044d\u0442\u043e\u0433\u043e \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0440\u0430\u0437\u0431\u0438\u0432\u043a\u0443 \u0438 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0438 \u043f\u0435\u0440\u0435\u0434 \u0440\u0435\u0448\u0435\u043d\u0438\u0435\u043c."
        )
    return (
        f"{recommended_country} has the highest stored MVP decision score "
        f"({ordered[0].score:.1f}) for this scenario. Review the breakdowns and sources before acting."
    )


def _localized_explanation(
    explanation_en: str | None, explanation_ru: str | None, locale: str
) -> str:
    if locale == LocaleCode.ru and explanation_ru:
        return explanation_ru
    return explanation_en or explanation_ru or ""


def _field_translation_status(
    value_en: str | None, value_ru: str | None, locale: str
) -> str:
    if locale == SOURCE_LOCALE and value_en:
        return "source"
    if locale == LocaleCode.ru and value_ru:
        return "translated"
    if value_en:
        return "fallback"
    return "missing"


def _caveat(locale: str) -> str:
    if locale == LocaleCode.ru:
        return CAVEAT_RU
    return CAVEAT


def _risks_for_country(country: DecisionCountryScore) -> list[str]:
    weak = [item.criterion for item in country.breakdowns if item.score < 50]
    if not weak:
        return [
            "No low-scoring criteria in the MVP breakdown; expert review is still required."
        ]
    return [f"Low or uncertain criterion: {criterion}" for criterion in weak[:4]]

from app.repositories import decision_engine as repository
from app.schemas.common import LocaleResolution, Pagination, locale_resolution
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


def _locale(rows: list[dict[str, Any]], requested_locale: str) -> LocaleResolution:
    if requested_locale == "en":
        return locale_resolution("en", False)
    return locale_resolution(
        requested_locale, bool(rows) and all(row.get("is_translated") for row in rows)
    )


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
    return _attach_breakdowns_and_sources(connection, rows)


def get_country_sources(
    connection: Connection[Any], country_slug: str, locale: str, limit: int, offset: int
) -> SourceListWithLocaleResponse:
    rows = repository.list_country_sources(connection, country_slug, limit, offset)
    total = repository.count_country_sources(connection, country_slug)
    return SourceListWithLocaleResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=locale_resolution(locale, locale == "en"),
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
    scenario_row = get_scenario(connection, payload.scenario_slug, payload.locale)
    rows = repository.list_scenario_countries(
        connection, payload.scenario_slug, payload.locale
    )
    rows = [row for row in rows if row["country_slug"] in payload.country_slugs]
    countries = _attach_breakdowns_and_sources(connection, rows)
    if len(countries) != len(set(payload.country_slugs)):
        raise LookupError("One or more country scores were not found")
    recommendation_type, recommended_country, confidence = _recommend(countries)
    explanation = _compare_explanation(
        countries, recommended_country, recommendation_type
    )
    return DecisionCompareResult(
        scenario=_scenario_model(scenario_row),
        countries=countries,
        recommended_country=recommended_country,
        recommendation_type=recommendation_type,
        confidence=confidence,
        explanation=explanation,
        caveat=CAVEAT,
        locale=_locale([scenario_row], payload.locale),
    )


def run_decision(
    connection: Connection[Any], payload: DecisionRunInput
) -> DecisionRunResult:
    scenario_row = get_scenario(connection, payload.scenario_slug, payload.locale)
    rows = repository.list_scenario_countries(
        connection, payload.scenario_slug, payload.locale
    )
    rows = [
        row for row in rows if row["country_slug"] in payload.candidate_country_slugs
    ]
    countries = _attach_breakdowns_and_sources(connection, rows)
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
                connection, payload.locale, country.country_slug, 3, 0
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
            countries, recommended_country, recommendation_type
        ),
        caveat=CAVEAT,
        locale=_locale([scenario_row], payload.locale),
    )


def _attach_breakdowns_and_sources(
    connection: Connection[Any], rows: list[dict[str, Any]]
) -> list[DecisionCountryScore]:
    score_ids = [str(row["id"]) for row in rows]
    breakdown_rows = repository.list_score_breakdowns(connection, score_ids)
    source_rows = repository.list_score_sources(
        connection, sorted({row["country_slug"] for row in rows})
    )
    breakdowns_by_score: dict[str, list[dict[str, Any]]] = {}
    for breakdown in breakdown_rows:
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
) -> str:
    ordered = sorted(countries, key=lambda item: item.score, reverse=True)
    if recommendation_type == "tie" or recommended_country is None:
        return "The top countries are close in score, so the recommendation is low-confidence."
    return (
        f"{recommended_country} has the highest stored MVP decision score "
        f"({ordered[0].score:.1f}) for this scenario. Review the breakdowns and sources before acting."
    )


def _risks_for_country(country: DecisionCountryScore) -> list[str]:
    weak = [item.criterion for item in country.breakdowns if item.score < 50]
    if not weak:
        return [
            "No low-scoring criteria in the MVP breakdown; expert review is still required."
        ]
    return [f"Low or uncertain criterion: {criterion}" for criterion in weak[:4]]

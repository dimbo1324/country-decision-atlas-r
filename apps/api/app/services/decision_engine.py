from app.core.errors import api_error
from app.core.locales import SOURCE_LOCALE, validate_locale
from app.repositories import decision_engine as repository
from app.repositories.common import build_locale
from app.schemas.common import (
    LocaleCode,
    LocaleResolution,
    Pagination,
    SortMeta,
    source_locale_resolution,
)
from app.schemas.decision_engine import (
    CountryCardResponse,
    DecisionBreakdownItem,
    DecisionCompareInput,
    DecisionCompareResult,
    DecisionCountryRef,
    DecisionCountryResult,
    DecisionCountryScore,
    DecisionPoint,
    DecisionRunInput,
    DecisionRunMeta,
    DecisionRunRequest,
    DecisionRunResponse,
    DecisionScenario,
    DecisionScenarioRef,
    DecisionSourceRef,
    EvidenceListResponse,
    LegalSignalDetailResponse,
    SourceListWithLocaleResponse,
    UserStoryCreate,
    UserStoryListResponse,
    UserStoryResponse,
)
from app.schemas.sources import EvidenceItemListResponse
from app.services.decision_labels import (
    criterion_label,
    score_label_text,
    strength_message,
    weakness_message,
)
from app.services.decision_warnings import build_risk_warnings
from app.services.localization import overlay_localized_fields
from collections.abc import Iterable
from datetime import UTC, datetime
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
    rows = repository.list_scenario_countries(connection, scenario_slug)
    rows = overlay_localized_fields(
        connection,
        rows,
        "scenario",
        "scenario_id",
        [("title", "scenario_name", "title_ru", "title_en")],
        locale,
    )
    rows = overlay_localized_fields(
        connection,
        rows,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    return _attach_breakdowns_and_sources(connection, rows, locale)


def get_country_sources(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    limit: int,
    offset: int,
    source_type: str | None = None,
    language: str | None = None,
    confidence: str | None = None,
    status: str = "published",
    sort: str = "title",
    order: str = "asc",
) -> SourceListWithLocaleResponse:
    rows = repository.list_country_sources(
        connection,
        country_slug,
        limit,
        offset,
        source_type,
        language,
        confidence,
        status,
        sort,
        order,
    )
    total = repository.count_country_sources(
        connection, country_slug, source_type, language, confidence, status
    )
    return SourceListWithLocaleResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
        locale=source_locale_resolution(locale),
    )


def list_legal_signals(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    limit: int,
    offset: int,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
    sort: str = "published_date",
    order: str = "desc",
) -> tuple[list[dict[str, Any]], Pagination, LocaleResolution, SortMeta]:
    rows = repository.list_legal_signals(
        connection=connection,
        country_slug=country_slug,
        signal_type=signal_type,
        impact_direction=impact_direction,
        impact_level=impact_level,
        status=status,
        limit=limit,
        offset=offset,
        sort=sort,
        order=order,
    )
    rows = overlay_localized_fields(
        connection,
        rows,
        "legal_signal",
        "id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    total = repository.count_legal_signals(
        connection,
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        status,
    )
    return (
        rows,
        Pagination(limit=limit, offset=offset, total=total),
        _locale(rows, locale),
        SortMeta(sort=sort, order=order),
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
    connection: Connection[Any],
    limit: int,
    offset: int,
    origin_country_slug: str | None = None,
    destination_country_slug: str | None = None,
    scenario: str | None = None,
    verification_status: str | None = None,
    is_synthetic: bool | None = None,
    status: str = "published",
    sort: str = "created_at",
    order: str = "desc",
) -> UserStoryListResponse:
    rows = repository.list_user_stories(
        connection,
        limit,
        offset,
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
        sort,
        order,
    )
    total = repository.count_user_stories(
        connection,
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
    )
    return UserStoryListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
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
    rows = repository.list_scenario_countries(connection, payload.scenario_slug)
    rows = [row for row in rows if row["country_slug"] in payload.country_slugs]
    rows = overlay_localized_fields(
        connection,
        rows,
        "scenario",
        "scenario_id",
        [("title", "scenario_name", "title_ru", "title_en")],
        locale,
    )
    rows = overlay_localized_fields(
        connection,
        rows,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
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
    connection: Connection[Any], payload: DecisionRunRequest | DecisionRunInput
) -> DecisionRunResponse:
    locale = validate_locale(str(payload.locale))
    scenario_row = repository.get_decision_scenario(
        connection, payload.scenario_slug, locale
    )
    if scenario_row is None:
        raise api_error(
            404,
            "scenario_not_found",
            "Scenario was not found.",
            {"scenario_slug": payload.scenario_slug},
        )
    candidate_slugs = list(payload.candidate_country_slugs)
    if len(candidate_slugs) != len(set(candidate_slugs)):
        raise api_error(
            422,
            "invalid_candidate_countries",
            "Candidate countries must be unique.",
            {"candidate_country_slugs": candidate_slugs},
        )
    country_slugs = sorted({payload.origin_country_slug, *candidate_slugs})
    country_rows = repository.list_decision_countries(connection, country_slugs, locale)
    countries_by_slug = {row["slug"]: row for row in country_rows}
    missing_slugs = [slug for slug in country_slugs if slug not in countries_by_slug]
    if missing_slugs:
        details_key = (
            "country_slug"
            if missing_slugs == [payload.origin_country_slug]
            else "missing_country_slugs"
        )
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {
                details_key: missing_slugs[0]
                if len(missing_slugs) == 1
                else missing_slugs
            },
        )
    score_rows = repository.list_decision_scores(
        connection, payload.scenario_slug, candidate_slugs
    )
    score_rows = overlay_localized_fields(
        connection,
        score_rows,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    scores_by_country = {row["country_slug"]: row for row in score_rows}
    missing_score_slugs = [
        slug for slug in candidate_slugs if slug not in scores_by_country
    ]
    if missing_score_slugs:
        raise api_error(
            422,
            "decision_score_not_found",
            "Decision score was not found for one or more candidate countries.",
            {
                "scenario_slug": payload.scenario_slug,
                "missing_country_slugs": missing_score_slugs,
            },
        )
    score_ids = [row["id"] for row in score_rows]
    breakdown_rows = repository.list_decision_score_breakdowns(connection, score_ids)
    breakdown_rows = overlay_localized_fields(
        connection,
        breakdown_rows,
        "country_score_breakdown",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    legal_signal_rows = repository.list_decision_legal_signals(
        connection, candidate_slugs
    )
    legal_signal_rows = overlay_localized_fields(
        connection,
        legal_signal_rows,
        "legal_signal",
        "id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    source_ids = _collect_source_ids(breakdown_rows, legal_signal_rows)
    source_rows = repository.list_decision_sources_by_ids(connection, source_ids)
    breakdowns_by_score = _group_by(breakdown_rows, "country_score_id")
    signals_by_country = _group_by(legal_signal_rows, "country_slug")
    sources_by_id = {row["id"]: row for row in source_rows}
    results = [
        _build_country_result(
            country=countries_by_slug[slug],
            score=scores_by_country[slug],
            breakdowns=breakdowns_by_score.get(scores_by_country[slug]["id"], []),
            legal_signals=signals_by_country.get(slug, []),
            sources_by_id=sources_by_id,
            scenario_slug=payload.scenario_slug,
            scenario_title=scenario_row["title"],
            locale=locale,
        )
        for slug in candidate_slugs
    ]
    ranked_results = _rank_results(results)
    locale_rows = [
        scenario_row,
        countries_by_slug[payload.origin_country_slug],
        *[countries_by_slug[slug] for slug in candidate_slugs],
        *score_rows,
        *breakdown_rows,
        *legal_signal_rows,
    ]
    return DecisionRunResponse(
        scenario=DecisionScenarioRef(
            slug=scenario_row["slug"],
            title=scenario_row["title"],
            description=scenario_row["description"],
        ),
        origin_country=_country_ref(countries_by_slug[payload.origin_country_slug]),
        results=ranked_results,
        meta=DecisionRunMeta(
            candidate_count=len(candidate_slugs),
            generated_at=datetime.now(UTC),
        ),
        locale=_locale(locale_rows, locale),
    )


def get_score_label(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 75:
        return "strong"
    if score >= 60:
        return "moderate"
    if score >= 40:
        return "limited"
    return "weak"


def aggregate_confidence(values: Iterable[str | None]) -> str:
    confidence_value = {"low": 1, "medium": 2, "high": 3}
    clean_values = [
        confidence_value[value] for value in values if value in confidence_value
    ]
    if not clean_values:
        return "low"
    average = sum(clean_values) / len(clean_values)
    if average >= 2.5:
        return "high"
    if average >= 1.7:
        return "medium"
    return "low"


def _build_country_result(
    country: dict[str, Any],
    score: dict[str, Any],
    breakdowns: list[dict[str, Any]],
    legal_signals: list[dict[str, Any]],
    sources_by_id: dict[str, dict[str, Any]],
    scenario_slug: str,
    scenario_title: str,
    locale: str,
) -> DecisionCountryResult:
    used_source_ids = _collect_source_ids(breakdowns, legal_signals)
    result_sources = [
        DecisionSourceRef(**sources_by_id[source_id])
        for source_id in used_source_ids
        if source_id in sources_by_id
    ]
    score_label = get_score_label(float(score["score"]))
    return DecisionCountryResult(
        rank=0,
        country=_country_ref(country),
        score=score["score"],
        score_label=score_label,
        summary=_build_summary(
            country["name"], score["score"], score_label, scenario_title, locale
        ),
        strengths=_build_strengths(breakdowns, locale),
        weaknesses=_build_weaknesses(breakdowns, locale),
        risk_warnings=build_risk_warnings(scenario_slug, legal_signals, locale),
        confidence=aggregate_confidence(
            [
                score.get("confidence"),
                *[item.get("confidence") for item in breakdowns],
                *[item.get("confidence") for item in legal_signals],
                *[item.confidence for item in result_sources],
            ]
        ),
        breakdown=[
            DecisionBreakdownItem(
                criterion=item["criterion"],
                title=criterion_label(item["criterion"], locale),
                score=item["score"],
                weight=item["weight"],
                weighted_score=item["weighted_score"],
                explanation=item.get("explanation"),
                confidence=item.get("confidence"),
                source_ids=_source_ids(item.get("source_ids")),
            )
            for item in breakdowns
        ],
        sources=result_sources,
    )


def _country_ref(country: dict[str, Any]) -> DecisionCountryRef:
    return DecisionCountryRef(
        id=str(country["id"]),
        slug=country["slug"],
        name=country["name"],
        iso_code=country.get("iso_code"),
    )


def _build_strengths(
    breakdowns: list[dict[str, Any]], locale: str
) -> list[DecisionPoint]:
    return [
        DecisionPoint(
            code=item["criterion"],
            title=criterion_label(item["criterion"], locale),
            message=strength_message(item["criterion"], locale),
            source_ids=_source_ids(item.get("source_ids")),
        )
        for item in breakdowns
        if float(item["score"]) >= 70
    ]


def _build_weaknesses(
    breakdowns: list[dict[str, Any]], locale: str
) -> list[DecisionPoint]:
    return [
        DecisionPoint(
            code=item["criterion"],
            title=criterion_label(item["criterion"], locale),
            message=weakness_message(item["criterion"], locale),
            source_ids=_source_ids(item.get("source_ids")),
        )
        for item in breakdowns
        if float(item["score"]) <= 50
    ]


def _build_summary(
    country_name: str,
    score: float,
    label: str,
    scenario_title: str,
    locale: str,
) -> str:
    display_label = score_label_text(label, locale)
    if locale == LocaleCode.ru:
        return (
            f"{country_name} \u043f\u043e\u043b\u0443\u0447\u0430\u0435\u0442 \u043e\u0446\u0435\u043d\u043a\u0443 {score:.0f}/100 \u043f\u043e \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044e "
            f"\u00ab{scenario_title}\u00bb. \u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043e\u0446\u0435\u043d\u0438\u0432\u0430\u0435\u0442\u0441\u044f \u043a\u0430\u043a {display_label}. "
            "\u0412\u044b\u0432\u043e\u0434 \u043e\u0441\u043d\u043e\u0432\u0430\u043d \u043d\u0430 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0445 score breakdowns, legal signals \u0438 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0430\u0445."
        )
    return (
        f"{country_name} receives a {score:.0f}/100 score for the "
        f'"{scenario_title}" scenario. The result is assessed as {display_label}. '
        "The conclusion is based on stored score breakdowns, legal signals, and sources."
    )


def _rank_results(
    results: list[DecisionCountryResult],
) -> list[DecisionCountryResult]:
    confidence_rank = {"high": 3, "medium": 2, "low": 1}
    ranked = sorted(
        results,
        key=lambda item: (
            -item.score,
            -confidence_rank.get(item.confidence, 0),
            item.country.slug,
        ),
    )
    for index, result in enumerate(ranked, start=1):
        result.rank = index
    return ranked


def _collect_source_ids(
    breakdowns: list[dict[str, Any]], legal_signals: list[dict[str, Any]]
) -> list[str]:
    source_ids = [
        source_id
        for breakdown in breakdowns
        for source_id in _source_ids(breakdown.get("source_ids"))
    ]
    source_ids.extend(
        str(signal["source_id"]) for signal in legal_signals if signal.get("source_id")
    )
    return sorted(set(source_ids))


def _source_ids(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return []


def _group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


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

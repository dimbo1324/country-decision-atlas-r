from app.core.errors import api_error
from app.core.locales import validate_locale
from app.repositories import (
    decision_engine as repository,
    feature_flags as ff_repo,
)
from app.schemas.common import LocaleCode
from app.schemas.country_pairs import CountryPairCompatibilitySummary
from app.schemas.decision_engine import (
    DecisionBreakdownItem,
    DecisionCompareInput,
    DecisionCompareResult,
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
)
from app.schemas.decision_personalization import (
    DecisionPersonalizationResponse,
    DecisionWeightItem,
)
from app.services import decision_analytics, decision_origin_context
from app.services.decision_engine import helpers
from app.services.decision_engine.retrieval import get_scenario
from app.services.decision_labels import (
    criterion_label,
    score_label_text,
    strength_message,
    weakness_message,
)
from app.services.decision_personalization import (
    apply_effective_weights_to_breakdown,
    build_personalization_summary,
    normalize_custom_weights,
    resolve_weight_mode,
)
from app.services.decision_warnings import build_risk_warnings
from app.services.feature_flags import can_access, default_access_context
from app.services.methodology_config import (
    MethodologyConfig,
    RecommendationThresholds,
    get_active_methodology_config,
)
from app.services.persona_runtime import aggregate_persona_cii_score
from app.services.weight_profiles import resolve_profile_for_decision
from datetime import UTC, datetime
from decimal import Decimal
from psycopg import Connection
from typing import Any


DECISION_PERSONALIZATION_FEATURE_KEY = "decision_personalization_enabled"


def _is_decision_personalization_enabled(connection: Connection[Any]) -> bool:
    feature = ff_repo.get_feature_flag(
        connection, DECISION_PERSONALIZATION_FEATURE_KEY
    )
    rules = ff_repo.list_feature_access_rules(
        connection, DECISION_PERSONALIZATION_FEATURE_KEY
    )
    from app.core.config import get_settings

    ctx = default_access_context(get_settings())
    decision = can_access(
        ctx, feature, rules, DECISION_PERSONALIZATION_FEATURE_KEY
    )
    return decision.is_enabled


def compare_countries(
    connection: Connection[Any], payload: DecisionCompareInput
) -> DecisionCompareResult:
    locale = validate_locale(str(payload.locale))
    methodology = get_active_methodology_config(connection)
    scenario_row = get_scenario(connection, payload.scenario_slug, locale)
    rows = repository.list_scenario_countries(connection, payload.scenario_slug)
    rows = [row for row in rows if row["country_slug"] in payload.country_slugs]
    rows = helpers.overlay_localized_fields(
        connection,
        rows,
        "scenario",
        "scenario_id",
        [("title", "scenario_name", "title_ru", "title_en")],
        locale,
    )
    rows = helpers.overlay_localized_fields(
        connection,
        rows,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    countries = helpers._attach_breakdowns_and_sources(connection, rows, locale)
    if len(countries) != len(set(payload.country_slugs)):
        raise LookupError("One or more country scores were not found")
    recommendation_type, recommended_country, confidence = _recommend(
        countries, methodology.decision.recommendation
    )
    explanation = _compare_explanation(
        countries, recommended_country, recommendation_type, locale
    )
    return DecisionCompareResult(
        scenario=_scenario_model(scenario_row),
        countries=countries,
        recommended_country=recommended_country,
        recommendation_type=recommendation_type,
        confidence=confidence,
        methodology_version=methodology.version,
        explanation=explanation,
        caveat=helpers._caveat(locale),
        locale=helpers._locale([scenario_row], locale),
    )


def run_decision(
    connection: Connection[Any],
    payload: DecisionRunRequest | DecisionRunInput,
    session_id: str | None = None,
    current_user_id: str | None = None,
) -> DecisionRunResponse:
    locale = validate_locale(str(payload.locale))
    methodology = get_active_methodology_config(connection)
    if (
        payload.weight_profile_id is not None
        and payload.custom_weights is not None
    ):
        raise api_error(
            422,
            "weight_profile_custom_weights_conflict",
            "Use either weight_profile_id or custom_weights, not both.",
            {},
        )
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
    origin_slug = payload.origin_country_slug
    country_slugs = sorted(
        {*candidate_slugs, *([origin_slug] if origin_slug else [])}
    )
    country_rows = repository.list_decision_countries(
        connection, country_slugs, locale
    )
    countries_by_slug = {row["slug"]: row for row in country_rows}
    missing_slugs = [
        slug for slug in country_slugs if slug not in countries_by_slug
    ]
    if missing_slugs:
        details_key = (
            "country_slug"
            if missing_slugs == [origin_slug]
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
    score_rows = helpers.overlay_localized_fields(
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
    breakdown_rows = repository.list_decision_score_breakdowns(
        connection, score_ids
    )
    breakdown_rows = helpers.overlay_localized_fields(
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
    legal_signal_rows = helpers.overlay_localized_fields(
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
    source_ids = helpers._collect_source_ids(breakdown_rows, legal_signal_rows)
    source_rows = repository.list_decision_sources_by_ids(
        connection, source_ids
    )
    base_weights_map: dict[str, Decimal] = {
        str(item["criterion"]): Decimal(str(item["weight"]))
        for item in breakdown_rows
    }
    allowed_criteria = sorted(base_weights_map)
    profile_weights: dict[str, Decimal] | None = None
    weight_profile_id: str | None = None
    weight_profile_name: str | None = None
    if payload.weight_profile_id is not None:
        if current_user_id is None:
            raise api_error(
                401,
                "auth_required",
                "Authentication is required.",
                {},
            )
        profile = resolve_profile_for_decision(
            connection,
            profile_id=payload.weight_profile_id,
            user_id=current_user_id,
            scenario_slug=payload.scenario_slug,
        )
        profile_weights = {
            criterion: Decimal(str(value))
            for criterion, value in profile["weights"].items()
        }
        weight_profile_id = profile["id"]
        weight_profile_name = profile["name"]
    requested_weights = (
        profile_weights
        if profile_weights is not None
        else payload.custom_weights
    )
    effective_weights: dict[str, Decimal] | None = None
    if requested_weights is not None:
        if not _is_decision_personalization_enabled(connection):
            raise api_error(
                422,
                "decision_personalization_disabled",
                "Decision personalization is currently disabled.",
            )
        effective_weights = normalize_custom_weights(
            requested_weights, allowed_criteria
        )
    if effective_weights is not None:
        breakdown_rows = apply_effective_weights_to_breakdown(
            breakdown_rows, effective_weights
        )
        decision_analytics.record_custom_weights_used(
            connection,
            session_id=session_id,
            scenario_slug=payload.scenario_slug,
            persona_slug=payload.persona,
            candidate_count=len(candidate_slugs),
            criteria_count=len(allowed_criteria),
            weight_mode=resolve_weight_mode(
                payload.persona, effective_weights, weight_profile_id
            ),
        )
    breakdowns_by_score = helpers._group_by(breakdown_rows, "country_score_id")
    signals_by_country = helpers._group_by(legal_signal_rows, "country_slug")
    sources_by_id = {row["id"]: row for row in source_rows}
    persona_profile: dict[str, Any] | None = None
    persona_adjusted_scores: dict[str, float] = {}
    if payload.persona:
        persona_profile, persona_adjusted_scores = (
            _build_persona_adjusted_scores(
                connection,
                candidate_slugs,
                payload.scenario_slug,
                payload.persona,
                locale,
            )
        )
    pair_contexts = (
        decision_origin_context.build_country_pair_contexts(
            connection, origin_slug, candidate_slugs
        )
        if origin_slug is not None
        else {}
    )
    results = [
        _build_country_result(
            country=countries_by_slug[slug],
            score=scores_by_country[slug],
            breakdowns=breakdowns_by_score.get(
                scores_by_country[slug]["id"], []
            ),
            legal_signals=signals_by_country.get(slug, []),
            sources_by_id=sources_by_id,
            scenario_slug=payload.scenario_slug,
            scenario_title=scenario_row["title"],
            locale=locale,
            override_score=(
                sum(
                    float(item["weighted_score"])
                    for item in breakdowns_by_score.get(
                        scores_by_country[slug]["id"], []
                    )
                )
                if effective_weights is not None
                else None
            ),
            country_pair_context=pair_contexts.get(slug),
            methodology=methodology,
        )
        for slug in candidate_slugs
    ]
    if persona_profile is not None:
        for result in results:
            adjusted_score = persona_adjusted_scores.get(result.country.slug)
            if adjusted_score is None:
                continue
            result.persona_adjusted_score = adjusted_score
            result.persona_adjusted_label = helpers._score_label_literal(
                adjusted_score, methodology.score_labels
            )
        ranked_results = _rank_persona_adjusted_results(results)
    else:
        ranked_results = _rank_results(results)
    locale_rows = [
        scenario_row,
        *([countries_by_slug[origin_slug]] if origin_slug is not None else []),
        *[countries_by_slug[slug] for slug in candidate_slugs],
        *score_rows,
        *breakdown_rows,
        *legal_signal_rows,
    ]
    personalization_summary = build_personalization_summary(
        persona_slug=payload.persona,
        custom_weights_applied=effective_weights is not None,
        base_weights=base_weights_map,
        effective_weights=effective_weights or base_weights_map,
        weight_profile_id=weight_profile_id,
        weight_profile_name=weight_profile_name,
    )
    personalization = DecisionPersonalizationResponse(
        weight_mode=personalization_summary["weight_mode"],
        persona_slug=personalization_summary["persona_slug"],
        weight_profile_id=personalization_summary["weight_profile_id"],
        weight_profile_name=personalization_summary["weight_profile_name"],
        custom_weights_applied=personalization_summary[
            "custom_weights_applied"
        ],
        base_weights=[
            DecisionWeightItem(**item)
            for item in personalization_summary["base_weights"]
        ],
        effective_weights=[
            DecisionWeightItem(**item)
            for item in personalization_summary["effective_weights"]
        ],
    )
    return DecisionRunResponse(
        scenario=DecisionScenarioRef(
            slug=scenario_row["slug"],
            title=scenario_row["title"],
            description=scenario_row["description"],
        ),
        origin_country=(
            helpers._country_ref(countries_by_slug[origin_slug])
            if origin_slug is not None
            else None
        ),
        origin_context_status=decision_origin_context.resolve_origin_context_status(
            origin_slug, candidate_slugs, pair_contexts
        ),
        results=ranked_results,
        meta=DecisionRunMeta(
            candidate_count=len(candidate_slugs),
            generated_at=datetime.now(UTC),
            methodology_version=methodology.version,
        ),
        methodology_version=methodology.version,
        locale=helpers._locale(locale_rows, locale),
        applied_persona=persona_profile["persona"] if persona_profile else None,
        persona_weight_profile=persona_profile,
        ranking_mode="persona_adjusted" if persona_profile else "base",
        personalization=personalization,
    )


def _build_country_result(
    country: dict[str, Any],
    score: dict[str, Any],
    breakdowns: list[dict[str, Any]],
    legal_signals: list[dict[str, Any]],
    sources_by_id: dict[str, dict[str, Any]],
    scenario_slug: str,
    scenario_title: str,
    locale: str,
    methodology: MethodologyConfig,
    override_score: float | None = None,
    country_pair_context: CountryPairCompatibilitySummary | None = None,
) -> DecisionCountryResult:
    used_source_ids = helpers._collect_source_ids(breakdowns, legal_signals)
    result_sources = [
        DecisionSourceRef(**sources_by_id[source_id])
        for source_id in used_source_ids
        if source_id in sources_by_id
    ]
    final_score = (
        override_score if override_score is not None else float(score["score"])
    )
    score_label = helpers.get_score_label(final_score, methodology.score_labels)
    return DecisionCountryResult(
        rank=0,
        country=helpers._country_ref(country),
        score=final_score,
        score_label=score_label,
        summary=_build_summary(
            country["name"], final_score, score_label, scenario_title, locale
        ),
        strengths=_build_strengths(
            breakdowns, locale, methodology.decision.strength_min_score
        ),
        weaknesses=_build_weaknesses(
            breakdowns, locale, methodology.decision.weakness_max_score
        ),
        risk_warnings=build_risk_warnings(scenario_slug, legal_signals, locale),
        confidence=helpers.aggregate_confidence(
            [
                score.get("confidence"),
                *[item.get("confidence") for item in breakdowns],
                *[item.get("confidence") for item in legal_signals],
                *[item.confidence for item in result_sources],
            ],
            methodology.decision.confidence,
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
                source_ids=helpers._source_ids(item.get("source_ids")),
            )
            for item in breakdowns
        ],
        sources=result_sources,
        country_pair_context=country_pair_context,
    )


def _build_strengths(
    breakdowns: list[dict[str, Any]], locale: str, min_score: float
) -> list[DecisionPoint]:
    return [
        DecisionPoint(
            code=item["criterion"],
            title=criterion_label(item["criterion"], locale),
            message=strength_message(item["criterion"], locale),
            source_ids=helpers._source_ids(item.get("source_ids")),
        )
        for item in breakdowns
        if float(item["score"]) >= min_score
    ]


def _build_weaknesses(
    breakdowns: list[dict[str, Any]], locale: str, max_score: float
) -> list[DecisionPoint]:
    return [
        DecisionPoint(
            code=item["criterion"],
            title=criterion_label(item["criterion"], locale),
            message=weakness_message(item["criterion"], locale),
            source_ids=helpers._source_ids(item.get("source_ids")),
        )
        for item in breakdowns
        if float(item["score"]) <= max_score
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
            f"{country_name} получает оценку {score:.0f}/100 по сценарию "
            f"«{scenario_title}». Результат оценивается как {display_label}. "
            "Вывод основан на сохранённых score breakdowns, legal signals и источниках."
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


def _rank_persona_adjusted_results(
    results: list[DecisionCountryResult],
) -> list[DecisionCountryResult]:
    confidence_rank = {"high": 3, "medium": 2, "low": 1}
    ranked = sorted(
        results,
        key=lambda item: (
            -(item.persona_adjusted_score or 0),
            -confidence_rank.get(item.confidence, 0),
            item.country.slug,
        ),
    )
    for index, result in enumerate(ranked, start=1):
        result.rank = index
        result.persona_adjusted_rank = index
    return ranked


def _build_persona_adjusted_scores(
    connection: Connection[Any],
    candidate_slugs: list[str],
    scenario_slug: str,
    persona_slug: str,
    locale: str,
) -> tuple[dict[str, Any], dict[str, float]]:
    profile = helpers.build_persona_weight_profile(
        connection, scenario_slug, persona_slug, locale
    )
    metric_defs = helpers.get_active_cii_metric_definitions(connection)
    metric_defs_by_slug = {str(item["slug"]): item for item in metric_defs}
    raw_values = helpers.get_cii_metric_values_for_countries(
        connection, candidate_slugs
    )
    values_by_country: dict[str, list[dict[str, Any]]] = {}
    for row in raw_values:
        values_by_country.setdefault(str(row["country_slug"]), []).append(row)
    scores: dict[str, float] = {}
    for slug in candidate_slugs:
        aggregate = aggregate_persona_cii_score(
            values_by_country.get(slug, []), profile, metric_defs_by_slug
        )
        scores[slug] = float(aggregate["overall_score"])
    return profile, scores


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
    thresholds: RecommendationThresholds,
) -> tuple[str, str | None, str]:
    if len(countries) < 2:
        return (
            "winner",
            countries[0].country_slug if countries else None,
            "medium",
        )
    ordered = sorted(countries, key=lambda item: item.score, reverse=True)
    delta = ordered[0].score - ordered[1].score
    if delta < thresholds.tie_delta_below:
        return "tie", None, "low"
    return (
        "winner",
        ordered[0].country_slug,
        "medium"
        if delta < thresholds.medium_confidence_delta_below
        else "high",
    )


def _compare_explanation(
    countries: list[DecisionCountryScore],
    recommended_country: str | None,
    recommendation_type: str,
    locale: str,
) -> str:
    ordered = sorted(countries, key=lambda item: item.score, reverse=True)
    if recommendation_type == "tie" or recommended_country is None:
        if locale == LocaleCode.ru:
            return "Страны-лидеры близки по баллам, поэтому рекомендация имеет низкую уверенность."
        return "The top countries are close in score, so the recommendation is low-confidence."
    if locale == LocaleCode.ru:
        return (
            f"{recommended_country} имеет самый высокий сохранённый MVP-балл "
            f"({ordered[0].score:.1f}) для этого сценария. Проверьте разбивку и источники перед решением."
        )
    return (
        f"{recommended_country} has the highest stored MVP decision score "
        f"({ordered[0].score:.1f}) for this scenario. Review the breakdowns and sources before acting."
    )

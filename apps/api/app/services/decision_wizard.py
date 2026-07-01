from app.core.config import get_settings
from app.core.errors import api_error
from app.repositories import (
    countries as countries_repository,
    decision_engine as decision_repository,
    feature_flags as ff_repo,
    personas as personas_repository,
)
from app.schemas.decision_wizard import (
    DecisionWizardAnswers,
    DecisionWizardRecommendation,
)
from app.services import decision_analytics
from app.services.decision_personalization import (
    DECISION_CRITERIA,
    normalize_custom_weights,
)
from app.services.feature_flags import can_access, default_access_context
from psycopg import Connection
from typing import Any, Literal


DECISION_WIZARD_FEATURE_KEY = "decision_wizard_enabled"

BASE_WEIGHT_TEMPLATE: dict[str, float] = {
    "legalization_score": 20.0,
    "long_term_status_score": 15.0,
    "cost_of_living_score": 15.0,
    "safety_score": 20.0,
    "business_score": 10.0,
    "legal_stability_score": 10.0,
    "source_quality_score": 10.0,
}

_SCENARIO_BY_GOAL: dict[str, str] = {
    "residence": "relocation_residence",
    "citizenship": "permanent_residence_citizenship",
    "low_budget": "low_budget_living",
    "business": "business_self_employment",
    "safety": "safety_political_risk",
    "remote_work": "relocation_residence",
    "study": "relocation_residence",
}

_SCENARIO_EXPLANATIONS: dict[str, str] = {
    "residence": "Residence goal selected, so relocation/residence scenario was chosen.",
    "citizenship": (
        "Citizenship goal selected, so permanent residence/citizenship "
        "scenario was chosen."
    ),
    "low_budget": "Low-budget goal selected, so low-budget living scenario was chosen.",
    "business": "Business goal selected, so business/self-employment scenario was chosen.",
    "safety": "Safety goal selected, so safety/political-risk scenario was chosen.",
    "remote_work": (
        "Remote work goal selected, so relocation/residence scenario was "
        "chosen as the closest match."
    ),
    "study": (
        "Study goal selected, so relocation/residence scenario was chosen "
        "as the closest match."
    ),
}

_PERSONA_EXPLANATIONS: dict[str, str] = {
    "family": "Family persona was selected because family with children was indicated.",
    "entrepreneur": (
        "Entrepreneur persona was selected because business priority is high "
        "or business is the primary goal."
    ),
    "digital_nomad": (
        "Digital nomad persona was selected because remote work is the primary goal."
    ),
    "student": "Student persona was selected because study is the primary goal.",
    "low_budget_migrant": (
        "Low-budget migrant persona was selected because low budget is the "
        "primary goal."
    ),
    "investor": (
        "Investor persona was selected because budget level is high and "
        "business is the primary goal."
    ),
    "skilled_worker": (
        "Skilled worker persona was selected because work priority is high."
    ),
}


def _is_decision_wizard_enabled(connection: Connection[Any]) -> bool:
    feature = ff_repo.get_feature_flag(connection, DECISION_WIZARD_FEATURE_KEY)
    rules = ff_repo.list_feature_access_rules(connection, DECISION_WIZARD_FEATURE_KEY)
    ctx = default_access_context(get_settings())
    decision = can_access(ctx, feature, rules, DECISION_WIZARD_FEATURE_KEY)
    return decision.is_enabled


def resolve_scenario_slug(answers: DecisionWizardAnswers) -> str:
    return _SCENARIO_BY_GOAL[answers.primary_goal]


def resolve_persona_slug(answers: DecisionWizardAnswers) -> str | None:
    if answers.family_status == "family_with_children":
        return "family"
    if answers.budget_level == "high" and answers.primary_goal == "business":
        return "investor"
    if answers.primary_goal == "business":
        return "entrepreneur"
    if answers.primary_goal == "remote_work":
        return "digital_nomad"
    if answers.primary_goal == "study":
        return "student"
    if answers.primary_goal == "low_budget":
        return "low_budget_migrant"
    if answers.work_priority == "high":
        return "skilled_worker"
    return None


def build_initial_custom_weights(answers: DecisionWizardAnswers) -> dict[str, float]:
    raw = dict(BASE_WEIGHT_TEMPLATE)
    if answers.safety_priority == "high":
        raw["safety_score"] += 10
    if answers.business_priority == "high":
        raw["business_score"] += 10
    if answers.citizenship_priority == "high":
        raw["long_term_status_score"] += 10
    if answers.budget_level == "low":
        raw["cost_of_living_score"] += 10
    if answers.timeframe == "fast":
        raw["legalization_score"] += 5
    normalized = normalize_custom_weights(raw, DECISION_CRITERIA)
    assert normalized is not None
    return {criterion: float(weight * 100) for criterion, weight in normalized.items()}


def build_wizard_explanation(
    answers: DecisionWizardAnswers,
    scenario_slug: str,
    persona_slug: str | None,
) -> list[str]:
    explanation = [_SCENARIO_EXPLANATIONS[answers.primary_goal]]
    if scenario_slug not in _SCENARIO_BY_GOAL.values():
        explanation.append(
            f"Scenario {scenario_slug} was resolved outside the standard mapping."
        )
    if persona_slug is not None and persona_slug in _PERSONA_EXPLANATIONS:
        explanation.append(_PERSONA_EXPLANATIONS[persona_slug])
    return explanation


def _resolve_confidence(
    answers: DecisionWizardAnswers, persona_slug: str | None
) -> Literal["low", "medium", "high"]:
    if persona_slug is None:
        return "low"
    if answers.family_status == "family_with_children":
        return "high"
    if answers.budget_level == "high" and answers.primary_goal == "business":
        return "high"
    return "medium"


def resolve_wizard_recommendation(
    connection: Connection[Any],
    answers: DecisionWizardAnswers,
    session_id: str | None = None,
) -> DecisionWizardRecommendation:
    if not _is_decision_wizard_enabled(connection):
        raise api_error(
            422,
            "decision_wizard_disabled",
            "Decision wizard is currently disabled.",
        )
    scenario_slug = resolve_scenario_slug(answers)
    scenario_row = decision_repository.get_decision_scenario(
        connection, scenario_slug, "en"
    )
    if scenario_row is None:
        raise api_error(
            404,
            "scenario_not_found",
            "Recommended scenario was not found.",
            {"scenario_slug": scenario_slug},
        )
    warnings: list[str] = []
    persona_candidate = resolve_persona_slug(answers)
    active_persona_slugs = set(
        personas_repository.list_active_persona_slugs(connection)
    )
    persona_slug = (
        persona_candidate if persona_candidate in active_persona_slugs else None
    )
    if persona_candidate is not None and persona_slug is None:
        warnings.append("recommended_persona_unavailable")
    initial_custom_weights = build_initial_custom_weights(answers)
    candidate_country_slugs = countries_repository.list_active_country_slugs(connection)
    explanation = build_wizard_explanation(answers, scenario_slug, persona_slug)
    confidence = _resolve_confidence(answers, persona_slug)
    decision_analytics.record_wizard_completed(
        connection,
        session_id=session_id,
        primary_goal=answers.primary_goal,
        recommended_scenario_slug=scenario_slug,
        recommended_persona_slug=persona_slug,
        confidence=confidence,
    )
    return DecisionWizardRecommendation(
        recommended_scenario_slug=scenario_slug,
        recommended_persona_slug=persona_slug,
        initial_custom_weights=initial_custom_weights,
        candidate_country_slugs=candidate_country_slugs,
        explanation=explanation,
        warnings=warnings,
        confidence=confidence,
    )

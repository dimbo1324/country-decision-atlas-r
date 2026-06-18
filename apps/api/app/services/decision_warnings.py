from app.schemas.decision_engine import DecisionRiskWarning
from typing import Any


SCENARIO_WARNINGS_EN = {
    "relocation_residence": [
        {
            "code": "residence_requirements_review",
            "level": "medium",
            "message": "Check current residence permit requirements before making a decision.",
        }
    ],
    "permanent_residence_citizenship": [
        {
            "code": "citizenship_timeline_uncertainty",
            "level": "medium",
            "message": "Permanent residence and citizenship timelines may depend on physical presence and administrative practice.",
        }
    ],
    "low_budget_living": [
        {
            "code": "city_level_cost_variation",
            "level": "medium",
            "message": "Cost of living should be checked at city and neighbourhood level.",
        }
    ],
    "business_self_employment": [
        {
            "code": "banking_tax_review_required",
            "level": "high",
            "message": "Banking, taxation and self-employment status require separate verification.",
        }
    ],
    "safety_political_risk": [
        {
            "code": "political_legal_risk_review",
            "level": "high",
            "message": "Political and legal risks may materially affect long-term country suitability.",
        }
    ],
}

SCENARIO_WARNINGS_RU = {
    "relocation_residence": [
        {
            "code": "residence_requirements_review",
            "level": "medium",
            "message": "\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0430\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0435 \u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u043a residence permit \u043f\u0435\u0440\u0435\u0434 \u043f\u0440\u0438\u043d\u044f\u0442\u0438\u0435\u043c \u0440\u0435\u0448\u0435\u043d\u0438\u044f.",
        }
    ],
    "permanent_residence_citizenship": [
        {
            "code": "citizenship_timeline_uncertainty",
            "level": "medium",
            "message": "\u0421\u0440\u043e\u043a\u0438 \u041f\u041c\u0416 \u0438 \u0433\u0440\u0430\u0436\u0434\u0430\u043d\u0441\u0442\u0432\u0430 \u043c\u043e\u0433\u0443\u0442 \u0437\u0430\u0432\u0438\u0441\u0435\u0442\u044c \u043e\u0442 \u0444\u0430\u043a\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u043f\u0440\u043e\u0436\u0438\u0432\u0430\u043d\u0438\u044f \u0438 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u0438\u0432\u043d\u043e\u0439 \u043f\u0440\u0430\u043a\u0442\u0438\u043a\u0438.",
        }
    ],
    "low_budget_living": [
        {
            "code": "city_level_cost_variation",
            "level": "medium",
            "message": "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0436\u0438\u0437\u043d\u0438 \u043d\u0443\u0436\u043d\u043e \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0442\u044c \u043d\u0430 \u0443\u0440\u043e\u0432\u043d\u0435 \u043a\u043e\u043d\u043a\u0440\u0435\u0442\u043d\u043e\u0433\u043e \u0433\u043e\u0440\u043e\u0434\u0430 \u0438 \u0440\u0430\u0439\u043e\u043d\u0430.",
        }
    ],
    "business_self_employment": [
        {
            "code": "banking_tax_review_required",
            "level": "high",
            "message": "\u0411\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0430\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u0430, \u043d\u0430\u043b\u043e\u0433\u0438 \u0438 \u0441\u0442\u0430\u0442\u0443\u0441 \u0441\u0430\u043c\u043e\u0437\u0430\u043d\u044f\u0442\u043e\u0441\u0442\u0438 \u0442\u0440\u0435\u0431\u0443\u044e\u0442 \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e\u0439 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438.",
        }
    ],
    "safety_political_risk": [
        {
            "code": "political_legal_risk_review",
            "level": "high",
            "message": "\u041f\u043e\u043b\u0438\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0438 \u043f\u0440\u0430\u0432\u043e\u0432\u044b\u0435 \u0440\u0438\u0441\u043a\u0438 \u043c\u043e\u0433\u0443\u0442 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0435\u043d\u043d\u043e \u0432\u043b\u0438\u044f\u0442\u044c \u043d\u0430 \u0434\u043e\u043b\u0433\u043e\u0441\u0440\u043e\u0447\u043d\u0443\u044e \u043f\u0440\u0438\u0433\u043e\u0434\u043d\u043e\u0441\u0442\u044c \u0441\u0442\u0440\u0430\u043d\u044b.",
        }
    ],
}

SCENARIO_RELEVANT_SIGNAL_TYPES = {
    "relocation_residence": {"migration", "residence", "banking", "tax"},
    "permanent_residence_citizenship": {
        "residence",
        "citizenship",
        "rule_of_law",
    },
    "low_budget_living": {"cost_of_living", "healthcare", "safety"},
    "business_self_employment": {"business", "tax", "banking", "property"},
    "safety_political_risk": {
        "safety",
        "freedom",
        "rule_of_law",
        "political_risk",
    },
}


def build_risk_warnings(
    scenario_slug: str, legal_signals: list[dict[str, Any]], locale: str
) -> list[DecisionRiskWarning]:
    warnings = [
        DecisionRiskWarning(**warning)
        for warning in (
            SCENARIO_WARNINGS_RU if locale == "ru" else SCENARIO_WARNINGS_EN
        ).get(scenario_slug, [])
    ]
    relevant_types = SCENARIO_RELEVANT_SIGNAL_TYPES.get(scenario_slug, set())
    for signal in legal_signals:
        signal_type = str(signal.get("signal_type") or "")
        impact_direction = str(signal.get("impact_direction") or "")
        impact_level = str(signal.get("impact_level") or "")
        is_relevant = signal_type in relevant_types
        is_warning = impact_direction in {"negative", "mixed", "uncertain"} or (
            impact_level in {"high", "critical"}
        )
        if is_relevant and is_warning:
            source_id = signal.get("source_id")
            warnings.append(
                DecisionRiskWarning(
                    code=f"{signal_type}_legal_signal_review",
                    level="high" if impact_level == "critical" else impact_level,
                    message=str(signal.get("summary") or signal.get("title") or ""),
                    legal_signal_ids=[str(signal["id"])],
                    source_ids=[str(source_id)] if source_id else [],
                )
            )
    return warnings

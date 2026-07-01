from pydantic import BaseModel
from typing import Literal


class DecisionWizardAnswers(BaseModel):
    primary_goal: Literal[
        "residence",
        "citizenship",
        "low_budget",
        "business",
        "safety",
        "remote_work",
        "study",
    ]
    origin_country_slug: str | None = None
    budget_level: Literal["low", "medium", "high", "unknown"] = "unknown"
    family_status: Literal["solo", "couple", "family_with_children", "unknown"] = (
        "unknown"
    )
    work_priority: Literal["low", "medium", "high"] = "medium"
    safety_priority: Literal["low", "medium", "high"] = "medium"
    citizenship_priority: Literal["low", "medium", "high"] = "medium"
    business_priority: Literal["low", "medium", "high"] = "medium"
    timeframe: Literal["fast", "medium", "long", "unknown"] = "unknown"


class DecisionWizardRecommendation(BaseModel):
    recommended_scenario_slug: str
    recommended_persona_slug: str | None
    initial_custom_weights: dict[str, float]
    candidate_country_slugs: list[str]
    explanation: list[str]
    warnings: list[str]
    confidence: Literal["low", "medium", "high"]

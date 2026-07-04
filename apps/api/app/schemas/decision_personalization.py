from pydantic import BaseModel, Field
from typing import Literal


class DecisionWeightItem(BaseModel):
    criterion: str
    weight: float


class DecisionPersonalizationResponse(BaseModel):
    weight_mode: Literal[
        "base",
        "persona",
        "custom",
        "persona_custom",
        "profile",
        "persona_profile",
    ]
    persona_slug: str | None = None
    weight_profile_id: str | None = None
    weight_profile_name: str | None = None
    custom_weights_applied: bool
    base_weights: list[DecisionWeightItem] = Field(default_factory=list)
    effective_weights: list[DecisionWeightItem] = Field(default_factory=list)

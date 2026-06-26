from app.schemas.common import LocaleResolution
from pydantic import BaseModel, Field


class Persona(BaseModel):
    slug: str
    name: str
    description: str | None = None
    is_active: bool = True
    display_order: int


class PersonaListResponse(BaseModel):
    items: list[Persona] = Field(default_factory=list)
    locale: LocaleResolution


class PersonaMetricModifier(BaseModel):
    metric_slug: str
    metric_name: str
    modifier: float
    version: str = "v1.0"


class PersonaAdjustedMetricWeight(BaseModel):
    metric_id: str
    metric_slug: str
    metric_name: str
    base_weight: float
    modifier: float
    adjusted_weight: float


class PersonaWeightProfile(BaseModel):
    persona: Persona
    scenario_slug: str
    version: str
    weights: list[PersonaAdjustedMetricWeight] = Field(default_factory=list)
    weight_sum: float


class PersonaWeightProfileResponse(BaseModel):
    item: PersonaWeightProfile

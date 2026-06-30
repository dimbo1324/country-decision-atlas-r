from app.schemas.common import LocaleResolution, Pagination
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ScenarioCriterion(BaseModel):
    id: UUID
    scenario_id: UUID
    key: str
    label: str
    weight: float
    is_required: bool
    created_at: datetime
    updated_at: datetime


class Scenario(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    criteria: list[ScenarioCriterion] = Field(default_factory=list)


class ScenarioListResponse(BaseModel):
    items: list[Scenario]
    pagination: Pagination
    locale: LocaleResolution

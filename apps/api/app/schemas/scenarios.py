from datetime import datetime
from uuid import UUID
from app.schemas.common import LocaleResolution, Pagination
from pydantic import BaseModel
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
    criteria: list[ScenarioCriterion] = []
class ScenarioListResponse(BaseModel):
    items: list[Scenario]
    pagination: Pagination
    locale: LocaleResolution

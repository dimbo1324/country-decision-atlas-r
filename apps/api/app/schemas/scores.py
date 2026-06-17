from datetime import datetime
from uuid import UUID

from app.schemas.common import LocaleResolution, Pagination
from pydantic import BaseModel


class CountryScore(BaseModel):
    id: UUID
    country_id: UUID
    scenario_id: UUID
    scenario_slug: str
    scenario_name: str
    score: float
    score_label: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


class CountryScoreListResponse(BaseModel):
    items: list[CountryScore]
    pagination: Pagination
    locale: LocaleResolution

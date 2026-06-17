from app.schemas.common import LocaleResolution, Pagination, TranslationStatus
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class CountryScore(BaseModel):
    id: UUID
    country_id: UUID
    scenario_id: UUID
    scenario_slug: str
    scenario_name: str
    score: float
    score_label: str
    summary: str | None = None
    translation_status: TranslationStatus
    created_at: datetime
    updated_at: datetime


class CountryScoreListResponse(BaseModel):
    items: list[CountryScore]
    pagination: Pagination
    locale: LocaleResolution

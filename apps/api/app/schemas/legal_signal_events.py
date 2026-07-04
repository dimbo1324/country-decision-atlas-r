from app.schemas.common import LocaleResolution
from app.schemas.localization import LocalizationMeta
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


EventType = Literal[
    "created", "updated", "amended", "effective", "expired", "confirmed"
]
ImpactDirection = Literal[
    "positive", "negative", "neutral", "mixed", "uncertain"
]
ImpactLevel = Literal["low", "medium", "high", "critical"]


class TimelineSourceRef(BaseModel):
    id: UUID
    title: str
    url: str
    publisher: str | None = None
    source_type: str
    confidence: str | None = None


class TimelineEvidenceRef(BaseModel):
    id: UUID
    claim: str
    excerpt: str | None = None
    url: str | None = None
    confidence: str | None = None


class LegalSignalTimelineEvent(BaseModel):
    id: UUID
    country_slug: str
    country_name: str
    legal_signal_id: UUID
    legal_signal_title: str
    event_date: date
    event_year: int
    event_type: EventType
    signal_type: str
    impact_direction: ImpactDirection
    impact_level: ImpactLevel
    affected_groups: list[str] = Field(default_factory=list)
    title: str
    summary: str | None = None
    source: TimelineSourceRef | None = None
    evidence: TimelineEvidenceRef | None = None
    localization: LocalizationMeta | None = None
    quality_warnings: list[str] = Field(default_factory=list)


class TimelineYearGroup(BaseModel):
    year: int
    events: list[LegalSignalTimelineEvent]


class TimelineFilters(BaseModel):
    country_slug: str | None = None
    signal_type: str | None = None
    impact_direction: str | None = None
    impact_level: str | None = None
    affected_group: str | None = None
    year_from: int | None = None
    year_to: int | None = None


class LegalSignalTimelineResponse(BaseModel):
    locale: LocaleResolution
    filters: TimelineFilters
    groups: list[TimelineYearGroup]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    available_years: list[int] = Field(default_factory=list)

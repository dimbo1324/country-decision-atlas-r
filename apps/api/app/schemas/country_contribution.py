from app.schemas.common import LegalStatus
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Any
from uuid import UUID


class CountryProposalCreate(BaseModel):
    slug: str
    name_en: str
    name_ru: str
    iso2: str = Field(min_length=2, max_length=2)
    iso3: str = Field(min_length=3, max_length=3)
    justification: str = Field(min_length=20)


class CountryProposalPatch(BaseModel):
    justification: str = Field(min_length=20)


class CountryProposal(BaseModel):
    id: UUID
    proposer_user_id: UUID
    country_id: UUID
    slug: str
    name_en: str
    name_ru: str
    iso2: str
    iso3: str
    justification: str
    status: str
    curator_user_id: UUID | None = None
    readiness_snapshot: dict[str, Any] | None = None
    moderated_by: UUID | None = None
    moderated_at: datetime | None = None
    moderation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    country_is_active: bool
    country_is_demo: bool


class CountryProposalResponse(BaseModel):
    item: CountryProposal


class CountryProposalListResponse(BaseModel):
    items: list[CountryProposal]
    total: int


class ModerationReasonPayload(BaseModel):
    reason: str = Field(min_length=5)


class ContributorSourceCreate(BaseModel):
    title: str
    url: str | None = None
    source_type: str | None = None
    publisher: str | None = None
    language: str | None = "en"
    confidence: str | None = "medium"
    published_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None


class ContributorSourcePatch(BaseModel):
    title: str | None = None
    url: str | None = None
    source_type: str | None = None
    publisher: str | None = None
    language: str | None = None
    confidence: str | None = None
    published_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None


class ContributorEvidenceItemCreate(BaseModel):
    source_id: UUID | None = None
    legal_signal_id: UUID | None = None
    claim: str | None = None
    excerpt: str | None = None
    url: str | None = None
    confidence: str | None = "medium"


class ContributorEvidenceItemPatch(BaseModel):
    source_id: UUID | None = None
    legal_signal_id: UUID | None = None
    claim: str | None = None
    excerpt: str | None = None
    url: str | None = None
    confidence: str | None = None


class ContributorLegalSignalCreate(BaseModel):
    source_id: UUID | None = None
    title_en: str | None = None
    title_ru: str | None = None
    summary_en: str | None = None
    summary_ru: str | None = None
    signal_type: str | None = None
    impact_direction: str | None = None
    impact_level: str | None = None
    legal_status: LegalStatus = LegalStatus.unknown
    affected_groups: list[str] = Field(default_factory=list)
    published_date: date | None = None
    effective_date: date | None = None
    confidence: str | None = "medium"


class ContributorLegalSignalPatch(BaseModel):
    source_id: UUID | None = None
    title_en: str | None = None
    title_ru: str | None = None
    summary_en: str | None = None
    summary_ru: str | None = None
    signal_type: str | None = None
    impact_direction: str | None = None
    impact_level: str | None = None
    legal_status: LegalStatus | None = None
    affected_groups: list[str] | None = None
    published_date: date | None = None
    effective_date: date | None = None
    confidence: str | None = None


class ContributorTimelineEventCreate(BaseModel):
    legal_signal_id: UUID
    event_date: date
    event_type: str
    impact_direction: str
    impact_level: str
    title: str
    summary: str | None = None
    source_id: UUID | None = None
    evidence_item_id: UUID | None = None
    affected_groups: list[str] = Field(default_factory=list)


class CountryCardUpsert(BaseModel):
    executive_summary: str
    migration_overview: str
    tax_overview: str
    cost_of_living_overview: str
    business_overview: str
    safety_overview: str
    legal_signals_summary: str
    risk_summary: str
    source_summary: str


class CountryMetricValueEntry(BaseModel):
    metric_slug: str
    raw_value: float
    normalized_value: float = Field(ge=0, le=100)
    data_year: int | None = None
    source_name: str | None = None
    source_url: str | None = None
    reliability: str = "medium"


class CountryMetricValuesUpsert(BaseModel):
    values: list[CountryMetricValueEntry] = Field(min_length=1)


class ScenarioBreakdownEntry(BaseModel):
    criterion: str
    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)
    explanation_en: str
    explanation_ru: str
    source_ids: list[UUID] = Field(min_length=1)
    confidence: str = "medium"


class ScenarioScoresUpsert(BaseModel):
    scenario_slug: str
    breakdowns: list[ScenarioBreakdownEntry] = Field(min_length=7, max_length=7)


class GenericItemResponse(BaseModel):
    item: dict[str, Any]


class GenericListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int

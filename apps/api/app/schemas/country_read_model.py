from app.schemas.common import LocaleResolution
from app.schemas.localization import LocalizationMeta
from datetime import date, datetime
from pydantic import BaseModel, Field


class CountryReadModelCountry(BaseModel):
    id: str
    slug: str
    iso_code: str | None = None
    name: str
    region: str | None = None
    status: str
    localization: LocalizationMeta | None = None


class CountryReadModelProfile(BaseModel):
    executive_summary: str | None = None
    migration_overview: str | None = None
    tax_overview: str | None = None
    cost_of_living_overview: str | None = None
    business_overview: str | None = None
    safety_overview: str | None = None
    legal_signals_summary: str | None = None
    risk_summary: str | None = None
    source_summary: str | None = None
    localization: LocalizationMeta | None = None


class CountryReadModelScoreBreakdown(BaseModel):
    criterion: str
    score: float
    weight: float
    weighted_score: float
    explanation: str | None = None
    confidence: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    localization: LocalizationMeta | None = None


class CountryReadModelScore(BaseModel):
    id: str
    scenario_slug: str
    scenario_title: str
    score: float
    confidence: str | None = None
    explanation: str | None = None
    calculated_at: datetime | None = None
    breakdowns: list[CountryReadModelScoreBreakdown] = Field(default_factory=list)
    localization: LocalizationMeta | None = None


class CountryReadModelLegalSignal(BaseModel):
    id: str
    title: str
    summary: str | None = None
    signal_type: str
    impact_direction: str | None = None
    impact_level: str | None = None
    affected_groups: list[str] | None = None
    published_date: date | None = None
    effective_date: date | None = None
    confidence: str | None = None
    localization: LocalizationMeta | None = None


class CountryReadModelSource(BaseModel):
    id: str
    title: str
    url: str
    source_type: str | None = None
    publisher: str | None = None
    confidence: str | None = None
    published_at: date | None = None
    last_checked_at: date | None = None
    localization: LocalizationMeta | None = None


class CountryReadModelMeta(BaseModel):
    scores_count: int
    legal_signals_count: int
    sources_count: int
    last_updated_at: datetime | None = None


class CountryReadModelEvidenceSummary(BaseModel):
    total: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int


class CountryReadModelUserStoriesSummary(BaseModel):
    total: int
    synthetic: int
    average_satisfaction_score: float | None = None


class CountryReadModelResponse(BaseModel):
    country: CountryReadModelCountry
    profile: CountryReadModelProfile | None
    scores: list[CountryReadModelScore]
    legal_signals: list[CountryReadModelLegalSignal]
    sources: list[CountryReadModelSource]
    evidence_summary: CountryReadModelEvidenceSummary
    user_stories_summary: CountryReadModelUserStoriesSummary
    meta: CountryReadModelMeta
    locale: LocaleResolution

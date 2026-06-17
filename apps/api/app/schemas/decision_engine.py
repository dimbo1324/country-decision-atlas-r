from app.schemas.common import (
    LocaleCode,
    LocaleResolution,
    Pagination,
    TranslationStatus,
)
from app.schemas.sources import EvidenceItem, Source
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Any, Literal
from uuid import UUID


class CountryCard(BaseModel):
    id: UUID
    country_id: UUID
    locale: str
    executive_summary: str
    migration_overview: str
    tax_overview: str
    cost_of_living_overview: str
    business_overview: str
    safety_overview: str
    legal_signals_summary: str
    risk_summary: str
    source_summary: str
    status: str
    created_at: datetime
    updated_at: datetime


class CountryCardResponse(BaseModel):
    item: CountryCard
    locale: LocaleResolution


class CountryScoreBreakdown(BaseModel):
    id: UUID
    country_score_id: UUID
    criterion: str
    score: float
    weight: float
    weighted_score: float
    explanation: str
    explanation_en: str
    explanation_ru: str
    source_ids: list[str]
    confidence: Literal["high", "medium", "low"]
    translation_status: TranslationStatus = TranslationStatus.not_applicable
    created_at: datetime
    updated_at: datetime


class DecisionCountryScore(BaseModel):
    id: UUID
    country_id: UUID
    country_slug: str
    country_name: str
    scenario_id: UUID
    scenario_slug: str
    scenario_name: str
    score: float
    explanation: str
    confidence: Literal["high", "medium", "low"]
    calculated_at: datetime
    translation_status: TranslationStatus
    breakdowns: list[CountryScoreBreakdown]
    source_references: list[Source] = []


class DecisionScenario(BaseModel):
    id: UUID
    slug: str
    title: str
    description: str
    weights: dict[str, float]


class DecisionScenarioResponse(BaseModel):
    item: DecisionScenario
    locale: LocaleResolution


class DecisionCountryScoreListResponse(BaseModel):
    items: list[DecisionCountryScore]
    locale: LocaleResolution


class DecisionCompareInput(BaseModel):
    scenario_slug: str
    country_slugs: list[str] = Field(min_length=2)
    locale: LocaleCode = LocaleCode.en


class DecisionCompareResult(BaseModel):
    scenario: DecisionScenario
    countries: list[DecisionCountryScore]
    recommended_country: str | None
    recommendation_type: Literal["winner", "tie", "low_confidence"]
    confidence: Literal["high", "medium", "low"]
    explanation: str
    caveat: str
    locale: LocaleResolution


class DecisionRunInput(BaseModel):
    scenario_slug: str
    origin_country_slug: str | None = None
    candidate_country_slugs: list[str] = Field(min_length=1)
    locale: LocaleCode = LocaleCode.en


class DecisionRunCountry(BaseModel):
    country: DecisionCountryScore
    rank: int
    risks: list[str]
    key_legal_signals: list[dict[str, Any]]
    source_references: list[Source]


class DecisionRunResult(BaseModel):
    scenario: DecisionScenario
    origin_country_slug: str | None
    ranked_candidates: list[DecisionRunCountry]
    recommended_country: str | None
    confidence: Literal["high", "medium", "low"]
    explanation: str
    caveat: str
    locale: LocaleResolution


class UserStory(BaseModel):
    id: UUID
    origin_country_id: UUID | None = None
    destination_country_id: UUID
    city: str | None = None
    year: int | None = None
    scenario: str
    budget_initial_usd: Decimal | None = None
    budget_monthly_usd: Decimal | None = None
    legal_path: str | None = None
    documents_used: list[str]
    problems: str | None = None
    positive_outcome: str | None = None
    negative_outcome: str | None = None
    advice: str | None = None
    satisfaction_score: Decimal | None = None
    verification_status: str
    status: str
    is_synthetic: bool
    notes: str
    created_at: datetime
    updated_at: datetime


class UserStoryCreate(BaseModel):
    origin_country_slug: str | None = None
    destination_country_slug: str
    city: str | None = None
    year: int | None = Field(default=None, ge=1990, le=2100)
    scenario: str
    budget_initial_usd: Decimal | None = Field(default=None, ge=0)
    budget_monthly_usd: Decimal | None = Field(default=None, ge=0)
    legal_path: str | None = None
    documents_used: list[str] = []
    problems: str | None = None
    positive_outcome: str | None = None
    negative_outcome: str | None = None
    advice: str | None = None
    satisfaction_score: Decimal | None = Field(default=None, ge=0, le=10)
    is_synthetic: bool = True
    notes: str = "Synthetic example for MVP demonstration only."


class UserStoryListResponse(BaseModel):
    items: list[UserStory]
    pagination: Pagination


class UserStoryResponse(BaseModel):
    item: UserStory


class EvidenceListResponse(BaseModel):
    items: list[EvidenceItem]
    pagination: Pagination


class SourceListWithLocaleResponse(BaseModel):
    items: list[Source]
    pagination: Pagination
    locale: LocaleResolution


class LegalSignalDetail(BaseModel):
    id: UUID
    country_id: UUID
    title: str
    summary: str
    signal_type: str
    impact_direction: str
    impact_level: str
    affected_groups: list[str]
    published_date: date | None = None
    effective_date: date | None = None
    source_id: UUID | None = None
    confidence: str
    status: str
    created_at: datetime
    updated_at: datetime


class LegalSignalDetailResponse(BaseModel):
    item: LegalSignalDetail
    locale: LocaleResolution


class LegalSignalDetailListResponse(BaseModel):
    items: list[LegalSignalDetail]
    pagination: Pagination
    locale: LocaleResolution

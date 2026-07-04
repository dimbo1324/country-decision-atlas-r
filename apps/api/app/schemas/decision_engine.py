from app.core.locales import DEFAULT_LOCALE, SUPPORTED_LOCALES
from app.schemas.common import (
    LegalStatus,
    LocaleResolution,
    Pagination,
    PublicationStatus,
    SortMeta,
    TranslationStatus,
)
from app.schemas.country_pairs import CountryPairCompatibilitySummary
from app.schemas.decision_personalization import DecisionPersonalizationResponse
from app.schemas.localization import LocalizationMeta
from app.schemas.personas import Persona, PersonaWeightProfile
from app.schemas.sources import EvidenceItem, Source
from datetime import date, datetime
from decimal import Decimal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Annotated, Any, Literal
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
    translation_status: TranslationStatus = TranslationStatus.source
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
    source_references: list[Source] = Field(default_factory=list)


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
    locale: str = Field(
        default=DEFAULT_LOCALE,
        json_schema_extra={"enum": list(SUPPORTED_LOCALES)},
    )


class DecisionCompareResult(BaseModel):
    scenario: DecisionScenario
    countries: list[DecisionCountryScore]
    recommended_country: str | None
    recommendation_type: Literal["winner", "tie", "low_confidence"]
    confidence: Literal["high", "medium", "low"]
    methodology_version: str
    explanation: str
    caveat: str
    locale: LocaleResolution


class DecisionRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    origin_country_slug: str | None = Field(
        default=None,
        validation_alias=AliasChoices("origin_country_slug", "origin_country"),
    )
    candidate_country_slugs: list[str] = Field(
        min_length=1,
        max_length=10,
        validation_alias=AliasChoices(
            "candidate_country_slugs", "candidate_countries"
        ),
        json_schema_extra={"uniqueItems": True},
    )
    scenario_slug: str = Field(
        validation_alias=AliasChoices("scenario_slug", "scenario")
    )
    locale: str = Field(
        default=DEFAULT_LOCALE,
        json_schema_extra={"enum": list(SUPPORTED_LOCALES)},
    )
    persona: str | None = None
    custom_weights: dict[str, Decimal] | None = None
    weight_profile_id: str | None = None


DecisionRunInput = DecisionRunRequest


class DecisionCountryRef(BaseModel):
    id: str
    slug: str
    name: str
    iso_code: str | None = None


class DecisionScenarioRef(BaseModel):
    slug: str
    title: str
    description: str | None = None
    localization: LocalizationMeta | None = None


class DecisionPoint(BaseModel):
    code: str
    title: str
    message: str
    source_ids: list[str] = Field(default_factory=list)


class DecisionRiskWarning(BaseModel):
    code: str
    level: str
    message: str
    legal_signal_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class DecisionBreakdownItem(BaseModel):
    criterion: str
    title: str
    score: float
    weight: float
    weighted_score: float
    explanation: str | None = None
    confidence: Literal["high", "medium", "low"] | None = None
    source_ids: list[str] = Field(default_factory=list)
    localization: LocalizationMeta | None = None


class DecisionSourceRef(BaseModel):
    id: str
    title: str
    url: str
    source_type: str | None = None
    confidence: Literal["high", "medium", "low"] | None = None
    localization: LocalizationMeta | None = None


class DecisionCountryResult(BaseModel):
    rank: int
    country: DecisionCountryRef
    score: float
    score_label: Literal["weak", "limited", "moderate", "strong", "excellent"]
    persona_adjusted_score: float | None = None
    persona_adjusted_label: (
        Literal["weak", "limited", "moderate", "strong", "excellent"] | None
    ) = None
    persona_adjusted_rank: int | None = None
    summary: str
    strengths: list[DecisionPoint]
    weaknesses: list[DecisionPoint]
    risk_warnings: list[DecisionRiskWarning]
    confidence: Literal["high", "medium", "low"]
    breakdown: list[DecisionBreakdownItem]
    sources: list[DecisionSourceRef]
    localization: LocalizationMeta | None = None
    country_pair_context: CountryPairCompatibilitySummary | None = None


class DecisionRunMeta(BaseModel):
    candidate_count: int
    generated_at: datetime
    methodology_version: str
    model_version: str = "scenario-decision-engine-v1"


OriginContextStatus = Literal[
    "not_requested", "available", "partial", "not_available"
]


class DecisionRunResponse(BaseModel):
    scenario: DecisionScenarioRef
    origin_country: DecisionCountryRef | None
    origin_context_status: OriginContextStatus = "not_requested"
    results: list[DecisionCountryResult]
    meta: DecisionRunMeta
    methodology_version: str
    locale: LocaleResolution
    applied_persona: Persona | None = None
    persona_weight_profile: PersonaWeightProfile | None = None
    ranking_mode: Literal["base", "persona_adjusted"] = "base"
    personalization: DecisionPersonalizationResponse


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
    origin_country_slug: (
        Annotated[str, Field(min_length=1, max_length=100)] | None
    ) = None
    destination_country_slug: Annotated[
        str, Field(min_length=1, max_length=100)
    ]
    city: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    year: int | None = Field(default=None, ge=1990, le=2100)
    scenario: Annotated[str, Field(min_length=1, max_length=100)]
    budget_initial_usd: Decimal | None = Field(default=None, ge=0)
    budget_monthly_usd: Decimal | None = Field(default=None, ge=0)
    legal_path: Annotated[str, Field(max_length=4000)] | None = None
    documents_used: list[
        Annotated[str, Field(min_length=1, max_length=200)]
    ] = Field(default_factory=list, max_length=30)
    problems: Annotated[str, Field(max_length=4000)] | None = None
    positive_outcome: Annotated[str, Field(max_length=4000)] | None = None
    negative_outcome: Annotated[str, Field(max_length=4000)] | None = None
    advice: Annotated[str, Field(max_length=4000)] | None = None
    satisfaction_score: Decimal | None = Field(default=None, ge=0, le=10)
    is_synthetic: bool = True
    notes: Annotated[str, Field(min_length=1, max_length=4000)] = (
        "Synthetic example for MVP demonstration only."
    )


class UserStoryListResponse(BaseModel):
    items: list[UserStory]
    pagination: Pagination
    sort: SortMeta | None = None


class UserStoryResponse(BaseModel):
    item: UserStory


class EvidenceListResponse(BaseModel):
    items: list[EvidenceItem]
    pagination: Pagination
    sort: SortMeta | None = None


class SourceListWithLocaleResponse(BaseModel):
    items: list[Source]
    pagination: Pagination
    sort: SortMeta | None = None
    locale: LocaleResolution


class LegalSignalDetail(BaseModel):
    id: UUID
    country_id: UUID
    title: str
    summary: str
    signal_type: str
    impact_direction: str
    impact_level: str
    legal_status: LegalStatus = LegalStatus.unknown
    affected_groups: list[str]
    published_date: date | None = None
    effective_date: date | None = None
    source_id: UUID | None = None
    confidence: str
    status: PublicationStatus
    created_at: datetime
    updated_at: datetime
    localization: LocalizationMeta | None = None


class LegalSignalDetailResponse(BaseModel):
    item: LegalSignalDetail
    locale: LocaleResolution


class LegalSignalDetailListResponse(BaseModel):
    items: list[LegalSignalDetail]
    pagination: Pagination
    sort: SortMeta | None = None
    locale: LocaleResolution

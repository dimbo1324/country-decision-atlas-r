from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


# Mirrors apps/api/app/schemas/common.py -- the same field names/shapes so
# a frontend already typed against packages/contracts/generated/types.ts
# can consume mock responses without any changes.
class LocaleResolution(BaseModel):
    requested_locale: Literal["en", "ru"]
    resolved_locale: Literal["en", "ru"]
    translation_status: Literal["source", "translated", "fallback", "missing"]


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, object] | list[object] | None = None


class ErrorResponse(BaseModel):
    error: ApiError


# Mirrors apps/api/app/schemas/countries.py
class Country(BaseModel):
    id: UUID
    slug: str
    iso2: str
    iso3: str
    name: str
    official_name: str | None = None
    region: str | None = None
    subregion: str | None = None
    capital: str | None = None
    currency_code: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CountryProfile(BaseModel):
    id: UUID
    country_id: UUID
    summary: str
    residence_overview: str | None = None
    citizenship_overview: str | None = None
    tax_overview: str | None = None
    business_overview: str | None = None
    quality_of_life_overview: str | None = None
    risk_overview: str | None = None
    created_at: datetime
    updated_at: datetime


class CountryListResponse(BaseModel):
    items: list[Country]
    pagination: Pagination
    locale: LocaleResolution


class CountryResponse(BaseModel):
    item: Country
    locale: LocaleResolution


class CountryProfileResponse(BaseModel):
    item: CountryProfile
    locale: LocaleResolution


# Mirrors apps/api/app/schemas/trust.py
class TrustComponentBreakdown(BaseModel):
    source_quality_score: float | None = None
    evidence_depth_score: float | None = None
    freshness_score: float | None = None
    review_coverage_score: float | None = None
    contradiction_component: float | None = None


class CountryTrustResponse(BaseModel):
    country_slug: str
    trust_score: float | None = None
    trust_label: str
    confidence: str
    freshness_status: str
    source_count: int
    evidence_count: int
    legal_signal_count: int
    route_count: int
    platform_metric_count: int
    contradiction_score: float | None = None
    components: TrustComponentBreakdown
    last_verified_at: datetime | None = None
    computed_at: datetime | None = None
    expires_at: datetime | None = None
    methodology_version: str
    disclaimer: str


# Mirrors apps/api/app/schemas/country_read_model.py (Cii subset only)
class CountryReadModelCiiMetric(BaseModel):
    slug: str
    name_en: str
    name_ru: str
    score: float
    weight: float
    weighted_score: float
    data_year: int | None = None
    source_name: str | None = None
    reliability: str | None = None
    base_weight: float | None = None
    modifier: float | None = None
    adjusted_weight: float | None = None


class CountryReadModelCii(BaseModel):
    overall_score: float
    confidence: str
    drift: float | None = None
    version: str
    formula_version: str | None = None
    aggregation_method: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)
    calculated_at: datetime
    metrics: list[CountryReadModelCiiMetric] = Field(default_factory=list)


# Mirrors apps/api/app/schemas/cii_comparison.py
class ComparedScenario(BaseModel):
    slug: str
    title: str


class ComparedCountry(BaseModel):
    slug: str
    name: str
    iso2: str | None = None
    cii_score: float | None = None
    cii_confidence: str | None = None
    country_drift: float | None = None


class ComparedMetricValue(BaseModel):
    country_slug: str
    value: float | None = None
    effective_value: float | None = None
    quality_warnings: list[str] = Field(default_factory=list)


class ComparedMetric(BaseModel):
    metric_slug: str
    metric_name: str
    display_order: int
    higher_is_better: bool
    weight: float | None = None
    delta: float | None = None
    winner_country_slug: str | None = None
    values: list[ComparedMetricValue] = Field(default_factory=list)


class CiiCountryComparisonResponse(BaseModel):
    scenario: ComparedScenario
    locale: LocaleResolution
    countries: list[ComparedCountry] = Field(default_factory=list)
    metrics: list[ComparedMetric] = Field(default_factory=list)
    formula_version: str | None = None
    aggregation_method: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)


# Mirrors apps/api/app/schemas/sources.py + decision_engine.SourceListWithLocaleResponse
class Source(BaseModel):
    id: UUID
    title: str
    url: str
    source_type: str
    publisher: str | None = None
    country_id: UUID | None = None
    reliability_level: str
    language: str | None = None
    confidence: str | None = None
    status: str | None = None
    published_at: date | None = None
    accessed_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class SourceListWithLocaleResponse(BaseModel):
    items: list[Source]
    pagination: Pagination
    locale: LocaleResolution


# Mirrors apps/api/app/schemas/search.py
SearchResultType = Literal["country", "source"]


class SearchResultItem(BaseModel):
    id: str
    entity_type: SearchResultType
    entity_id: str
    country_slug: str | None = None
    title: str
    snippet: str
    path: str
    rank: float


class SearchResponse(BaseModel):
    query: str
    locale: Literal["en", "ru"]
    total: int
    limit: int
    offset: int
    items: list[SearchResultItem] = Field(default_factory=list)

from app.schemas.common import LocaleResolution
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


CompatibilityLabel = Literal["favourable", "mixed", "restrictive", "unknown"]
CompatibilityConfidence = Literal["low", "medium", "high"]
CompatibilityFreshness = Literal["fresh", "current", "stale", "unknown"]


class CountryPairCountry(BaseModel):
    slug: str
    name: str
    iso2: str | None = None


class CountryPairSourceRef(BaseModel):
    id: str
    title: str
    url: str
    source_type: str | None = None
    publisher: str | None = None
    confidence: str | None = None
    country_slug: str | None = None


class CountryPairEvidenceRef(BaseModel):
    id: str
    claim: str | None = None
    excerpt: str | None = None
    source_id: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    confidence: str | None = None
    country_slug: str | None = None


class CountryPairNote(BaseModel):
    type: str
    message: str


class CountryPairCompatibility(BaseModel):
    label: CompatibilityLabel
    confidence: CompatibilityConfidence
    freshness_status: CompatibilityFreshness
    visa_note: str | None = None
    tax_treaty_note: str | None = None
    banking_note: str | None = None
    flight_logistics_note: str | None = None
    timezone_note: str | None = None
    language_note: str | None = None
    migration_restriction_note: str | None = None
    practical_summary: str | None = None
    last_verified_at: datetime | None = None


class CountryPairCompatibilityResponse(BaseModel):
    origin_country: CountryPairCountry
    destination_country: CountryPairCountry
    compatibility: CountryPairCompatibility
    sources: list[CountryPairSourceRef]
    evidence: list[CountryPairEvidenceRef]
    disclaimer: str
    locale: LocaleResolution


class CountryPairCompatibilityListItem(BaseModel):
    destination_country: CountryPairCountry
    compatibility: CountryPairCompatibility
    sources: list[CountryPairSourceRef]
    evidence: list[CountryPairEvidenceRef]


class CountryPairCompatibilityListResponse(BaseModel):
    origin_country: CountryPairCountry
    items: list[CountryPairCompatibilityListItem]
    disclaimer: str
    locale: LocaleResolution


class CountryPairCompatibilitySummary(BaseModel):
    origin_slug: str
    destination_slug: str
    compatibility_label: CompatibilityLabel
    confidence: CompatibilityConfidence
    freshness_status: CompatibilityFreshness
    practical_summary: str | None = None
    key_notes: list[CountryPairNote] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

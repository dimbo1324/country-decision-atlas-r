from datetime import datetime
from uuid import UUID

from app.schemas.common import LocaleResolution, Pagination
from pydantic import BaseModel, Field


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


class ScenarioRunInput(BaseModel):
    scenario_slug: str
    country_ids: list[UUID] = Field(min_length=1)


class ScenarioRunCountryResult(BaseModel):
    country_id: UUID
    country_slug: str
    score: float
    score_label: str
    summary: str | None = None


class ScenarioRunResult(BaseModel):
    scenario_slug: str
    results: list[ScenarioRunCountryResult]

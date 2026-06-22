from app.schemas.common import LocaleResolution
from pydantic import BaseModel, Field


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
    weights_version: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)

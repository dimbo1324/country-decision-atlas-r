from app.schemas.common import LocaleResolution
from pydantic import BaseModel, Field


class MatrixCountry(BaseModel):
    slug: str
    name: str
    iso2: str | None = None


class MatrixScenario(BaseModel):
    slug: str
    name: str
    display_order: int


class MatrixCell(BaseModel):
    country_slug: str
    scenario_slug: str
    cii_score: float | None = None
    cii_confidence: str | None = None
    country_drift: float | None = None
    score_label: str | None = None
    confidence_label: str | None = None
    formula_version: str | None = None
    aggregation_method: str | None = None
    weights_version: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)


class CompareMatrixResponse(BaseModel):
    locale: LocaleResolution
    countries: list[MatrixCountry] = Field(default_factory=list)
    scenarios: list[MatrixScenario] = Field(default_factory=list)
    cells: list[MatrixCell] = Field(default_factory=list)
    formula_version: str | None = None
    aggregation_method: str | None = None
    weights_version: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)

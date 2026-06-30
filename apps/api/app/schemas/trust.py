from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


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
    disclaimer: str = Field(
        default="This is a data quality indicator, not a recommendation. Not legal advice."
    )


class TrustRecomputeRequest(BaseModel):
    country_slug: str | None = None
    dry_run: bool = False


class TrustRecomputeCountryResult(BaseModel):
    country_slug: str
    feature_enabled: bool
    country_not_found: bool
    dry_run: bool
    computed: bool
    stored: bool
    trust_label: str | None = None
    trust_score: float | None = None
    confidence: str | None = None
    freshness_status: str | None = None
    error: str | None = None


class TrustRecomputeSummary(BaseModel):
    feature_enabled: bool
    dry_run: bool
    countries_processed: int
    countries_computed: int
    countries_stored: int
    countries_failed: int
    errors: list[dict[str, Any]] = Field(default_factory=list)

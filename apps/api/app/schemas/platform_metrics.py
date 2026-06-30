from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class PlatformMetricInputSummary(BaseModel):
    raw: dict[str, Any] = Field(default_factory=dict)


class PlatformMetric(BaseModel):
    country_slug: str
    metric_key: str
    scenario_slug: str | None = None
    value: float | None = None
    label: str
    confidence: str
    freshness_status: str
    window_days: int
    methodology_version: str
    input_summary: PlatformMetricInputSummary | None = None
    source_count: int
    evidence_count: int
    signal_count: int
    event_count: int
    computed_at: datetime | None = None
    expires_at: datetime | None = None


class PlatformMetricListResponse(BaseModel):
    items: list[PlatformMetric]
    country_slug: str


class PlatformMetricDetailResponse(BaseModel):
    item: PlatformMetric


class PlatformMetricsRecomputeRequest(BaseModel):
    dry_run: bool = False
    metric_key: str | None = None
    scenario_slug: str | None = None


class PlatformMetricCountryResult(BaseModel):
    country_slug: str
    metrics_computed: int
    metrics_written: int
    metrics_failed: int
    errors: list[str] = Field(default_factory=list)


class PlatformMetricsRecomputeResult(BaseModel):
    feature_enabled: bool
    dry_run: bool
    country_slug: str
    metrics_computed: int
    metrics_written: int
    metrics_failed: int
    errors: list[str] = Field(default_factory=list)


class PlatformMetricsRecomputeSummary(BaseModel):
    feature_enabled: bool
    dry_run: bool
    countries_requested: int
    countries_processed: int
    countries_skipped: int
    metrics_computed: int
    metrics_written: int
    metrics_failed: int
    errors: list[str] = Field(default_factory=list)

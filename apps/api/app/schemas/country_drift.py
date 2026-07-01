from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Any


class CountryDriftSnapshot(BaseModel):
    country_slug: str
    period_start: date
    period_end: date
    window_days: int
    label: str
    previous_label: str | None = None
    confidence: str
    net_score: float | None = None
    positive_weight: float
    negative_weight: float
    neutral_weight: float
    mixed_weight: float
    uncertain_weight: float
    total_weight: float
    event_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    uncertain_count: int
    methodology_version: str
    input_summary: dict[str, Any]
    computed_at: datetime
    expires_at: datetime | None = None


class CountryDriftHistoryItem(BaseModel):
    period_start: date
    period_end: date
    label: str
    confidence: str
    net_score: float | None = None
    event_count: int
    computed_at: datetime


class CountryDriftResponse(BaseModel):
    country_slug: str
    latest_snapshot: CountryDriftSnapshot | None = None
    history: list[CountryDriftHistoryItem] = Field(default_factory=list)
    disclaimer: str = Field(
        default="This is a contextual trend indicator based on legal signal events, not legal advice or a prediction."
    )


class CountryDriftRecomputeRequest(BaseModel):
    dry_run: bool = False
    emit_events: bool = True


class CountryDriftRecomputeResult(BaseModel):
    country_slug: str
    country_not_found: bool
    dry_run: bool
    computed: bool
    stored: bool
    label: str | None = None
    previous_label: str | None = None
    confidence: str | None = None
    net_score: float | None = None
    event_count: int
    event_emitted: bool
    error: str | None = None


class CountryDriftBatchRecomputeResult(BaseModel):
    countries_processed: int
    snapshots_written: int
    events_emitted: int
    insufficient_data_count: int
    errors: list[dict[str, Any]] = Field(default_factory=list)

from app.services.platform_metric_types import (
    GLOBAL_SCENARIO_SLUG,
    METHODOLOGY_VERSION,
    PlatformMetricComputation,
)
from app.services.platform_metric_utils import (
    days_old,
    decimal_score,
    frequency,
    parse_date,
    unique_count,
    velocity_label,
)
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any


IMPACT_WEIGHTS = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
}
DIRECTION_FACTORS = {
    "positive": 1.0,
    "negative": 1.0,
    "mixed": 0.8,
    "neutral": 0.5,
    "uncertain": 0.4,
}


def compute_legal_velocity_index(
    events: Sequence[Mapping[str, Any]],
    window_days: int = 365,
) -> PlatformMetricComputation:
    rows = [dict(event) for event in events]
    event_count = len(rows)
    source_count = unique_count(rows, "source_id")
    evidence_count = unique_count(rows, "evidence_item_id")
    raw_points = sum(_event_points(row) for row in rows)
    value = None if event_count < 3 else decimal_score(raw_points * 8)
    impact_levels = [str(row.get("impact_level") or "") for row in rows]
    impact_directions = [str(row.get("impact_direction") or "") for row in rows]
    return PlatformMetricComputation(
        metric_key="legal_velocity_index",
        scenario_slug=GLOBAL_SCENARIO_SLUG,
        value=value,
        label=velocity_label(value),
        confidence=_confidence(event_count, evidence_count),
        freshness_status=_freshness(rows),
        window_days=window_days,
        methodology_version=METHODOLOGY_VERSION,
        input_summary={
            "raw_points": round(raw_points, 4),
            "event_count": event_count,
            "source_count": source_count,
            "evidence_count": evidence_count,
            "impact_levels": frequency(impact_levels),
            "impact_directions": frequency(impact_directions),
            "window_days": window_days,
        },
        source_count=source_count,
        evidence_count=evidence_count,
        signal_count=unique_count(rows, "signal_id"),
        event_count=event_count,
    )


def _event_points(row: Mapping[str, Any]) -> float:
    impact_level = str(row.get("impact_level") or "low")
    impact_direction = str(row.get("impact_direction") or "uncertain")
    return IMPACT_WEIGHTS.get(impact_level, 1.0) * DIRECTION_FACTORS.get(
        impact_direction, 0.4
    )


def _confidence(event_count: int, evidence_count: int) -> str:
    if event_count >= 8 and evidence_count >= 5:
        return "high"
    if event_count >= 4 and evidence_count >= 2:
        return "medium"
    return "low"


def _freshness(rows: Sequence[Mapping[str, Any]]) -> str:
    event_dates = [
        parsed
        for row in rows
        if (parsed := parse_date(row.get("event_date"))) is not None
    ]
    if not event_dates:
        return "unknown"
    age = days_old(max(event_dates), date.today())
    if age is None:
        return "unknown"
    if age <= 90:
        return "fresh"
    if age <= 365:
        return "stale"
    return "unknown"

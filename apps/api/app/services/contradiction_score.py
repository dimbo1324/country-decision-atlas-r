from app.services.platform_metric_types import (
    GLOBAL_SCENARIO_SLUG,
    METHODOLOGY_VERSION,
    PlatformMetricComputation,
)
from app.services.platform_metric_utils import (
    clamp,
    decimal_score,
    normalize_groups,
    risk_label,
    unique_count,
)
from collections.abc import Mapping, Sequence
from typing import Any


GROUP_BUCKETS = {
    "business": {"business", "entrepreneurs", "self_employed", "investors"},
    "migration": {"migration", "migrants", "residents", "families", "remote_workers"},
    "citizenship": {"citizenship"},
    "banking": {"banking"},
    "tax": {"tax", "low_income"},
    "safety": {"safety", "political_risk", "freedom", "activists", "journalists"},
}
OFFICIAL_SOURCE_TYPES = {"official", "dataset"}


def compute_contradiction_score(
    inputs: Sequence[Mapping[str, Any]],
    window_days: int = 365,
) -> PlatformMetricComputation:
    rows = [dict(row) for row in inputs]
    topics = _topics(rows)
    topic_count = len(topics)
    signal_count = unique_count(rows, "signal_id")
    source_count = unique_count(rows, "source_id")
    evidence_count = unique_count(rows, "evidence_item_id")
    if topic_count < 2 or signal_count < 3:
        return _result(None, rows, topics, window_days)
    topic_points = {
        topic: _topic_points(topic_rows) for topic, topic_rows in topics.items()
    }
    value = decimal_score(clamp(sum(topic_points.values()) * 12))
    return PlatformMetricComputation(
        metric_key="contradiction_score",
        scenario_slug=GLOBAL_SCENARIO_SLUG,
        value=value,
        label=risk_label(value),
        confidence=_confidence(signal_count, source_count),
        freshness_status=_freshness(rows),
        window_days=window_days,
        methodology_version=METHODOLOGY_VERSION,
        input_summary={
            "topic_count": topic_count,
            "signal_count": signal_count,
            "source_count": source_count,
            "evidence_count": evidence_count,
            "contradictory_topic_count": sum(
                1 for points in topic_points.values() if points > 0
            ),
            "topic_points": topic_points,
            "window_days": window_days,
        },
        source_count=source_count,
        evidence_count=evidence_count,
        signal_count=signal_count,
        event_count=unique_count(rows, "event_id"),
    )


def _result(
    value: None,
    rows: Sequence[Mapping[str, Any]],
    topics: dict[str, list[Mapping[str, Any]]],
    window_days: int,
) -> PlatformMetricComputation:
    return PlatformMetricComputation(
        metric_key="contradiction_score",
        scenario_slug=GLOBAL_SCENARIO_SLUG,
        value=value,
        label="insufficient_data",
        confidence="low",
        freshness_status=_freshness(rows),
        window_days=window_days,
        methodology_version=METHODOLOGY_VERSION,
        input_summary={
            "topic_count": len(topics),
            "signal_count": unique_count(rows, "signal_id"),
            "source_count": unique_count(rows, "source_id"),
            "evidence_count": unique_count(rows, "evidence_item_id"),
            "contradictory_topic_count": 0,
            "topic_points": {},
            "window_days": window_days,
        },
        source_count=unique_count(rows, "source_id"),
        evidence_count=unique_count(rows, "evidence_item_id"),
        signal_count=unique_count(rows, "signal_id"),
        event_count=unique_count(rows, "event_id"),
    )


def _topics(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        signal_type = str(row.get("signal_type") or "other")
        for bucket in _group_buckets(row):
            grouped.setdefault(f"{signal_type}:{bucket}", []).append(row)
    return grouped


def _group_buckets(row: Mapping[str, Any]) -> list[str]:
    groups = normalize_groups(row.get("affected_groups"))
    if not groups:
        return ["general"]
    buckets = {
        bucket
        for group in groups
        for bucket, values in GROUP_BUCKETS.items()
        if group in values
    }
    return sorted(buckets) if buckets else ["general"]


def _topic_points(rows: Sequence[Mapping[str, Any]]) -> int:
    directions = {str(row.get("impact_direction") or "uncertain") for row in rows}
    points = 0
    if "positive" in directions and "negative" in directions:
        points += 4
    elif "positive" in directions and directions.intersection({"mixed", "uncertain"}):
        points += 2
    if _source_type_disagreement(rows):
        points += 3
    if any(_is_high_impact_low_confidence(row) for row in rows):
        points += 2
    if _has_multiple_opposite_events(rows):
        points += 3
    return points


def _source_type_disagreement(rows: Sequence[Mapping[str, Any]]) -> bool:
    official_directions = {
        str(row.get("impact_direction") or "")
        for row in rows
        if str(row.get("source_type") or "") in OFFICIAL_SOURCE_TYPES
    }
    other_directions = {
        str(row.get("impact_direction") or "")
        for row in rows
        if str(row.get("source_type") or "") not in OFFICIAL_SOURCE_TYPES
    }
    return bool(
        official_directions
        and other_directions
        and official_directions != other_directions
    )


def _is_high_impact_low_confidence(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("impact_level") or "") in {"high", "critical"}
        and str(row.get("confidence") or "") == "low"
    )


def _has_multiple_opposite_events(rows: Sequence[Mapping[str, Any]]) -> bool:
    event_directions = {
        str(row.get("event_id")): str(row.get("impact_direction") or "")
        for row in rows
        if row.get("event_id") is not None
    }
    directions = set(event_directions.values())
    return (
        len(event_directions) > 1
        and "positive" in directions
        and "negative" in directions
    )


def _confidence(signal_count: int, source_count: int) -> str:
    if signal_count >= 8 and source_count >= 5:
        return "high"
    if signal_count >= 4 and source_count >= 3:
        return "medium"
    return "low"


def _freshness(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return "unknown"
    return "fresh"

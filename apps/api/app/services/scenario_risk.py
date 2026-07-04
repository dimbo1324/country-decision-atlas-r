from app.services.platform_metric_types import (
    METHODOLOGY_VERSION,
    PlatformMetricComputation,
)
from app.services.platform_metric_utils import (
    clamp,
    days_old,
    decimal_score,
    frequency,
    normalize_groups,
    risk_label,
    unique_count,
)
from collections.abc import Mapping, Sequence
from typing import Any


SCENARIO_RELEVANCE = {
    "relocation_residence": {
        "signal_types": {"migration", "residence", "banking", "tax", "safety"},
        "affected_groups": {
            "migrants",
            "residents",
            "families",
            "remote_workers",
        },
    },
    "permanent_residence_citizenship": {
        "signal_types": {
            "migration",
            "residence",
            "citizenship",
            "rule_of_law",
        },
        "affected_groups": {"migrants", "residents", "families"},
    },
    "low_budget_living": {
        "signal_types": {
            "cost_of_living",
            "tax",
            "banking",
            "healthcare",
            "safety",
        },
        "affected_groups": {"low_income", "migrants", "families"},
    },
    "business_self_employment": {
        "signal_types": {
            "business",
            "tax",
            "banking",
            "property",
            "rule_of_law",
        },
        "affected_groups": {"entrepreneurs", "self_employed", "investors"},
    },
    "safety_political_risk": {
        "signal_types": {"safety", "political_risk", "rule_of_law", "freedom"},
        "affected_groups": {
            "migrants",
            "activists",
            "journalists",
            "residents",
        },
    },
}
LEVEL_POINTS = {
    "low": 5.0,
    "medium": 12.0,
    "high": 22.0,
    "critical": 35.0,
}
DIRECTION_FACTORS = {
    "negative": 1.0,
    "mixed": 0.5,
    "uncertain": 0.4,
    "neutral": 0.2,
    "positive": -0.6,
}


def compute_scenario_specific_risk_score(
    inputs: Sequence[Mapping[str, Any]],
    scenario_slug: str,
    window_days: int = 365,
) -> PlatformMetricComputation:
    rows = [dict(row) for row in inputs]
    if scenario_slug not in SCENARIO_RELEVANCE:
        return _insufficient(
            scenario_slug, rows, window_days, 0, len(rows), 0.0
        )
    scored = [(_relevance(row, scenario_slug), row) for row in rows]
    relevant_rows = [row for relevance, row in scored if relevance > 0]
    ignored_signal_count = len(rows) - len(relevant_rows)
    risk_delta = sum(
        _signal_points(row, relevance)
        for relevance, row in scored
        if relevance > 0
    )
    if len(relevant_rows) < 2:
        return _insufficient(
            scenario_slug,
            rows,
            window_days,
            len(relevant_rows),
            ignored_signal_count,
            risk_delta,
        )
    value = decimal_score(clamp(35.0 + risk_delta))
    evidence_count = unique_count(relevant_rows, "evidence_item_id")
    source_count = unique_count(relevant_rows, "source_id")
    signal_types = [str(row.get("signal_type") or "") for row in relevant_rows]
    groups = [
        group
        for row in relevant_rows
        for group in normalize_groups(row.get("affected_groups"))
    ]
    return PlatformMetricComputation(
        metric_key="scenario_specific_risk_score",
        scenario_slug=scenario_slug,
        value=value,
        label=risk_label(value),
        confidence=_confidence(len(relevant_rows), evidence_count),
        freshness_status=_freshness(relevant_rows),
        window_days=window_days,
        methodology_version=METHODOLOGY_VERSION,
        input_summary={
            "scenario_slug": scenario_slug,
            "relevant_signal_count": len(relevant_rows),
            "ignored_signal_count": ignored_signal_count,
            "source_count": source_count,
            "evidence_count": evidence_count,
            "risk_delta": round(risk_delta, 4),
            "window_days": window_days,
            "top_signal_types": frequency(signal_types),
            "top_affected_groups": frequency(groups),
        },
        source_count=source_count,
        evidence_count=evidence_count,
        signal_count=len(relevant_rows),
        event_count=unique_count(relevant_rows, "event_id"),
    )


def _insufficient(
    scenario_slug: str,
    rows: Sequence[Mapping[str, Any]],
    window_days: int,
    relevant_signal_count: int,
    ignored_signal_count: int,
    risk_delta: float,
) -> PlatformMetricComputation:
    relevant_rows = [
        row
        for row in rows
        if scenario_slug in SCENARIO_RELEVANCE
        and _relevance(row, scenario_slug) > 0
    ]
    evidence_count = unique_count(relevant_rows, "evidence_item_id")
    source_count = unique_count(relevant_rows, "source_id")
    return PlatformMetricComputation(
        metric_key="scenario_specific_risk_score",
        scenario_slug=scenario_slug,
        value=None,
        label="insufficient_data",
        confidence="low",
        freshness_status=_freshness(relevant_rows),
        window_days=window_days,
        methodology_version=METHODOLOGY_VERSION,
        input_summary={
            "scenario_slug": scenario_slug,
            "relevant_signal_count": relevant_signal_count,
            "ignored_signal_count": ignored_signal_count,
            "source_count": source_count,
            "evidence_count": evidence_count,
            "risk_delta": round(risk_delta, 4),
            "window_days": window_days,
            "top_signal_types": frequency(
                str(row.get("signal_type") or "") for row in relevant_rows
            ),
            "top_affected_groups": frequency(
                group
                for row in relevant_rows
                for group in normalize_groups(row.get("affected_groups"))
            ),
        },
        source_count=source_count,
        evidence_count=evidence_count,
        signal_count=relevant_signal_count,
        event_count=unique_count(relevant_rows, "event_id"),
    )


def _signal_points(row: Mapping[str, Any], relevance: float) -> float:
    impact_level = str(row.get("impact_level") or "low")
    impact_direction = str(row.get("impact_direction") or "uncertain")
    return (
        LEVEL_POINTS.get(impact_level, 5.0)
        * DIRECTION_FACTORS.get(impact_direction, 0.4)
        * _recency_factor(row.get("event_date"))
        * relevance
    )


def _relevance(row: Mapping[str, Any], scenario_slug: str) -> float:
    scenario = SCENARIO_RELEVANCE[scenario_slug]
    signal_type = str(row.get("signal_type") or "")
    affected_groups = set(normalize_groups(row.get("affected_groups")))
    if signal_type in scenario["signal_types"] or affected_groups.intersection(
        scenario["affected_groups"]
    ):
        return 1.0
    if _weak_signal_match(signal_type, scenario["signal_types"]):
        return 0.5
    if affected_groups and _weak_group_match(
        affected_groups, scenario["affected_groups"]
    ):
        return 0.25
    return 0.0


def _weak_signal_match(signal_type: str, relevant: set[str]) -> bool:
    return any(part in signal_type or signal_type in part for part in relevant)


def _weak_group_match(groups: set[str], relevant: set[str]) -> bool:
    return any(
        group in item or item in group for group in groups for item in relevant
    )


def _recency_factor(value: Any) -> float:
    age = days_old(value)
    if age is None:
        return 0.4
    if age <= 180:
        return 1.0
    if age <= 365:
        return 0.7
    if age <= 730:
        return 0.4
    return 0.2


def _confidence(relevant_signal_count: int, evidence_count: int) -> str:
    if relevant_signal_count >= 6 and evidence_count >= 5:
        return "high"
    if relevant_signal_count >= 3 and evidence_count >= 2:
        return "medium"
    return "low"


def _freshness(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return "unknown"
    freshest_age = min(
        (
            age
            for row in rows
            if (age := days_old(row.get("event_date"))) is not None
        ),
        default=None,
    )
    if freshest_age is None:
        return "unknown"
    if freshest_age <= 90:
        return "fresh"
    if freshest_age <= 365:
        return "stale"
    return "unknown"

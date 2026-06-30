from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


METHODOLOGY_VERSION = "v1.0"

MIN_SOURCES_FOR_SCORE = 5
MIN_EVIDENCE_FOR_SCORE = 5
MIN_LEGAL_SIGNALS_FOR_SCORE = 3

FRESHNESS_FRESH_DAYS = 180
FRESHNESS_AGING_DAYS = 365


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _decimal(value: float) -> Decimal:
    return Decimal(str(_clamp(value))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_source_quality_score(source_count: int) -> float:
    if source_count == 0:
        return 0.0
    if source_count < 5:
        return 35.0
    if source_count < 10:
        return 55.0
    if source_count < 15:
        return 75.0
    return 100.0


def compute_evidence_depth_score(evidence_count: int) -> float:
    if evidence_count == 0:
        return 0.0
    if evidence_count < 5:
        return 30.0
    if evidence_count < 10:
        return 50.0
    if evidence_count < 20:
        return 75.0
    return 100.0


def compute_freshness_score(
    last_verified_at: datetime | None, now: datetime
) -> tuple[float, str]:
    if last_verified_at is None:
        return 35.0, "unknown"
    days = (
        now - last_verified_at.replace(tzinfo=UTC)
        if last_verified_at.tzinfo is None
        else now - last_verified_at
    ).days
    if days <= FRESHNESS_FRESH_DAYS:
        return 100.0, "fresh"
    if days <= FRESHNESS_AGING_DAYS:
        return 70.0, "aging"
    return 40.0, "stale"


def compute_review_coverage_score(
    source_count: int,
    evidence_count: int,
    legal_signal_count: int,
    route_count: int,
) -> float:
    total = source_count + evidence_count + legal_signal_count + route_count
    if total == 0:
        return 0.0
    if total < 5:
        return 30.0
    if total < 15:
        return 55.0
    if total < 30:
        return 75.0
    if total < 50:
        return 88.0
    return 100.0


def compute_contradiction_component(
    contradiction_score_value: float | None,
) -> tuple[float, bool]:
    if contradiction_score_value is None:
        return 50.0, True
    return _clamp(100.0 - float(contradiction_score_value)), False


def compute_trust_label(trust_score: float | None) -> str:
    if trust_score is None:
        return "insufficient_data"
    if trust_score >= 85:
        return "very_high"
    if trust_score >= 70:
        return "high"
    if trust_score >= 50:
        return "medium"
    if trust_score >= 30:
        return "low"
    return "very_low"


def compute_confidence(
    source_count: int,
    evidence_count: int,
    legal_signal_count: int,
    freshness_status: str,
) -> str:
    if (
        source_count >= 15
        and evidence_count >= 20
        and legal_signal_count >= 8
        and freshness_status in ("fresh", "aging")
    ):
        return "high"
    if source_count >= 10 and evidence_count >= 10 and legal_signal_count >= 5:
        return "medium"
    return "low"


def has_sufficient_data(
    source_count: int, evidence_count: int, legal_signal_count: int
) -> bool:
    return (
        source_count >= MIN_SOURCES_FOR_SCORE
        and evidence_count >= MIN_EVIDENCE_FOR_SCORE
        and legal_signal_count >= MIN_LEGAL_SIGNALS_FOR_SCORE
    )


def compute_trust_score_from_inputs(
    inputs: dict[str, Any], now: datetime
) -> dict[str, Any]:
    source_count = int(inputs.get("source_count") or 0)
    evidence_count = int(inputs.get("evidence_count") or 0)
    legal_signal_count = int(inputs.get("legal_signal_count") or 0)
    route_count = int(inputs.get("route_count") or 0)
    platform_metric_count = int(inputs.get("platform_metric_count") or 0)
    last_verified_at = inputs.get("last_verified_at")
    raw_contradiction = inputs.get("contradiction_score_value")
    contradiction_raw: float | None = (
        float(raw_contradiction) if raw_contradiction is not None else None
    )

    src_score = compute_source_quality_score(source_count)
    evd_score = compute_evidence_depth_score(evidence_count)
    freshness_score, freshness_status = compute_freshness_score(last_verified_at, now)
    review_score = compute_review_coverage_score(
        source_count, evidence_count, legal_signal_count, route_count
    )
    contradiction_component, contradiction_missing = compute_contradiction_component(
        contradiction_raw
    )

    weighted = (
        src_score * 0.25
        + evd_score * 0.25
        + freshness_score * 0.20
        + review_score * 0.15
        + contradiction_component * 0.15
    )
    weakest = min(
        src_score, evd_score, freshness_score, review_score, contradiction_component
    )
    raw_trust = min(weighted, weakest + 20.0)

    if not has_sufficient_data(source_count, evidence_count, legal_signal_count):
        trust_score_val: float | None = None
        trust_label = "insufficient_data"
    else:
        trust_score_val = _clamp(raw_trust)
        trust_label = compute_trust_label(trust_score_val)

    confidence = compute_confidence(
        source_count, evidence_count, legal_signal_count, freshness_status
    )

    input_summary: dict[str, Any] = {
        "source_count": source_count,
        "evidence_count": evidence_count,
        "legal_signal_count": legal_signal_count,
        "route_count": route_count,
        "platform_metric_count": platform_metric_count,
        "contradiction_score_missing": contradiction_missing,
        "last_verified_at_source": "max(sources,evidence,legal_signals).updated_at",
        "has_explicit_verification_date": last_verified_at is not None,
        "components": {
            "source_quality_score": round(src_score, 2),
            "evidence_depth_score": round(evd_score, 2),
            "freshness_score": round(freshness_score, 2),
            "review_coverage_score": round(review_score, 2),
            "contradiction_component": round(contradiction_component, 2),
        },
    }

    return {
        "country_id": inputs["country_id"],
        "trust_score": float(_decimal(trust_score_val))
        if trust_score_val is not None
        else None,
        "trust_label": trust_label,
        "confidence": confidence,
        "freshness_status": freshness_status,
        "source_count": source_count,
        "evidence_count": evidence_count,
        "legal_signal_count": legal_signal_count,
        "route_count": route_count,
        "platform_metric_count": platform_metric_count,
        "contradiction_score": float(_decimal(contradiction_raw))
        if contradiction_raw is not None
        else None,
        "freshness_score": float(_decimal(freshness_score)),
        "evidence_depth_score": float(_decimal(evd_score)),
        "source_quality_score": float(_decimal(src_score)),
        "review_coverage_score": float(_decimal(review_score)),
        "last_verified_at": last_verified_at,
        "computed_at": now,
        "expires_at": now + timedelta(days=30),
        "methodology_version": METHODOLOGY_VERSION,
        "input_summary": input_summary,
    }

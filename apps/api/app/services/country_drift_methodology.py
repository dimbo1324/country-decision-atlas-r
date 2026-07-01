from decimal import ROUND_HALF_UP, Decimal
from typing import Any


WINDOW_DAYS = 180
MIN_EVENTS_FOR_DRIFT = 3
METHODOLOGY_VERSION = "v1.0"

IMPACT_LEVEL_WEIGHTS: dict[str, Decimal] = {
    "low": Decimal("1"),
    "medium": Decimal("2"),
    "high": Decimal("3"),
    "critical": Decimal("4"),
}

IMPACT_DIRECTIONS = ("positive", "negative", "neutral", "mixed", "uncertain")

LABEL_INSUFFICIENT_DATA = "insufficient_data"
LABEL_NEGATIVE = "negative"
LABEL_STABLE = "stable"
LABEL_MILDLY_POSITIVE = "mildly_positive"
LABEL_POSITIVE = "positive"

NEGATIVE_THRESHOLD = Decimal("-15")
MILDLY_POSITIVE_THRESHOLD = Decimal("15")
POSITIVE_THRESHOLD = Decimal("40")

CONFIDENCE_LOW = "low"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_HIGH = "high"

CONFIDENCE_MEDIUM_MIN_EVENTS = 5
CONFIDENCE_HIGH_MIN_EVENTS = 8
UNCERTAIN_RATIO_DOWNGRADE_THRESHOLD = Decimal("0.4")


def impact_level_weight(impact_level: str) -> Decimal:
    try:
        return IMPACT_LEVEL_WEIGHTS[impact_level]
    except KeyError:
        raise ValueError(f"unknown impact_level: {impact_level}") from None


def compute_net_score(
    positive_weight: Decimal,
    negative_weight: Decimal,
    neutral_weight: Decimal,
    mixed_weight: Decimal,
    uncertain_weight: Decimal,
) -> Decimal | None:
    total_weight = (
        positive_weight
        + negative_weight
        + neutral_weight
        + mixed_weight
        + uncertain_weight
    )
    if total_weight == 0:
        return None
    directional_net = positive_weight - negative_weight
    net_score = (directional_net / total_weight) * Decimal(100)
    return net_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def label_for_drift(event_count: int, net_score: Decimal | None) -> str:
    if event_count < MIN_EVENTS_FOR_DRIFT or net_score is None:
        return LABEL_INSUFFICIENT_DATA
    if net_score <= NEGATIVE_THRESHOLD:
        return LABEL_NEGATIVE
    if net_score < MILDLY_POSITIVE_THRESHOLD:
        return LABEL_STABLE
    if net_score < POSITIVE_THRESHOLD:
        return LABEL_MILDLY_POSITIVE
    return LABEL_POSITIVE


def _downgrade_confidence(confidence: str) -> str:
    if confidence == CONFIDENCE_HIGH:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW


def confidence_for_drift(
    event_count: int, mixed_count: int, uncertain_count: int
) -> str:
    if event_count < CONFIDENCE_MEDIUM_MIN_EVENTS:
        base = CONFIDENCE_LOW
    elif event_count < CONFIDENCE_HIGH_MIN_EVENTS:
        base = CONFIDENCE_MEDIUM
    else:
        base = CONFIDENCE_HIGH

    uncertain_ratio_exceeded = (
        event_count > 0
        and Decimal(mixed_count + uncertain_count)
        > Decimal(event_count) * UNCERTAIN_RATIO_DOWNGRADE_THRESHOLD
    )

    if uncertain_ratio_exceeded:
        return _downgrade_confidence(base)
    return base


def build_drift_input_summary(
    window_days: int = WINDOW_DAYS,
    event_ids: list[str] | None = None,
    legal_signal_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "window_days": window_days,
        "methodology_version": METHODOLOGY_VERSION,
        "impact_level_weights": {
            key: float(value) for key, value in IMPACT_LEVEL_WEIGHTS.items()
        },
        "label_thresholds": {
            "negative": "<= -15",
            "stable": "-15..15",
            "mildly_positive": "15..40",
            "positive": ">= 40",
        },
        "event_ids": event_ids or [],
        "legal_signal_ids": legal_signal_ids or [],
    }

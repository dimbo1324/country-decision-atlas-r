from app.core.errors import api_error
from collections.abc import Mapping, Sequence
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any


NORMALIZED_WEIGHT_PRECISION = Decimal("0.000001")
MIN_CUSTOM_WEIGHT_VALUE = Decimal("0")
MAX_CUSTOM_WEIGHT_VALUE = Decimal("100")

DECISION_CRITERIA = (
    "legalization_score",
    "long_term_status_score",
    "cost_of_living_score",
    "safety_score",
    "business_score",
    "legal_stability_score",
    "source_quality_score",
)

WEIGHT_MODE_BASE = "base"
WEIGHT_MODE_PERSONA = "persona"
WEIGHT_MODE_CUSTOM = "custom"
WEIGHT_MODE_PERSONA_CUSTOM = "persona_custom"


def _to_decimal(criterion: str, value: Any) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise api_error(
            422,
            "custom_weight_invalid",
            "Custom weight value is not a valid number.",
            {"criterion": criterion},
        ) from None
    if not parsed.is_finite():
        raise api_error(
            422,
            "custom_weight_invalid",
            "Custom weight value is not a valid number.",
            {"criterion": criterion},
        )
    return parsed


def validate_custom_weights(
    custom_weights: Mapping[str, Decimal | float | int],
    allowed_criteria: Sequence[str],
) -> None:
    allowed_set = set(allowed_criteria)
    unknown = sorted(set(custom_weights) - allowed_set)
    if unknown:
        raise api_error(
            422,
            "unknown_custom_weight_criterion",
            "Custom weights contain unknown criteria.",
            {"unknown_criteria": unknown},
        )
    missing = sorted(allowed_set - set(custom_weights))
    if missing:
        raise api_error(
            422,
            "custom_weights_incomplete",
            "Custom weights must include every active decision criterion.",
            {"missing_criteria": missing},
        )
    parsed = {
        criterion: _to_decimal(criterion, value)
        for criterion, value in custom_weights.items()
    }
    for criterion, value in parsed.items():
        if value < MIN_CUSTOM_WEIGHT_VALUE or value > MAX_CUSTOM_WEIGHT_VALUE:
            raise api_error(
                422,
                "custom_weight_out_of_range",
                "Custom weight must be between 0 and 100.",
                {"criterion": criterion, "value": float(value)},
            )
    total = sum(parsed.values())
    if total <= 0:
        raise api_error(
            422,
            "custom_weights_sum_zero",
            "At least one custom weight must be greater than zero.",
        )


def normalize_custom_weights(
    custom_weights: Mapping[str, Decimal | float | int] | None,
    allowed_criteria: Sequence[str],
) -> dict[str, Decimal] | None:
    if custom_weights is None:
        return None
    validate_custom_weights(custom_weights, allowed_criteria)
    parsed = {
        criterion: _to_decimal(criterion, value)
        for criterion, value in custom_weights.items()
    }
    total = sum(parsed.values())
    ordered_criteria = sorted(parsed)
    normalized: dict[str, Decimal] = {}
    running_total = Decimal("0")
    for index, criterion in enumerate(ordered_criteria):
        if index == len(ordered_criteria) - 1:
            share = Decimal("1") - running_total
        else:
            share = (parsed[criterion] / total).quantize(
                NORMALIZED_WEIGHT_PRECISION, rounding=ROUND_HALF_UP
            )
            running_total += share
        normalized[criterion] = share
    return normalized


def apply_effective_weights_to_breakdown(
    breakdown_items: Sequence[Mapping[str, Any]],
    effective_weights: Mapping[str, Decimal],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in breakdown_items:
        new_item = dict(item)
        effective_weight = effective_weights.get(str(item["criterion"]))
        if effective_weight is None:
            result.append(new_item)
            continue
        score = Decimal(str(item["score"]))
        new_item["weight"] = float(effective_weight)
        new_item["weighted_score"] = float(score * effective_weight)
        result.append(new_item)
    return result


def resolve_weight_mode(
    persona_slug: str | None,
    custom_weights: Mapping[str, Any] | None,
) -> str:
    if persona_slug and custom_weights:
        return WEIGHT_MODE_PERSONA_CUSTOM
    if persona_slug:
        return WEIGHT_MODE_PERSONA
    if custom_weights:
        return WEIGHT_MODE_CUSTOM
    return WEIGHT_MODE_BASE


def build_personalization_summary(
    *,
    persona_slug: str | None,
    custom_weights_applied: bool,
    base_weights: Mapping[str, Decimal],
    effective_weights: Mapping[str, Decimal],
) -> dict[str, Any]:
    weight_mode = resolve_weight_mode(
        persona_slug, effective_weights if custom_weights_applied else None
    )
    return {
        "weight_mode": weight_mode,
        "persona_slug": persona_slug,
        "custom_weights_applied": custom_weights_applied,
        "base_weights": [
            {"criterion": criterion, "weight": float(weight)}
            for criterion, weight in sorted(base_weights.items())
        ],
        "effective_weights": [
            {"criterion": criterion, "weight": float(weight)}
            for criterion, weight in sorted(effective_weights.items())
        ],
    }

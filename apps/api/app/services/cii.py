import math
from typing import Any


def _effective_value(normalized_value: float, polarity: str) -> float:
    if polarity == "negative":
        return 100.0 - normalized_value
    return normalized_value


def _protected_score(effective_value: float) -> float:
    return max(effective_value, 1.0)


def aggregate_cii_score(
    metric_values: list[dict[str, Any]],
) -> dict[str, Any]:
    warnings: list[str] = []
    valid_entries: list[dict[str, Any]] = []

    for mv in metric_values:
        slug = mv.get("slug", "")
        normalized_value = mv.get("normalized_value")
        weight = mv.get("weight")
        polarity = mv.get("polarity", "positive")

        if normalized_value is None:
            warnings.append(f"metric '{slug}' missing normalized_value")
            continue
        if weight is None or weight <= 0:
            warnings.append(f"metric '{slug}' has invalid weight")
            continue

        eff = _effective_value(float(normalized_value), str(polarity))
        ps = _protected_score(eff)
        valid_entries.append(
            {
                "slug": slug,
                "normalized_value": float(normalized_value),
                "effective_value": eff,
                "protected_score": ps,
                "weight": float(weight),
                "polarity": polarity,
            }
        )

    if not valid_entries:
        warnings.append("no valid metric entries for aggregation")
        return {
            "overall_score": 0.0,
            "aggregation_method": "geometric",
            "formula_version": "cii-v1.0",
            "warnings": warnings,
        }

    total_weight = sum(e["weight"] for e in valid_entries)
    if total_weight <= 0:
        warnings.append("total weight is zero or negative")
        return {
            "overall_score": 0.0,
            "aggregation_method": "geometric",
            "formula_version": "cii-v1.0",
            "warnings": warnings,
        }

    log_sum = sum(
        e["weight"] * math.log(e["protected_score"]) for e in valid_entries
    )
    raw_score = math.exp(log_sum / total_weight)
    overall_score = round(min(max(raw_score, 0.0), 100.0), 2)

    return {
        "overall_score": overall_score,
        "aggregation_method": "geometric",
        "formula_version": "cii-v1.0",
        "warnings": warnings,
    }


def compute_confidence(
    metric_values: list[dict[str, Any]],
) -> str:
    if not metric_values:
        return "low"

    reliability_scores: list[float] = []
    for mv in metric_values:
        rel = mv.get("reliability", "medium")
        if rel == "high":
            reliability_scores.append(1.0)
        elif rel == "medium":
            reliability_scores.append(0.6)
        else:
            reliability_scores.append(0.3)

    avg_reliability = sum(reliability_scores) / len(reliability_scores)
    coverage = len(metric_values) / max(len(metric_values), 6)

    combined = avg_reliability * coverage
    if combined >= 0.8:
        return "high"
    if combined >= 0.5:
        return "medium"
    return "low"

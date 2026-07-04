from app.services.cii import aggregate_cii_score
from typing import Any


def persona_weights_by_metric(
    profile: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {str(row["metric_slug"]): row for row in profile.get("weights", [])}


def persona_metric_entries(
    metric_rows: list[dict[str, Any]],
    profile: dict[str, Any],
    metric_defs_by_slug: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    metric_defs = metric_defs_by_slug or {}
    weights_by_metric = persona_weights_by_metric(profile)
    entries: list[dict[str, Any]] = []
    for row in metric_rows:
        metric_slug = str(row.get("metric_slug") or row.get("slug") or "")
        weight_row = weights_by_metric.get(metric_slug)
        if weight_row is None:
            continue
        metric_def = metric_defs.get(metric_slug, {})
        normalized_value = row.get(
            "normalized_value", row.get("value", row.get("score"))
        )
        entries.append(
            {
                "slug": metric_slug,
                "normalized_value": normalized_value,
                "weight": float(weight_row["adjusted_weight"]),
                "polarity": row.get("polarity")
                or metric_def.get("polarity", "positive"),
                "reliability": row.get("reliability", "medium"),
            }
        )
    return entries


def aggregate_persona_cii_score(
    metric_rows: list[dict[str, Any]],
    profile: dict[str, Any],
    metric_defs_by_slug: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return aggregate_cii_score(
        persona_metric_entries(metric_rows, profile, metric_defs_by_slug)
    )


def persona_metric_weight_metadata(
    metric_slug: str, profile: dict[str, Any]
) -> dict[str, float] | None:
    weight_row = persona_weights_by_metric(profile).get(metric_slug)
    if weight_row is None:
        return None
    return {
        "base_weight": float(weight_row["base_weight"]),
        "modifier": float(weight_row["modifier"]),
        "adjusted_weight": float(weight_row["adjusted_weight"]),
    }

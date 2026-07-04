from app.core.errors import api_error
from app.repositories import personas as personas_repository
from collections.abc import Mapping, Sequence
from decimal import Decimal
from psycopg import Connection
from typing import Any


DEFAULT_PERSONA_WEIGHTS_VERSION = "v1.0"
WEIGHT_SUM_TOLERANCE = Decimal("0.000001")


def validate_modifier_coverage(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if not rows:
        raise api_error(
            422,
            "persona_weights_degenerate",
            "No weight rows provided.",
        )
    missing: list[str] = [
        str(row.get("metric_slug", ""))
        for row in rows
        if row.get("modifier") is None
    ]
    if missing:
        raise api_error(
            422,
            "persona_modifier_incomplete",
            "Persona is missing modifiers for some metrics.",
            {"missing_metric_slugs": missing},
        )


def ensure_adjusted_weights_valid(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    for row in rows:
        if Decimal(str(row["adjusted_weight"])) < Decimal("0"):
            raise api_error(
                422,
                "persona_adjusted_weights_invalid",
                "Adjusted weight is negative.",
            )
    total = sum(Decimal(str(row["adjusted_weight"])) for row in rows)
    if abs(total - Decimal("1")) > WEIGHT_SUM_TOLERANCE:
        raise api_error(
            422,
            "persona_adjusted_weights_invalid",
            "Adjusted weights do not sum to 1.0.",
        )


def build_adjusted_weights(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not rows:
        raise api_error(
            422,
            "persona_weights_degenerate",
            "No weight rows provided.",
        )
    validate_modifier_coverage(rows)

    clamped: list[Decimal] = []
    for row in rows:
        base = Decimal(str(row["base_weight"]))
        mod = Decimal(str(row["modifier"]))
        raw = base * (Decimal("1") + mod)
        clamped.append(max(raw, Decimal("0")))

    total = sum(clamped)
    if total <= Decimal("0"):
        raise api_error(
            422,
            "persona_weights_degenerate",
            "Adjusted weights sum to zero or less after clamping.",
        )

    result: list[dict[str, Any]] = []
    for row, cl in zip(rows, clamped, strict=True):
        adjusted = cl / total
        result.append(
            {
                "metric_id": str(row["metric_id"]),
                "metric_slug": row["metric_slug"],
                "metric_name": row["metric_name"],
                "base_weight": float(row["base_weight"]),
                "modifier": float(row["modifier"]),
                "adjusted_weight": float(adjusted),
            }
        )

    ensure_adjusted_weights_valid(result)
    return result


def build_persona_weight_profile(
    conn: Connection[Any],
    scenario_slug: str,
    persona_slug: str,
    locale: str = "ru",
    version: str = DEFAULT_PERSONA_WEIGHTS_VERSION,
) -> dict[str, Any]:
    persona = personas_repository.get_persona_by_slug(
        conn, persona_slug, locale
    )
    if persona is None:
        raise api_error(
            422,
            "persona_not_found",
            "Persona not found.",
            {"persona_slug": persona_slug},
        )

    rows = personas_repository.list_persona_weight_inputs(
        conn, scenario_slug, persona_slug, version
    )
    if not rows:
        raise api_error(
            422,
            "scenario_not_found",
            "No weights found for this scenario.",
            {"scenario_slug": scenario_slug},
        )

    weights = build_adjusted_weights(rows)
    weight_sum = float(sum(Decimal(str(w["adjusted_weight"])) for w in weights))

    return {
        "persona": {
            "slug": persona["slug"],
            "name": persona["name"],
            "description": persona["description"],
            "is_active": persona["is_active"],
            "display_order": persona["display_order"],
        },
        "scenario_slug": scenario_slug,
        "version": version,
        "weights": weights,
        "weight_sum": weight_sum,
    }


def maybe_build_persona_weight_profile(
    conn: Connection[Any],
    scenario_slug: str,
    persona_slug: str | None,
    locale: str = "ru",
    version: str = DEFAULT_PERSONA_WEIGHTS_VERSION,
) -> dict[str, Any] | None:
    if not persona_slug:
        return None
    return build_persona_weight_profile(
        conn, scenario_slug, persona_slug, locale, version
    )

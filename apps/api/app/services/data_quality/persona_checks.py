from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services import persona_weights
from app.services.data_quality._issues import _check, _issue
from fastapi import HTTPException
from psycopg import Connection
from typing import Any


def _append_persona_layer_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_active_personas_missing_required_fields(connection):
        issues.append(
            _issue(
                "persona_required_fields",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing a required field.",
                row,
            )
        )
    checks.append(
        _check("persona_required_fields", issues, ["persona_required_fields"])
    )

    for row in repository.list_active_personas_missing_metric_modifiers(connection):
        issues.append(
            _issue(
                "persona_modifier_coverage",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing a CII metric modifier.",
                row,
            )
        )
    checks.append(
        _check("persona_modifier_coverage", issues, ["persona_modifier_coverage"])
    )

    for row in repository.list_persona_modifiers_out_of_range(connection):
        issues.append(
            _issue(
                "persona_modifier_range",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Persona modifier is outside the allowed range.",
                {**row, "expected_range": [-0.5, 0.5]},
            )
        )
    checks.append(_check("persona_modifier_range", issues, ["persona_modifier_range"]))

    _append_persona_adjusted_weight_issues(connection, issues)
    checks.append(
        _check(
            "persona_adjusted_weights_valid",
            issues,
            ["persona_adjusted_weights_valid"],
        )
    )

    for row in repository.list_active_personas_missing_descriptions(connection):
        issues.append(
            _issue(
                "persona_descriptions",
                "warning",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing optional description content.",
                row,
            )
        )
    checks.append(_check("persona_descriptions", issues, ["persona_descriptions"]))

    for row in repository.list_inactive_personas_with_modifiers(connection):
        issues.append(
            _issue(
                "inactive_persona_modifiers",
                "warning",
                "persona",
                row.get("persona_slug"),
                "Inactive persona still has metric modifiers.",
                row,
            )
        )
    checks.append(
        _check("inactive_persona_modifiers", issues, ["inactive_persona_modifiers"])
    )


def _append_persona_adjusted_weight_issues(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in repository.list_persona_adjusted_weight_inputs(connection):
        key = (str(row["persona_slug"]), str(row["scenario_slug"]))
        grouped.setdefault(key, []).append(row)

    for (persona_slug, scenario_slug), rows in grouped.items():
        try:
            adjusted = persona_weights.build_adjusted_weights(rows)
        except HTTPException as exc:
            error_code = "persona_adjusted_weights_invalid"
            if isinstance(exc.detail, dict):
                error_code = str(exc.detail.get("error", {}).get("code", error_code))
            issues.append(
                _issue(
                    "persona_adjusted_weights_valid",
                    "critical",
                    "persona",
                    persona_slug,
                    "Persona adjusted weights could not be built.",
                    {
                        "persona_slug": persona_slug,
                        "scenario_slug": scenario_slug,
                        "error_code": error_code,
                    },
                )
            )
            continue
        weight_sum = sum(float(row["adjusted_weight"]) for row in adjusted)
        negative = [
            row["metric_slug"] for row in adjusted if float(row["adjusted_weight"]) < 0
        ]
        if negative or abs(weight_sum - 1.0) > 0.000001:
            issues.append(
                _issue(
                    "persona_adjusted_weights_valid",
                    "critical",
                    "persona",
                    persona_slug,
                    "Persona adjusted weights are invalid.",
                    {
                        "persona_slug": persona_slug,
                        "scenario_slug": scenario_slug,
                        "error_code": "persona_adjusted_weights_invalid",
                        "weight_sum": weight_sum,
                        "negative_metric_slugs": negative,
                    },
                )
            )

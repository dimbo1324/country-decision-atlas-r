from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_methodology_config_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_missing_required_methodology_parameters(
        connection
    ):
        issues.append(
            _issue(
                "methodology_parameter_missing",
                "critical",
                "methodology_parameter",
                row.get("param_key"),
                "Active methodology version is missing a required parameter.",
                {
                    "version": row.get("version"),
                    "param_key": row.get("param_key"),
                },
            )
        )
    checks.append(
        _check(
            "methodology_active_version_complete",
            issues,
            ["methodology_parameter_missing"],
        )
    )

    for row in repository.list_methodology_parameters_out_of_range(connection):
        issues.append(
            _issue(
                "methodology_parameter_out_of_range",
                "critical",
                "methodology_parameter",
                row.get("param_key"),
                "Methodology parameter value is outside the allowed range.",
                {
                    "version": row.get("version"),
                    "param_key": row.get("param_key"),
                    "value_numeric": row.get("value_numeric"),
                    "min_value": row.get("min_value"),
                    "max_value": row.get("max_value"),
                },
            )
        )
    checks.append(
        _check(
            "methodology_numeric_parameters_in_range",
            issues,
            ["methodology_parameter_out_of_range"],
        )
    )

    for row in repository.list_invalid_methodology_threshold_order(connection):
        issues.append(
            _issue(
                "methodology_threshold_order_invalid",
                "critical",
                "methodology_parameter",
                row.get("version"),
                "Methodology thresholds are not strictly ordered.",
                dict(row),
            )
        )
    checks.append(
        _check(
            "methodology_thresholds_ordered",
            issues,
            ["methodology_threshold_order_invalid"],
        )
    )

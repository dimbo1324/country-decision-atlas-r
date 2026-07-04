from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_platform_metrics_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_invalid_platform_metric_values(connection):
        issues.append(
            _issue(
                "platform_metric_value_invalid",
                "critical",
                "platform_metric",
                row.get("id"),
                "Platform metric has invalid value, label, confidence or freshness_status.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_values_in_range",
            issues,
            ["platform_metric_value_invalid"],
        )
    )

    for row in repository.list_inconsistent_insufficient_data_metrics(
        connection
    ):
        issues.append(
            _issue(
                "platform_metric_insufficient_data_inconsistent",
                "critical",
                "platform_metric",
                row.get("id"),
                "Platform metric has inconsistent insufficient_data state (value/label mismatch).",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_insufficient_data_consistent",
            issues,
            ["platform_metric_insufficient_data_inconsistent"],
        )
    )

    for row in repository.list_platform_metrics_with_missing_methodology(
        connection
    ):
        issues.append(
            _issue(
                "platform_metric_methodology_missing",
                "critical",
                "platform_metric",
                row.get("id"),
                "Platform metric is missing methodology_version.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_have_methodology",
            issues,
            ["platform_metric_methodology_missing"],
        )
    )

    for row in repository.list_platform_metrics_with_missing_computed_at(
        connection
    ):
        issues.append(
            _issue(
                "platform_metric_computed_at_missing",
                "critical",
                "platform_metric",
                row.get("id"),
                "Platform metric is missing computed_at timestamp.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_have_computed_at",
            issues,
            ["platform_metric_computed_at_missing"],
        )
    )

    for row in repository.list_stale_platform_metrics(connection):
        issues.append(
            _issue(
                "platform_metric_stale",
                "warning",
                "platform_metric",
                row.get("id"),
                "Platform metric computed_at is older than 30 days.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_freshness",
            issues,
            ["platform_metric_stale"],
        )
    )

    for row in repository.list_high_confidence_low_sample_metrics(connection):
        issues.append(
            _issue(
                "platform_metric_high_confidence_low_sample",
                "warning",
                "platform_metric",
                row.get("id"),
                "Platform metric claims high confidence with very few input signals.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_confidence_sample_consistency",
            issues,
            ["platform_metric_high_confidence_low_sample"],
        )
    )

    for row in repository.list_mvp_countries_missing_global_platform_metrics(
        connection
    ):
        issues.append(
            _issue(
                "platform_metric_global_missing",
                "warning",
                "platform_metric",
                None,
                "MVP country is missing global platform metrics (LVI or contradiction score).",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_completeness",
            issues,
            ["platform_metric_global_missing"],
        )
    )

    for row in repository.list_mvp_countries_missing_scenario_risk_metrics(
        connection
    ):
        issues.append(
            _issue(
                "platform_metric_scenario_missing",
                "warning",
                "platform_metric",
                None,
                "MVP country is missing scenario-specific risk score for an active MVP scenario.",
                row,
            )
        )
    checks.append(
        _check(
            "platform_metrics_scenario_completeness",
            issues,
            ["platform_metric_scenario_missing"],
        )
    )

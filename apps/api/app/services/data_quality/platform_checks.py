from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from app.services.data_quality.platform_metrics_checks import (
    _append_platform_metrics_checks,
)
from psycopg import Connection
from typing import Any


def _append_platform_runtime_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_enabled_feature_flags_without_access_rules(
        connection
    ):
        issues.append(
            _issue(
                "enabled_feature_flag_without_access_rule",
                "critical",
                "feature_flag",
                row.get("key"),
                "Enabled feature flag has no access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "enabled_feature_flags_have_access_rules",
            issues,
            ["enabled_feature_flag_without_access_rule"],
        )
    )
    for row in repository.list_disabled_feature_flags_without_access_rules(
        connection
    ):
        issues.append(
            _issue(
                "disabled_feature_flag_without_access_rule",
                "warning",
                "feature_flag",
                row.get("key"),
                "Disabled feature flag has no access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "feature_flags_have_valid_access_rules",
            issues,
            ["disabled_feature_flag_without_access_rule"],
        )
    )
    for row in repository.list_data_journal_events_with_internal_payload_fields(
        connection
    ):
        issues.append(
            _issue(
                "data_journal_internal_payload_field",
                "critical",
                "domain_event",
                row.get("id"),
                "Data journal source event contains internal payload fields.",
                row,
            )
        )
    checks.append(
        _check(
            "data_journal_does_not_expose_internal_fields",
            issues,
            ["data_journal_internal_payload_field"],
        )
    )
    for (
        row
    ) in repository.list_data_journal_events_referencing_non_public_content(
        connection
    ):
        issues.append(
            _issue(
                "data_journal_non_public_reference",
                "critical",
                "domain_event",
                row.get("id"),
                "Data journal source event references non-public content.",
                row,
            )
        )
    checks.append(
        _check(
            "data_journal_entries_reference_public_content",
            issues,
            ["data_journal_non_public_reference"],
        )
    )
    checks.append(_check("cache_config_is_safe", issues, []))
    _append_platform_metrics_checks(connection, issues, checks)

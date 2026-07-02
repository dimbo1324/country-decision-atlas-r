from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_ai_foundation_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_missing_ai_feature_flags(connection):
        issues.append(
            _issue(
                "ai_feature_flag_missing",
                "critical",
                "feature_flag",
                row.get("feature_key"),
                "Required AI feature flag is missing.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_feature_flags_exist",
            issues,
            ["ai_feature_flag_missing"],
        )
    )
    for row in repository.list_ai_feature_flags_without_public_access_rules(connection):
        issues.append(
            _issue(
                "ai_feature_flag_public_access_rule_missing",
                "critical",
                "feature_flag",
                row.get("feature_key"),
                "AI feature flag has no public access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_feature_flags_have_public_access_rules",
            issues,
            ["ai_feature_flag_public_access_rule_missing"],
        )
    )
    for row in repository.list_ai_logs_with_forbidden_metadata_keys(connection):
        issues.append(
            _issue(
                "ai_log_forbidden_metadata_key",
                "critical",
                "ai_interaction_log",
                row.get("id"),
                "AI interaction log metadata contains a forbidden key.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_logs_do_not_store_forbidden_metadata_keys",
            issues,
            ["ai_log_forbidden_metadata_key"],
        )
    )

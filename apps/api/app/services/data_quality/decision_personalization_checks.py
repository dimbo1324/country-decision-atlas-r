from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_decision_personalization_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_decision_personalization_feature_flag_mismatches(
        connection
    ):
        issues.append(
            _issue(
                "decision_personalization_feature_flag_invalid",
                "critical",
                "feature_flag",
                row.get("feature_key"),
                "Decision personalization feature flag is not publicly enabled.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_personalization_feature_flags_enabled",
            issues,
            ["decision_personalization_feature_flag_invalid"],
        )
    )
    for row in repository.list_decision_scores_missing_required_criteria(connection):
        issues.append(
            _issue(
                "decision_score_required_criterion_missing",
                "critical",
                "country_score",
                None,
                "Decision score is missing a required personalization criterion.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_scores_include_personalization_criteria",
            issues,
            ["decision_score_required_criterion_missing"],
        )
    )
    for row in repository.list_decision_wizard_rule_mismatches(connection):
        issues.append(
            _issue(
                "decision_wizard_dependency_missing",
                "critical",
                "decision_wizard",
                row.get("dependency_slug"),
                "Decision wizard rule references a missing active dependency.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_wizard_rules_have_active_dependencies",
            issues,
            ["decision_wizard_dependency_missing"],
        )
    )

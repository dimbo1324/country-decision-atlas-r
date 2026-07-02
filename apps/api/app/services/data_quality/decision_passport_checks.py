from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_decision_passport_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_active_passports_missing_scenario_slug(connection):
        issues.append(
            _issue(
                "decision_passport_missing_scenario_slug",
                "critical",
                "decision_passport",
                row.get("id"),
                "Active decision passport is missing scenario_slug.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passports_have_scenario_slug",
            issues,
            ["decision_passport_missing_scenario_slug"],
        )
    )

    for row in repository.list_active_passports_with_empty_candidates(connection):
        issues.append(
            _issue(
                "decision_passport_empty_candidates",
                "critical",
                "decision_passport",
                row.get("id"),
                "Active decision passport has an empty candidate country list.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passports_have_candidates",
            issues,
            ["decision_passport_empty_candidates"],
        )
    )

    for row in repository.list_active_passports_with_empty_result_snapshot(connection):
        issues.append(
            _issue(
                "decision_passport_empty_result_snapshot",
                "critical",
                "decision_passport",
                row.get("id"),
                "Active decision passport has no decision result snapshot.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passports_have_result_snapshot",
            issues,
            ["decision_passport_empty_result_snapshot"],
        )
    )

    for row in repository.list_active_passports_with_selected_country_not_in_candidates(
        connection
    ):
        issues.append(
            _issue(
                "decision_passport_selected_country_not_candidate",
                "critical",
                "decision_passport",
                row.get("id"),
                "Active decision passport selected_country_slug is not part of candidate_country_slugs.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passport_selected_country_is_candidate",
            issues,
            ["decision_passport_selected_country_not_candidate"],
        )
    )

    for row in repository.list_passports_with_inconsistent_expiry_status(connection):
        issues.append(
            _issue(
                "decision_passport_expiry_status_inconsistent",
                "warning",
                "decision_passport",
                row.get("id"),
                "Decision passport is past expires_at but still marked active.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passport_expiry_status_consistent",
            issues,
            ["decision_passport_expiry_status_inconsistent"],
        )
    )

    for row in repository.list_active_passports_without_sources(connection):
        issues.append(
            _issue(
                "decision_passport_missing_sources",
                "warning",
                "decision_passport",
                row.get("id"),
                "Active decision passport has no linked sources.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passports_have_sources",
            issues,
            ["decision_passport_missing_sources"],
        )
    )

    for row in repository.list_old_active_passports_without_expires_at(connection):
        issues.append(
            _issue(
                "decision_passport_old_without_expiry",
                "warning",
                "decision_passport",
                row.get("id"),
                "Active decision passport older than 30 days has no expires_at.",
                row,
            )
        )
    checks.append(
        _check(
            "decision_passports_old_have_expiry",
            issues,
            ["decision_passport_old_without_expiry"],
        )
    )

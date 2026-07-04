from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_country_drift_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_active_countries_missing_drift_snapshots(
        connection
    ):
        issues.append(
            _issue(
                "drift_missing_for_active_country",
                "critical",
                "country_drift_snapshot",
                None,
                "Active country has no country drift snapshot.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_snapshots_exist_for_active_countries",
            issues,
            ["drift_missing_for_active_country"],
        )
    )

    for row in repository.list_invalid_drift_snapshot_values(connection):
        issues.append(
            _issue(
                "drift_value_invalid",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot has invalid label, confidence, or net_score.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_snapshot_values_valid",
            issues,
            ["drift_value_invalid"],
        )
    )

    for row in repository.list_drift_snapshots_insufficient_data_inconsistent(
        connection
    ):
        issues.append(
            _issue(
                "drift_insufficient_data_inconsistent",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot label is inconsistent with event_count/total_weight.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_insufficient_data_consistent",
            issues,
            ["drift_insufficient_data_inconsistent"],
        )
    )

    for (
        row
    ) in repository.list_drift_snapshots_insufficient_data_with_high_confidence(
        connection
    ):
        issues.append(
            _issue(
                "drift_insufficient_data_confidence_mismatch",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot marked insufficient_data must have low confidence.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_insufficient_data_has_low_confidence",
            issues,
            ["drift_insufficient_data_confidence_mismatch"],
        )
    )

    for row in repository.list_drift_snapshots_missing_methodology_version(
        connection
    ):
        issues.append(
            _issue(
                "drift_methodology_version_missing",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot is missing methodology_version.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_snapshots_have_methodology_version",
            issues,
            ["drift_methodology_version_missing"],
        )
    )

    for row in repository.list_drift_snapshots_missing_computed_at(connection):
        issues.append(
            _issue(
                "drift_computed_at_missing",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot is missing computed_at timestamp.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_snapshots_have_computed_at",
            issues,
            ["drift_computed_at_missing"],
        )
    )

    for row in repository.list_drift_snapshots_with_non_object_input_summary(
        connection
    ):
        issues.append(
            _issue(
                "drift_input_summary_not_object",
                "critical",
                "country_drift_snapshot",
                row.get("id"),
                "Country drift snapshot input_summary is not a JSON object.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_input_summary_is_object",
            issues,
            ["drift_input_summary_not_object"],
        )
    )

    for row in repository.list_duplicate_drift_changed_event_keys(connection):
        issues.append(
            _issue(
                "drift_changed_event_key_duplicate",
                "critical",
                "domain_event",
                row.get("event_key"),
                "drift.changed domain event_key is not unique.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_changed_event_keys_unique",
            issues,
            ["drift_changed_event_key_duplicate"],
        )
    )

    for row in repository.list_drift_changed_events_missing_payload_fields(
        connection
    ):
        issues.append(
            _issue(
                "drift_changed_payload_incomplete",
                "critical",
                "domain_event",
                row.get("id"),
                "drift.changed domain event payload is missing previous_label or new_label.",
                row,
            )
        )
    checks.append(
        _check(
            "drift_changed_payload_complete",
            issues,
            ["drift_changed_payload_incomplete"],
        )
    )

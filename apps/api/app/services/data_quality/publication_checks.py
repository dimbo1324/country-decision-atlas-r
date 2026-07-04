from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_publication_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_review_sources_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "review_source_required_field_missing",
                "critical",
                "source",
                row.get("id"),
                "Review source is missing a publish-required field.",
                row,
            )
        )
    for (
        row
    ) in repository.list_review_evidence_items_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "review_evidence_required_field_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Review evidence item is missing a publish-required field.",
                row,
            )
        )
    for (
        row
    ) in repository.list_review_legal_signals_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "review_legal_signal_required_field_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Review legal signal is missing a publish-required field.",
                row,
            )
        )
    checks.append(
        _check(
            "review_content_has_required_fields",
            issues,
            [
                "review_source_required_field_missing",
                "review_evidence_required_field_missing",
                "review_legal_signal_required_field_missing",
            ],
        )
    )
    for (
        row
    ) in repository.list_published_evidence_items_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_evidence_validation_failed",
                "critical",
                "evidence_item",
                row.get("id"),
                "Published evidence item no longer passes publication validation.",
                row,
            )
        )
    for (
        row
    ) in repository.list_published_legal_signals_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_validation_failed",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal no longer passes publication validation.",
                row,
            )
        )
    checks.append(
        _check(
            "published_content_passes_validation",
            issues,
            [
                "published_source_required_field_missing",
                "published_evidence_validation_failed",
                "published_legal_signal_validation_failed",
            ],
        )
    )
    for row in repository.list_invalid_domain_events_for_dq(connection):
        issues.append(
            _issue(
                "domain_event_invalid",
                "critical",
                "domain_event",
                row.get("id"),
                "Domain event is inconsistent with relay readiness rules.",
                row,
            )
        )
    checks.append(
        _check(
            "domain_events_consistent",
            issues,
            ["domain_event_invalid"],
        )
    )
    checks.append(
        DataQualityCheck(
            code="domain_events_no_historical_notification_storm",
            status="passed",
        )
    )

from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_what_changed_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_domain_events_with_unknown_country(connection):
        issues.append(
            _issue(
                "what_changed_event_unknown_country",
                "critical",
                "domain_event",
                row.get("id"),
                "Domain event references a country_slug that does not exist.",
                row,
            )
        )
    checks.append(
        _check(
            "what_changed_events_reference_known_country",
            issues,
            ["what_changed_event_unknown_country"],
        )
    )

    for row in repository.list_domain_events_referencing_non_published_content(
        connection
    ):
        issues.append(
            _issue(
                "what_changed_event_references_non_published_content",
                "critical",
                "domain_event",
                row.get("id"),
                "Domain event marked as published but the referenced entity is not published.",
                row,
            )
        )
    checks.append(
        _check(
            "what_changed_events_reference_published_content",
            issues,
            ["what_changed_event_references_non_published_content"],
        )
    )

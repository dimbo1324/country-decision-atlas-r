from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_timeline_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_legal_signals_without_timeline_event(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_timeline_event_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no timeline event.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_timeline_events",
            issues,
            ["published_legal_signal_timeline_event_missing"],
        )
    )
    timeline_checks = [
        (
            repository.list_timeline_events_with_invalid_date,
            "timeline_event_date_invalid",
            "critical",
            "Timeline event must have an event date.",
        ),
        (
            repository.list_timeline_events_with_invalid_impact_direction,
            "timeline_event_impact_direction_invalid",
            "critical",
            "Timeline event has an invalid impact direction.",
        ),
        (
            repository.list_timeline_events_with_invalid_impact_level,
            "timeline_event_impact_level_invalid",
            "critical",
            "Timeline event has an invalid impact level.",
        ),
        (
            repository.list_timeline_events_with_country_mismatch,
            "timeline_event_country_mismatch",
            "critical",
            "Timeline event country differs from its legal signal country.",
        ),
        (
            repository.list_timeline_events_without_traceability,
            "timeline_event_traceability_missing",
            "warning",
            "Timeline event has neither source nor evidence.",
        ),
        (
            repository.list_unplanned_future_timeline_events,
            "timeline_event_future_date",
            "critical",
            "Timeline event date is in the future.",
        ),
    ]
    timeline_codes: list[str] = []
    for query, code, severity, message in timeline_checks:
        timeline_codes.append(code)
        for row in query(connection):
            issues.append(
                _issue(
                    code,
                    severity,
                    "legal_signal_event",
                    row.get("id"),
                    message,
                    row,
                )
            )
    checks.append(
        _check("legal_signal_timeline_is_valid", issues, timeline_codes)
    )
    for row in repository.list_mvp_countries_without_legal_events(connection):
        issues.append(
            _issue(
                "legal_timeline_no_events_for_country",
                "critical",
                "country",
                None,
                "MVP country has no legal signal timeline events.",
                row,
            )
        )
    checks.append(
        _check(
            "legal_timeline_has_events_per_country",
            issues,
            ["legal_timeline_no_events_for_country"],
        )
    )

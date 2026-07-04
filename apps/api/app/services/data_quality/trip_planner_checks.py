from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_trip_planner_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_trips_with_invalid_share_state(connection):
        issues.append(
            _issue(
                "trip_share_state_invalid",
                "critical",
                "trip",
                row.get("id"),
                "Trip share visibility and token fields must stay consistent.",
                row,
            )
        )
    checks.append(
        _check(
            "trip_share_tokens_are_private_and_consistent",
            issues,
            ["trip_share_state_invalid"],
        )
    )

    for row in repository.list_reminders_with_invalid_trip_or_item(connection):
        issues.append(
            _issue(
                "trip_reminder_invalid_checklist_item",
                "critical",
                "trip_reminder",
                row.get("id"),
                "Trip reminder checklist item must belong to the same trip.",
                row,
            )
        )
    checks.append(
        _check(
            "trip_reminders_reference_same_trip_items",
            issues,
            ["trip_reminder_invalid_checklist_item"],
        )
    )

    for row in repository.list_trip_waypoints_with_invalid_position(connection):
        issues.append(
            _issue(
                "trip_waypoint_position_invalid",
                "critical",
                "trip_waypoint",
                row.get("trip_id"),
                "Trip waypoint positions must be positive and unique per trip.",
                row,
            )
        )
    checks.append(
        _check(
            "trip_waypoint_positions_are_valid",
            issues,
            ["trip_waypoint_position_invalid"],
        )
    )

from app.core.errors import api_error
from app.repositories import domain_events, trip_planner as repository
from app.schemas.trip_planner import (
    TripReminder,
    TripReminderCreateRequest,
)
from app.services.trip_planner import helpers
from datetime import UTC, datetime
from psycopg import Connection
from typing import Any
from uuid import UUID


def list_reminders(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> list[TripReminder]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    return [
        helpers.reminder_model(row)
        for row in repository.list_reminders(connection, trip_id)
    ]


def create_reminder(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripReminderCreateRequest,
) -> TripReminder:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    if payload.checklist_item_id is not None:
        item = repository.get_checklist_item_for_trip(
            connection, trip_id=trip_id, item_id=payload.checklist_item_id
        )
        if item is None:
            raise api_error(
                422,
                "checklist_item_not_in_trip",
                "Reminder checklist item must belong to this trip.",
                {},
            )
    row = repository.create_reminder(
        connection,
        trip_id=trip_id,
        checklist_item_id=payload.checklist_item_id,
        remind_at=payload.remind_at,
        channel=payload.channel,
    )
    return helpers.reminder_model(row)


def cancel_reminder(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    reminder_id: str,
) -> TripReminder:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    row = repository.cancel_reminder(
        connection, reminder_id=reminder_id, trip_id=trip_id
    )
    if row is None:
        raise api_error(
            404, "reminder_not_found", "Trip reminder was not found.", {}
        )
    return helpers.reminder_model(row)


def dispatch_due_reminders(
    connection: Connection[Any], *, now: datetime, limit: int
) -> dict[str, Any]:
    rows = repository.list_due_reminders(connection, now=now, limit=limit)
    inserted = 0
    for row in rows:
        country_slug = row.get("country_slug") or "unknown"
        event = domain_events.insert_domain_event(
            connection,
            event_key=f"trip_reminder:{row['id']}",
            event_type="trip_reminder_due",
            aggregate_type="trip_reminder",
            aggregate_id=UUID(str(row["id"])),
            country_slug=str(country_slug),
            payload={
                "reminder_id": row["id"],
                "trip_id": row["trip_id"],
                "user_id": row["user_id"],
                "title": row.get("checklist_item_title")
                or row.get("trip_title")
                or "Trip reminder",
                "trip_title": row.get("trip_title"),
                "checklist_item_id": row.get("checklist_item_id"),
                "remind_at": row["remind_at"],
                "channel": row["channel"],
            },
            notifiable=True,
        )
        if event is not None:
            inserted += 1
        repository.mark_reminder_sent(connection, row["id"], datetime.now(UTC))
    return {
        "due_reminders": len(rows),
        "events_inserted": inserted,
    }

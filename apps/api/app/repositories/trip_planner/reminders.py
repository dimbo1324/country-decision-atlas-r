from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from typing import Any


REMINDER_FIELDS = """
    tr.id::text AS id,
    tr.trip_id::text AS trip_id,
    tr.checklist_item_id::text AS checklist_item_id,
    tci.title AS checklist_item_title,
    tr.remind_at,
    tr.channel,
    tr.status,
    tr.sent_at,
    tr.created_at,
    tr.updated_at
"""


def list_reminders(
    connection: Connection[Any], trip_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {REMINDER_FIELDS}
        FROM trip_reminders tr
        LEFT JOIN trip_checklist_items tci ON tci.id = tr.checklist_item_id
        WHERE tr.trip_id = %s::uuid
        ORDER BY tr.remind_at, tr.created_at
        """,
        (trip_id,),
    )


def get_reminder_for_trip(
    connection: Connection[Any], *, trip_id: str, reminder_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {REMINDER_FIELDS}
        FROM trip_reminders tr
        LEFT JOIN trip_checklist_items tci ON tci.id = tr.checklist_item_id
        WHERE tr.trip_id = %s::uuid AND tr.id = %s::uuid
        """,
        (trip_id, reminder_id),
    )


def create_reminder(
    connection: Connection[Any],
    *,
    trip_id: str,
    checklist_item_id: str | None,
    remind_at: datetime,
    channel: str,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO trip_reminders (
            trip_id,
            checklist_item_id,
            remind_at,
            channel
        )
        VALUES (%s::uuid, %s::uuid, %s, %s)
        RETURNING id::text AS id
        """,
        (trip_id, checklist_item_id, remind_at, channel),
    )
    reminder = get_reminder_for_trip(
        connection, trip_id=trip_id, reminder_id=row["id"]
    )
    assert reminder is not None
    return reminder


def cancel_reminder(
    connection: Connection[Any],
    *,
    reminder_id: str,
    trip_id: str,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trip_reminders
        SET status = 'cancelled'
        WHERE id = %s::uuid
          AND trip_id = %s::uuid
          AND status = 'scheduled'
        RETURNING id::text AS id
        """,
        (reminder_id, trip_id),
    )
    if row is None:
        return None
    return get_reminder_for_trip(
        connection, trip_id=trip_id, reminder_id=row["id"]
    )


def list_due_reminders(
    connection: Connection[Any], *, now: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        WITH due AS (
            SELECT tr.id
            FROM trip_reminders tr
            WHERE tr.status = 'scheduled'
              AND tr.remind_at <= %s
            ORDER BY tr.remind_at ASC
            LIMIT %s
            FOR UPDATE OF tr SKIP LOCKED
        )
        SELECT
            tr.id::text AS id,
            tr.trip_id::text AS trip_id,
            tr.checklist_item_id::text AS checklist_item_id,
            tr.remind_at,
            tr.channel,
            t.user_id::text AS user_id,
            t.title AS trip_title,
            tci.title AS checklist_item_title,
            COALESCE(wc.slug, oc.slug) AS country_slug
        FROM due
        JOIN trip_reminders tr ON tr.id = due.id
        JOIN trips t ON t.id = tr.trip_id
        LEFT JOIN trip_checklist_items tci ON tci.id = tr.checklist_item_id
        LEFT JOIN countries oc ON oc.id = t.origin_country_id
        LEFT JOIN LATERAL (
            SELECT c.slug
            FROM trip_waypoints tw
            JOIN countries c ON c.id = tw.country_id
            WHERE tw.trip_id = t.id
            ORDER BY tw.position ASC
            LIMIT 1
        ) wc ON TRUE
        ORDER BY tr.remind_at ASC
        """,
        (now, limit),
    )


def mark_reminder_sent(
    connection: Connection[Any], reminder_id: str, sent_at: datetime
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE trip_reminders
        SET status = 'sent', sent_at = %s
        WHERE id = %s::uuid AND status = 'scheduled'
        RETURNING id::text AS id
        """,
        (sent_at, reminder_id),
    )

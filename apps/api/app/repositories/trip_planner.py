from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from typing import Any


TRIP_FIELDS = """
    t.id::text AS id,
    t.user_id::text AS user_id,
    t.title,
    t.scenario_slug,
    t.origin_country_id::text AS origin_country_id,
    oc.slug AS origin_country_slug,
    oc.name AS origin_country_name,
    t.status,
    t.confidence_tier,
    t.visibility,
    t.share_token_prefix,
    t.created_at,
    t.updated_at,
    t.completed_at
"""

WAYPOINT_FIELDS = """
    tw.id::text AS id,
    tw.trip_id::text AS trip_id,
    tw.position,
    tw.country_id::text AS country_id,
    c.slug AS country_slug,
    c.name AS country_name,
    c.iso2 AS country_iso2,
    tw.city,
    tw.kind,
    tw.planned_from,
    tw.planned_to,
    tw.notes,
    tw.created_at,
    tw.updated_at
"""

CHECKLIST_FIELDS = """
    tci.id::text AS id,
    tci.trip_id::text AS trip_id,
    tci.waypoint_id::text AS waypoint_id,
    tci.title,
    tci.description,
    tci.due_date,
    tci.status,
    tci.origin_kind,
    tci.origin_ref::text AS origin_ref,
    tci.position,
    tci.created_at,
    tci.updated_at
"""

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

ANNOTATION_FIELDS = """
    ta.id::text AS id,
    ta.trip_id::text AS trip_id,
    ta.waypoint_id::text AS waypoint_id,
    ta.kind,
    ta.body,
    ta.position,
    ta.created_at,
    ta.updated_at
"""


def list_user_trips(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {TRIP_FIELDS}
        FROM trips t
        LEFT JOIN countries oc ON oc.id = t.origin_country_id
        WHERE t.user_id::text = %s
        ORDER BY t.updated_at DESC, t.created_at DESC
        """,
        (user_id,),
    )


def get_trip_for_user(
    connection: Connection[Any], trip_id: str, user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {TRIP_FIELDS}
        FROM trips t
        LEFT JOIN countries oc ON oc.id = t.origin_country_id
        WHERE t.id::text = %s AND t.user_id::text = %s
        """,
        (trip_id, user_id),
    )


def get_trip_by_share_token_hash(
    connection: Connection[Any], token_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {TRIP_FIELDS}
        FROM trips t
        LEFT JOIN countries oc ON oc.id = t.origin_country_id
        WHERE t.share_token_hash = %s
          AND t.visibility = 'link'
        """,
        (token_hash,),
    )


def create_trip(
    connection: Connection[Any],
    *,
    user_id: str,
    title: str,
    scenario_slug: str | None,
    origin_country_id: str | None,
    status: str,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO trips (
            user_id,
            title,
            scenario_slug,
            origin_country_id,
            status
        )
        VALUES (%s::uuid, %s, %s, %s::uuid, %s)
        RETURNING id::text AS id
        """,
        (user_id, title, scenario_slug, origin_country_id, status),
    )
    trip = get_trip_for_user(connection, row["id"], user_id)
    assert trip is not None
    return trip


def update_trip(
    connection: Connection[Any],
    *,
    trip_id: str,
    user_id: str,
    title: str,
    scenario_slug: str | None,
    origin_country_id: str | None,
    status: str,
    confidence_tier: str,
    completed_at: datetime | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trips
        SET
            title = %s,
            scenario_slug = %s,
            origin_country_id = %s::uuid,
            status = %s,
            confidence_tier = %s,
            completed_at = %s
        WHERE id::text = %s AND user_id::text = %s
        RETURNING id::text AS id
        """,
        (
            title,
            scenario_slug,
            origin_country_id,
            status,
            confidence_tier,
            completed_at,
            trip_id,
            user_id,
        ),
    )
    return get_trip_for_user(connection, row["id"], user_id) if row else None


def delete_trip(
    connection: Connection[Any], *, trip_id: str, user_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        DELETE FROM trips
        WHERE id::text = %s AND user_id::text = %s
        RETURNING id
        """,
        (trip_id, user_id),
    )
    return row is not None


def enable_trip_share(
    connection: Connection[Any],
    *,
    trip_id: str,
    user_id: str,
    token_hash: str,
    token_prefix: str,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trips
        SET
            visibility = 'link',
            share_token_hash = %s,
            share_token_prefix = %s
        WHERE id::text = %s AND user_id::text = %s
        RETURNING id::text AS id
        """,
        (token_hash, token_prefix, trip_id, user_id),
    )
    return get_trip_for_user(connection, row["id"], user_id) if row else None


def disable_trip_share(
    connection: Connection[Any], *, trip_id: str, user_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trips
        SET
            visibility = 'private',
            share_token_hash = NULL,
            share_token_prefix = NULL
        WHERE id::text = %s AND user_id::text = %s
        RETURNING id::text AS id
        """,
        (trip_id, user_id),
    )
    return get_trip_for_user(connection, row["id"], user_id) if row else None


def list_waypoints(
    connection: Connection[Any], trip_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {WAYPOINT_FIELDS}
        FROM trip_waypoints tw
        JOIN countries c ON c.id = tw.country_id
        WHERE tw.trip_id::text = %s
        ORDER BY tw.position, tw.created_at
        """,
        (trip_id,),
    )


def get_waypoint_for_trip(
    connection: Connection[Any], *, trip_id: str, waypoint_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {WAYPOINT_FIELDS}
        FROM trip_waypoints tw
        JOIN countries c ON c.id = tw.country_id
        WHERE tw.trip_id::text = %s AND tw.id::text = %s
        """,
        (trip_id, waypoint_id),
    )


def next_waypoint_position(connection: Connection[Any], trip_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COALESCE(MAX(position), 0) + 1 AS next_position
        FROM trip_waypoints
        WHERE trip_id::text = %s
        """,
        (trip_id,),
    )
    return int(row["next_position"]) if row else 1


def create_waypoint(
    connection: Connection[Any],
    *,
    trip_id: str,
    position: int,
    country_id: str,
    city: str | None,
    kind: str,
    planned_from: Any | None,
    planned_to: Any | None,
    notes: str | None,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO trip_waypoints (
            trip_id,
            position,
            country_id,
            city,
            kind,
            planned_from,
            planned_to,
            notes
        )
        VALUES (%s::uuid, %s, %s::uuid, %s, %s, %s, %s, %s)
        RETURNING id::text AS id
        """,
        (
            trip_id,
            position,
            country_id,
            city,
            kind,
            planned_from,
            planned_to,
            notes,
        ),
    )
    waypoint = get_waypoint_for_trip(
        connection, trip_id=trip_id, waypoint_id=row["id"]
    )
    assert waypoint is not None
    return waypoint


def update_waypoint(
    connection: Connection[Any],
    *,
    waypoint_id: str,
    trip_id: str,
    position: int,
    country_id: str,
    city: str | None,
    kind: str,
    planned_from: Any | None,
    planned_to: Any | None,
    notes: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trip_waypoints
        SET
            position = %s,
            country_id = %s::uuid,
            city = %s,
            kind = %s,
            planned_from = %s,
            planned_to = %s,
            notes = %s
        WHERE id::text = %s AND trip_id::text = %s
        RETURNING id::text AS id
        """,
        (
            position,
            country_id,
            city,
            kind,
            planned_from,
            planned_to,
            notes,
            waypoint_id,
            trip_id,
        ),
    )
    if row is None:
        return None
    return get_waypoint_for_trip(
        connection, trip_id=trip_id, waypoint_id=row["id"]
    )


def delete_waypoint(
    connection: Connection[Any], *, trip_id: str, waypoint_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        DELETE FROM trip_waypoints
        WHERE trip_id::text = %s AND id::text = %s
        RETURNING id
        """,
        (trip_id, waypoint_id),
    )
    return row is not None


def set_waypoint_position(
    connection: Connection[Any],
    *,
    waypoint_id: str,
    trip_id: str,
    position: int,
) -> None:
    connection.execute(
        """
        UPDATE trip_waypoints
        SET position = %s
        WHERE id::text = %s AND trip_id::text = %s
        """,
        (position, waypoint_id, trip_id),
    )


def list_checklist_items(
    connection: Connection[Any], trip_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {CHECKLIST_FIELDS}
        FROM trip_checklist_items tci
        WHERE tci.trip_id::text = %s
        ORDER BY tci.position, tci.created_at
        """,
        (trip_id,),
    )


def get_checklist_item_for_trip(
    connection: Connection[Any], *, trip_id: str, item_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {CHECKLIST_FIELDS}
        FROM trip_checklist_items tci
        WHERE tci.trip_id::text = %s AND tci.id::text = %s
        """,
        (trip_id, item_id),
    )


def next_checklist_position(connection: Connection[Any], trip_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COALESCE(MAX(position), 0) + 1 AS next_position
        FROM trip_checklist_items
        WHERE trip_id::text = %s
        """,
        (trip_id,),
    )
    return int(row["next_position"]) if row else 1


def create_checklist_item(
    connection: Connection[Any],
    *,
    trip_id: str,
    waypoint_id: str | None,
    title: str,
    description: str | None,
    due_date: Any | None,
    status: str,
    origin_kind: str,
    origin_ref: str | None,
    position: int,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO trip_checklist_items (
            trip_id,
            waypoint_id,
            title,
            description,
            due_date,
            status,
            origin_kind,
            origin_ref,
            position
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s)
        RETURNING id::text AS id
        """,
        (
            trip_id,
            waypoint_id,
            title,
            description,
            due_date,
            status,
            origin_kind,
            origin_ref,
            position,
        ),
    )
    item = get_checklist_item_for_trip(
        connection, trip_id=trip_id, item_id=row["id"]
    )
    assert item is not None
    return item


def update_checklist_item(
    connection: Connection[Any],
    *,
    item_id: str,
    trip_id: str,
    waypoint_id: str | None,
    title: str,
    description: str | None,
    due_date: Any | None,
    status: str,
    position: int,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trip_checklist_items
        SET
            waypoint_id = %s::uuid,
            title = %s,
            description = %s,
            due_date = %s,
            status = %s,
            position = %s
        WHERE id::text = %s AND trip_id::text = %s
        RETURNING id::text AS id
        """,
        (
            waypoint_id,
            title,
            description,
            due_date,
            status,
            position,
            item_id,
            trip_id,
        ),
    )
    if row is None:
        return None
    return get_checklist_item_for_trip(
        connection, trip_id=trip_id, item_id=row["id"]
    )


def delete_checklist_item(
    connection: Connection[Any], *, trip_id: str, item_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        DELETE FROM trip_checklist_items
        WHERE trip_id::text = %s AND id::text = %s
        RETURNING id
        """,
        (trip_id, item_id),
    )
    return row is not None


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
        WHERE tr.trip_id::text = %s
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
        WHERE tr.trip_id::text = %s AND tr.id::text = %s
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
        WHERE id::text = %s
          AND trip_id::text = %s
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
        WHERE id::text = %s AND status = 'scheduled'
        RETURNING id::text AS id
        """,
        (sent_at, reminder_id),
    )


def list_annotations(
    connection: Connection[Any], trip_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {ANNOTATION_FIELDS}
        FROM trip_annotations ta
        WHERE ta.trip_id::text = %s
        ORDER BY ta.position NULLS LAST, ta.created_at
        """,
        (trip_id,),
    )


def get_annotation_for_trip(
    connection: Connection[Any], *, trip_id: str, annotation_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {ANNOTATION_FIELDS}
        FROM trip_annotations ta
        WHERE ta.trip_id::text = %s AND ta.id::text = %s
        """,
        (trip_id, annotation_id),
    )


def create_annotation(
    connection: Connection[Any],
    *,
    trip_id: str,
    waypoint_id: str | None,
    kind: str,
    body: str,
    position: int | None,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO trip_annotations (
            trip_id,
            waypoint_id,
            kind,
            body,
            position
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s)
        RETURNING id::text AS id
        """,
        (trip_id, waypoint_id, kind, body, position),
    )
    annotation = get_annotation_for_trip(
        connection, trip_id=trip_id, annotation_id=row["id"]
    )
    assert annotation is not None
    return annotation


def update_annotation(
    connection: Connection[Any],
    *,
    annotation_id: str,
    trip_id: str,
    waypoint_id: str | None,
    kind: str,
    body: str,
    position: int | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE trip_annotations
        SET
            waypoint_id = %s::uuid,
            kind = %s,
            body = %s,
            position = %s
        WHERE id::text = %s AND trip_id::text = %s
        RETURNING id::text AS id
        """,
        (waypoint_id, kind, body, position, annotation_id, trip_id),
    )
    if row is None:
        return None
    return get_annotation_for_trip(
        connection, trip_id=trip_id, annotation_id=row["id"]
    )


def delete_annotation(
    connection: Connection[Any], *, trip_id: str, annotation_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        DELETE FROM trip_annotations
        WHERE trip_id::text = %s AND id::text = %s
        RETURNING id
        """,
        (trip_id, annotation_id),
    )
    return row is not None


def list_published_legal_signals_for_country_slugs(
    connection: Connection[Any], country_slugs: list[str]
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id::text AS id,
            c.slug AS country_slug,
            ls.title,
            ls.summary,
            ls.signal_type,
            ls.severity,
            ls.impact_level,
            ls.source_id::text AS source_id
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = ANY(%s)
          AND ls.status = 'published'
        ORDER BY c.slug, ls.published_at DESC NULLS LAST, ls.updated_at DESC
        """,
        (country_slugs,),
    )

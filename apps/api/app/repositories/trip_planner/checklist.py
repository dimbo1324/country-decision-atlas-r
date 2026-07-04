from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


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

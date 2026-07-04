from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


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

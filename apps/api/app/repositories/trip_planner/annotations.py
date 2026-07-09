from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


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


def list_annotations(
    connection: Connection[Any], trip_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {ANNOTATION_FIELDS}
        FROM trip_annotations ta
        WHERE ta.trip_id = %s::uuid
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
        WHERE ta.trip_id = %s::uuid AND ta.id = %s::uuid
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
        WHERE id = %s::uuid AND trip_id = %s::uuid
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
        WHERE trip_id = %s::uuid AND id = %s::uuid
        RETURNING id
        """,
        (trip_id, annotation_id),
    )
    return row is not None

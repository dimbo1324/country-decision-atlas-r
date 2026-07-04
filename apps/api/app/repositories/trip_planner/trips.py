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

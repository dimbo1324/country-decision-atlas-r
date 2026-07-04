from app.core.database import fetch_one
from app.repositories.trip_planner import trips
from psycopg import Connection
from typing import Any


def get_trip_by_share_token_hash(
    connection: Connection[Any], token_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {trips.TRIP_FIELDS}
        FROM trips t
        LEFT JOIN countries oc ON oc.id = t.origin_country_id
        WHERE t.share_token_hash = %s
          AND t.visibility = 'link'
        """,
        (token_hash,),
    )


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
    return (
        trips.get_trip_for_user(connection, row["id"], user_id) if row else None
    )


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
    return (
        trips.get_trip_for_user(connection, row["id"], user_id) if row else None
    )

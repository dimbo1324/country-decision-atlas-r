from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_trips_with_invalid_share_state(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, visibility, share_token_prefix
        FROM trips
        WHERE (
            visibility = 'private'
            AND (share_token_hash IS NOT NULL OR share_token_prefix IS NOT NULL)
        )
        OR (
            visibility = 'link'
            AND (share_token_hash IS NULL OR share_token_prefix IS NULL)
        )
        """,
    )


def list_reminders_with_invalid_trip_or_item(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tr.id::text AS id,
            tr.trip_id::text AS trip_id,
            tr.checklist_item_id::text AS checklist_item_id
        FROM trip_reminders tr
        LEFT JOIN trip_checklist_items tci ON tci.id = tr.checklist_item_id
        WHERE tr.checklist_item_id IS NOT NULL
          AND (
              tci.id IS NULL
              OR tci.trip_id <> tr.trip_id
          )
        """,
    )


def list_trip_waypoints_with_invalid_position(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT trip_id::text AS trip_id, position, COUNT(*) AS count
        FROM trip_waypoints
        GROUP BY trip_id, position
        HAVING position < 1 OR COUNT(*) > 1
        """,
    )

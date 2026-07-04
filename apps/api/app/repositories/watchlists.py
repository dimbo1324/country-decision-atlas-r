from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


WATCHLIST_FIELDS = """
    w.id::text AS id,
    w.user_id::text AS user_id,
    c.slug AS country_slug,
    c.name AS country_name,
    w.status,
    w.notify_legal_signals,
    w.notify_drift_changes,
    w.notify_route_updates,
    w.notes,
    w.created_source,
    w.created_at,
    w.updated_at,
    w.archived_at
"""


def list_user_watchlist(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {WATCHLIST_FIELDS}
        FROM watchlists w
        JOIN countries c ON c.id = w.country_id
        WHERE w.user_id::text = %s AND w.status = 'active'
        ORDER BY w.created_at DESC
        """,
        (user_id,),
    )


def get_user_watchlist_item(
    connection: Connection[Any], user_id: str, watchlist_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {WATCHLIST_FIELDS}
        FROM watchlists w
        JOIN countries c ON c.id = w.country_id
        WHERE w.id::text = %s AND w.user_id::text = %s
        """,
        (watchlist_id, user_id),
    )


def get_user_watchlist_item_by_country_slug(
    connection: Connection[Any], user_id: str, country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {WATCHLIST_FIELDS}
        FROM watchlists w
        JOIN countries c ON c.id = w.country_id
        WHERE w.user_id::text = %s AND c.slug = %s
        """,
        (user_id, country_slug),
    )


def add_country_to_watchlist(
    connection: Connection[Any],
    *,
    user_id: str,
    country_id: str,
    created_source: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO watchlists (user_id, country_id, status, created_source)
        VALUES (%s, %s, 'active', %s)
        ON CONFLICT (user_id, country_id) DO UPDATE
        SET status = 'active', archived_at = NULL, updated_at = NOW()
        RETURNING id::text AS id, user_id::text AS user_id, country_id::text AS country_id
        """,
        (user_id, country_id, created_source),
    )


def archive_country_from_watchlist(
    connection: Connection[Any], *, user_id: str, country_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE watchlists
        SET status = 'archived', archived_at = NOW(), updated_at = NOW()
        WHERE user_id::text = %s AND country_id::text = %s AND status = 'active'
        RETURNING id::text AS id
        """,
        (user_id, country_id),
    )


def update_watchlist_preferences(
    connection: Connection[Any],
    *,
    user_id: str,
    country_id: str,
    notify_legal_signals: bool | None,
    notify_drift_changes: bool | None,
    notify_route_updates: bool | None,
    notes: str | None,
    notes_provided: bool,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE watchlists
        SET
            notify_legal_signals = COALESCE(%s, notify_legal_signals),
            notify_drift_changes = COALESCE(%s, notify_drift_changes),
            notify_route_updates = COALESCE(%s, notify_route_updates),
            notes = CASE WHEN %s THEN %s ELSE notes END,
            updated_at = NOW()
        WHERE user_id::text = %s AND country_id::text = %s AND status = 'active'
        RETURNING id::text AS id
        """,
        (
            notify_legal_signals,
            notify_drift_changes,
            notify_route_updates,
            notes_provided,
            notes,
            user_id,
            country_id,
        ),
    )


def get_watchlist_status_for_country(
    connection: Connection[Any], user_id: str, country_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT id
        FROM watchlists
        WHERE user_id::text = %s AND country_id::text = %s AND status = 'active'
        """,
        (user_id, country_id),
    )
    return row is not None


def count_user_watchlist(connection: Connection[Any], user_id: str) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM watchlists WHERE user_id::text = %s AND status = 'active'",
        (user_id,),
    )
    return int(row["total"]) if row else 0

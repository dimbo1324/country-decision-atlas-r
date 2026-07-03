from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_watchlists_referencing_missing_users(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT w.id::text AS id, w.user_id::text AS user_id
        FROM watchlists w
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = w.user_id)
        """,
    )


def list_watchlists_referencing_missing_countries(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT w.id::text AS id, w.country_id::text AS country_id
        FROM watchlists w
        WHERE NOT EXISTS (SELECT 1 FROM countries c WHERE c.id = w.country_id)
        """,
    )


def list_watchlists_with_invalid_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, status
        FROM watchlists
        WHERE status NOT IN ('active', 'archived')
        """,
    )


def list_duplicate_active_watchlist_entries(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT user_id::text AS user_id, country_id::text AS country_id, COUNT(*)::int AS entry_count
        FROM watchlists
        WHERE status = 'active'
        GROUP BY user_id, country_id
        HAVING COUNT(*) > 1
        """,
    )


def list_archived_watchlists_missing_archived_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id
        FROM watchlists
        WHERE status = 'archived' AND archived_at IS NULL
        """,
    )


def list_watchlists_with_null_notification_flags(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id
        FROM watchlists
        WHERE notify_legal_signals IS NULL
           OR notify_drift_changes IS NULL
           OR notify_route_updates IS NULL
        """,
    )

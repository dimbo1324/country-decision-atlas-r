from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_telegram_links_with_invalid_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, telegram_user_id, status
        FROM user_telegram_links
        WHERE status NOT IN ('linked', 'unlinked')
        """,
    )


def list_linked_telegram_links_missing_linked_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, telegram_user_id
        FROM user_telegram_links
        WHERE status = 'linked' AND linked_at IS NULL
        """,
    )


def list_unlinked_telegram_links_missing_unlinked_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, telegram_user_id
        FROM user_telegram_links
        WHERE status = 'unlinked' AND unlinked_at IS NULL
        """,
    )


def list_telegram_links_referencing_missing_users(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT l.id::text AS id, l.telegram_user_id, l.user_id::text AS user_id
        FROM user_telegram_links l
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = l.user_id)
        """,
    )


def list_duplicate_active_telegram_links(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT telegram_user_id, COUNT(*)::int AS link_count
        FROM user_telegram_links
        WHERE status = 'linked'
        GROUP BY telegram_user_id
        HAVING COUNT(*) > 1
        """,
    )

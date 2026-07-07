from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_published_proposals_without_curator(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, slug
        FROM country_proposals
        WHERE status IN ('review', 'published')
          AND curator_user_id IS NULL
        """,
    )


def list_published_proposals_with_inactive_country(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT cp.id::text AS id, cp.slug
        FROM country_proposals cp
        JOIN countries c ON c.id = cp.country_id
        WHERE cp.status = 'published'
          AND c.is_active IS NOT TRUE
        """,
    )


def list_proposals_with_non_editor_curator(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT cp.id::text AS id, cp.slug, u.role AS curator_role
        FROM country_proposals cp
        JOIN users u ON u.id = cp.curator_user_id
        WHERE cp.curator_user_id IS NOT NULL
          AND u.role NOT IN ('editor', 'admin', 'owner')
        """,
    )

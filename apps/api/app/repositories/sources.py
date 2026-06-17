from typing import Any

from app.core.database import fetch_all, fetch_one
from psycopg import Connection


def list_sources(
    connection: Connection[Any],
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            title,
            url,
            source_type,
            publisher,
            country_id,
            locale_id,
            reliability_level,
            published_at,
            accessed_at,
            created_at,
            updated_at
        FROM sources
        ORDER BY created_at DESC, title
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


def count_sources(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM sources")
    return int(row["total"]) if row else 0


def list_evidence_items(
    connection: Connection[Any],
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            source_id,
            country_id,
            title,
            summary,
            url,
            quote,
            evidence_type,
            confidence_level,
            published_at,
            created_at,
            updated_at
        FROM evidence_items
        ORDER BY created_at DESC, title
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


def count_evidence_items(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM evidence_items")
    return int(row["total"]) if row else 0

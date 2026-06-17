from typing import Any
from app.core.database import execute_one, fetch_all, fetch_one
from app.schemas.legal_signals import LegalSignalCreate
from psycopg import Connection
def list_legal_signals(
    connection: Connection[Any],
    country_id: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id,
            ls.country_id,
            ls.title,
            ls.summary,
            ls.signal_type,
            ls.sentiment,
            ls.severity,
            ls.status,
            ls.confidence_level,
            ls.effective_date,
            ls.published_at,
            ls.created_at,
            ls.updated_at
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.id::text = %s OR c.slug = %s
        ORDER BY ls.created_at DESC, ls.title
        LIMIT %s OFFSET %s
        """,
        (country_id, country_id, limit, offset),
    )
def count_legal_signals(connection: Connection[Any], country_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.id::text = %s OR c.slug = %s
        """,
        (country_id, country_id),
    )
    return int(row["total"]) if row else 0
def create_legal_signal(
    connection: Connection[Any],
    payload: LegalSignalCreate,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO legal_signals (
            country_id,
            title,
            summary,
            signal_type,
            sentiment,
            severity,
            status,
            confidence_level,
            effective_date,
            published_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING
            id,
            country_id,
            title,
            summary,
            signal_type,
            sentiment,
            severity,
            status,
            confidence_level,
            effective_date,
            published_at,
            created_at,
            updated_at
        """,
        (
            payload.country_id,
            payload.title,
            payload.summary,
            payload.signal_type,
            payload.sentiment,
            payload.severity,
            payload.status,
            payload.confidence_level,
            payload.effective_date,
            payload.published_at,
        ),
    )

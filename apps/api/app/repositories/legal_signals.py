from app.core.database import execute_one, fetch_all, fetch_one
from app.repositories.sorting import resolve_sort_clause
from app.schemas.legal_signals import LegalSignalCreate
from psycopg import Connection
from typing import Any


LEGAL_SIGNAL_SORT_COLUMNS = {
    "published_date": "ls.published_date",
    "effective_date": "ls.effective_date",
    "impact_level": "ls.impact_level",
    "created_at": "ls.created_at",
    "updated_at": "ls.updated_at",
}


def list_legal_signals(
    connection: Connection[Any],
    country_id: str,
    limit: int,
    offset: int,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
    sort: str = "published_date",
    order: str = "desc",
) -> list[dict[str, Any]]:
    filter_sql, params = _filters(
        country_id, signal_type, impact_direction, impact_level, status
    )
    sort_column, order_sql = resolve_sort_clause(
        sort, order, LEGAL_SIGNAL_SORT_COLUMNS, "published_date"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            ls.id::text AS id,
            ls.country_id,
            ls.title_ru,
            COALESCE(ls.title_en, ls.title, '') AS title_en,
            ls.summary_ru,
            COALESCE(ls.summary_en, ls.summary, '') AS summary_en,
            ls.signal_type,
            ls.sentiment,
            ls.severity,
            ls.status,
            ls.legal_status,
            ls.confidence_level,
            ls.effective_date,
            ls.published_at,
            ls.created_at,
            ls.updated_at
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE {filter_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, ls.title
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_legal_signals(
    connection: Connection[Any],
    country_id: str,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
) -> int:
    filter_sql, params = _filters(
        country_id, signal_type, impact_direction, impact_level, status
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE {filter_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def _filters(
    country_id: str,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["(c.id::text = %s OR c.slug = %s)", "ls.status = %s"]
    params: list[Any] = [country_id, country_id, status]
    if signal_type:
        filters.append("ls.signal_type = %s")
        params.append(signal_type)
    if impact_direction:
        filters.append("ls.impact_direction = %s")
        params.append(impact_direction)
    if impact_level:
        filters.append("ls.impact_level = %s")
        params.append(impact_level)
    return " AND ".join(filters), tuple(params)


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
            legal_status,
            confidence_level,
            effective_date,
            published_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING
            id,
            country_id,
            title,
            summary,
            signal_type,
            sentiment,
            severity,
            status,
            legal_status,
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
            payload.legal_status,
            payload.confidence_level,
            payload.effective_date,
            payload.published_at,
        ),
    )

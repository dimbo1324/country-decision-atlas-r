from app.core.database import execute_one, fetch_all, fetch_one
from app.core.locales import SOURCE_LOCALE, localized_column, validate_locale
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
    locale: str,
    limit: int,
    offset: int,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
    sort: str = "published_date",
    order: str = "desc",
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "ls.title_en", "ls.title_ru")
    summary_column = localized_column(
        requested_locale, "ls.summary_en", "ls.summary_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'translated'
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    filter_sql, params = _filters(
        country_id, signal_type, impact_direction, impact_level, status
    )
    sort_column = LEGAL_SIGNAL_SORT_COLUMNS.get(
        sort, LEGAL_SIGNAL_SORT_COLUMNS["published_date"]
    )
    order_sql = "ASC" if order == "asc" else "DESC"
    return fetch_all(
        connection,
        f"""
        SELECT
            ls.id,
            ls.country_id,
            COALESCE({title_column}, ls.title_en, ls.title, '') AS title,
            COALESCE({summary_column}, ls.summary_en, ls.summary, '') AS summary,
            ls.signal_type,
            ls.sentiment,
            ls.severity,
            ls.status,
            ls.confidence_level,
            ls.effective_date,
            ls.published_at,
            ls.created_at,
            ls.updated_at,
            {title_column} IS NOT NULL AND {summary_column} IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
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

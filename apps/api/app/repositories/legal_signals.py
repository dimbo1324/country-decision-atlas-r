from app.core.database import execute_one, fetch_all, fetch_one
from app.core.locales import SOURCE_LOCALE, localized_column, validate_locale
from app.schemas.legal_signals import LegalSignalCreate
from psycopg import Connection
from typing import Any


def list_legal_signals(
    connection: Connection[Any],
    country_id: str,
    locale: str,
    limit: int,
    offset: int,
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

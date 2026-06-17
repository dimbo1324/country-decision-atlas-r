from app.core.database import execute_one, fetch_all, fetch_one
from app.schemas.translations import TranslationJobCreate
from psycopg import Connection
from typing import Any


def list_translations(
    connection: Connection[Any],
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            entity_type,
            entity_id,
            field_name,
            locale_id,
            translated_value,
            status,
            created_at,
            updated_at
        FROM translations
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


def count_translations(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM translations")
    return int(row["total"]) if row else 0


def create_translation_job(
    connection: Connection[Any],
    payload: TranslationJobCreate,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO translation_jobs (
            entity_type,
            entity_id,
            source_locale_id,
            target_locale_id,
            status,
            provider
        )
        SELECT
            %s,
            %s,
            source_locale.id,
            target_locale.id,
            'queued',
            %s
        FROM locales AS target_locale
        LEFT JOIN locales AS source_locale ON source_locale.code = %s
        WHERE target_locale.code = %s
        RETURNING
            id,
            entity_type,
            entity_id,
            source_locale_id,
            target_locale_id,
            status,
            provider,
            error_message,
            created_at,
            updated_at
        """,
        (
            payload.entity_type,
            payload.entity_id,
            payload.provider,
            payload.source_locale_code,
            payload.target_locale_code,
        ),
    )

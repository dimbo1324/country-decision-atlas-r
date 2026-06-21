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


def get_translation_unit(
    connection: Connection[Any],
    entity_type: str,
    entity_id: str,
    field_name: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id::text AS id,
            entity_type,
            entity_id::text AS entity_id,
            field_name,
            original_locale_code,
            source_hash,
            is_active,
            created_at,
            updated_at
        FROM translation_units
        WHERE entity_type = %s
          AND entity_id = %s
          AND field_name = %s
        """,
        (entity_type, entity_id, field_name),
    )


def list_translation_variants_for_unit(
    connection: Connection[Any],
    translation_unit_id: str,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tv.id::text AS id,
            tv.translation_unit_id::text AS translation_unit_id,
            tv.locale_code,
            tv.text,
            tv.status,
            tv.method,
            tv.provider,
            tv.provider_model,
            tv.source_locale_code,
            tv.source_hash,
            tv.is_original,
            tv.reviewed_by,
            tv.reviewed_at,
            tv.quality_score,
            tv.created_at,
            tv.updated_at,
            tu.original_locale_code,
            tu.source_hash AS unit_source_hash
        FROM translation_variants tv
        JOIN translation_units tu ON tu.id = tv.translation_unit_id
        WHERE tv.translation_unit_id = %s
        ORDER BY tv.locale_code, tv.created_at
        """,
        (translation_unit_id,),
    )


def get_best_translation_variant(
    connection: Connection[Any],
    entity_type: str,
    entity_id: str,
    field_name: str,
    requested_locale: str,
    fallback_locale: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            tv.id::text AS id,
            tv.translation_unit_id::text AS translation_unit_id,
            tv.locale_code,
            tv.text,
            tv.status,
            tv.method,
            tv.provider,
            tv.provider_model,
            tv.source_locale_code,
            tv.source_hash,
            tv.is_original,
            tv.reviewed_by,
            tv.reviewed_at,
            tv.quality_score,
            tu.original_locale_code,
            tu.source_hash AS unit_source_hash
        FROM translation_units tu
        JOIN translation_variants tv ON tv.translation_unit_id = tu.id
        WHERE tu.entity_type = %s
          AND tu.entity_id = %s
          AND tu.field_name = %s
          AND tu.is_active = TRUE
          AND tv.locale_code IN (%s, %s)
          AND tv.status NOT IN ('missing', 'fallback', 'stale')
        ORDER BY
            CASE
                WHEN tv.locale_code = %s AND tv.is_original = TRUE THEN 1
                WHEN tv.locale_code = %s AND tv.status = 'human_reviewed' THEN 2
                WHEN tv.locale_code = %s AND tv.status = 'human_authored' THEN 3
                WHEN tv.locale_code = %s AND tv.status = 'machine_translated' THEN 4
                WHEN tv.locale_code = %s AND tv.status = 'needs_review' THEN 5
                WHEN tv.locale_code = %s AND tv.is_original = TRUE THEN 6
                WHEN tv.locale_code = %s AND tv.status = 'human_reviewed' THEN 7
                WHEN tv.locale_code = %s AND tv.status = 'human_authored' THEN 8
                ELSE 99
            END,
            tv.updated_at DESC
        LIMIT 1
        """,
        (
            entity_type,
            entity_id,
            field_name,
            requested_locale,
            fallback_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            fallback_locale,
            fallback_locale,
            fallback_locale,
        ),
    )


def list_best_translation_variants(
    connection: Connection[Any],
    entity_type: str,
    entity_ids: list[str],
    field_names: list[str],
    requested_locale: str,
    fallback_locale: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    if not entity_ids or not field_names:
        return {}
    rows = fetch_all(
        connection,
        """
        SELECT DISTINCT ON (tu.entity_id, tu.field_name)
            tu.entity_id::text AS entity_id,
            tu.field_name,
            tv.locale_code,
            tv.text,
            tv.status,
            tv.is_original
        FROM translation_units tu
        JOIN translation_variants tv ON tv.translation_unit_id = tu.id
        WHERE tu.entity_type = %s
          AND tu.entity_id = ANY(%s::uuid[])
          AND tu.field_name = ANY(%s::text[])
          AND tu.is_active = TRUE
          AND tv.locale_code IN (%s, %s)
          AND tv.status NOT IN ('missing', 'fallback', 'stale')
        ORDER BY
            tu.entity_id,
            tu.field_name,
            CASE
                WHEN tv.locale_code = %s AND tv.is_original = TRUE THEN 1
                WHEN tv.locale_code = %s AND tv.status = 'human_reviewed' THEN 2
                WHEN tv.locale_code = %s AND tv.status = 'human_authored' THEN 3
                WHEN tv.locale_code = %s AND tv.status = 'machine_translated' THEN 4
                WHEN tv.locale_code = %s AND tv.status = 'needs_review' THEN 5
                WHEN tv.locale_code = %s AND tv.is_original = TRUE THEN 6
                WHEN tv.locale_code = %s AND tv.status = 'human_reviewed' THEN 7
                WHEN tv.locale_code = %s AND tv.status = 'human_authored' THEN 8
                ELSE 99
            END,
            tv.updated_at DESC
        """,
        (
            entity_type,
            entity_ids,
            field_names,
            requested_locale,
            fallback_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            fallback_locale,
            fallback_locale,
            fallback_locale,
        ),
    )
    return {(row["entity_id"], row["field_name"]): row for row in rows}


def list_stale_translation_variants(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            translation_unit_id::text AS translation_unit_id,
            locale_code,
            status,
            source_hash
        FROM stale_translation_variants
        ORDER BY translation_unit_id, locale_code
        """,
    )


def count_translation_units(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM translation_units")
    return int(row["total"]) if row else 0


def count_translation_variants(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM translation_variants")
    return int(row["total"]) if row else 0


def list_critical_content_without_units(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        WITH expected_units AS (
            SELECT
                'country_card'::text AS entity_type,
                cc.id AS entity_id,
                fields.field_name
            FROM country_cards cc
            CROSS JOIN LATERAL (
                VALUES
                    ('executive_summary'),
                    ('migration_overview'),
                    ('tax_overview'),
                    ('cost_of_living_overview'),
                    ('business_overview'),
                    ('safety_overview'),
                    ('legal_signals_summary'),
                    ('risk_summary'),
                    ('source_summary')
            ) AS fields(field_name)
            WHERE cc.locale = 'ru'
            UNION ALL
            SELECT 'legal_signal', id, fields.field_name
            FROM legal_signals
            CROSS JOIN LATERAL (
                VALUES ('title'), ('summary')
            ) AS fields(field_name)
            UNION ALL
            SELECT 'evidence_item', id, fields.field_name
            FROM evidence_items
            CROSS JOIN LATERAL (
                VALUES ('claim', claim), ('excerpt', excerpt)
            ) AS fields(field_name, field_value)
            WHERE NULLIF(BTRIM(fields.field_value), '') IS NOT NULL
            UNION ALL
            SELECT 'source', id, 'title'
            FROM sources
            WHERE NULLIF(BTRIM(title), '') IS NOT NULL
            UNION ALL
            SELECT 'scenario', id, fields.field_name
            FROM scenarios
            CROSS JOIN LATERAL (
                VALUES
                    ('title', COALESCE(title_ru, name)),
                    ('description', COALESCE(description_ru, description))
            ) AS fields(field_name, field_value)
            WHERE NULLIF(BTRIM(fields.field_value), '') IS NOT NULL
            UNION ALL
            SELECT 'country_score', id, 'explanation'
            FROM country_scores
            WHERE NULLIF(BTRIM(explanation_ru), '') IS NOT NULL
            UNION ALL
            SELECT 'country_score_breakdown', id, 'explanation'
            FROM country_score_breakdowns
            WHERE NULLIF(BTRIM(explanation_ru), '') IS NOT NULL
        )
        SELECT
            expected_units.entity_type,
            expected_units.entity_id::text AS entity_id,
            expected_units.field_name
        FROM expected_units
        LEFT JOIN translation_units tu
            ON tu.entity_type = expected_units.entity_type
            AND tu.entity_id = expected_units.entity_id
            AND tu.field_name = expected_units.field_name
            AND tu.is_active = TRUE
        WHERE tu.id IS NULL
        ORDER BY
            expected_units.entity_type,
            expected_units.entity_id,
            expected_units.field_name
        """,
    )


def list_foundation_locales(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT code, is_active, is_default, fallback_locale_code, direction
        FROM locales
        WHERE code IN ('ru', 'en')
        ORDER BY code
        """,
    )


def count_default_locales(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM locales WHERE is_default = TRUE",
    )
    return int(row["total"]) if row else 0


def list_active_units_without_variants(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tu.id::text AS id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name
        FROM translation_units tu
        LEFT JOIN translation_variants tv ON tv.translation_unit_id = tu.id
        WHERE tu.is_active = TRUE
        GROUP BY tu.id, tu.entity_type, tu.entity_id, tu.field_name
        HAVING COUNT(tv.id) = 0
        ORDER BY tu.entity_type, tu.entity_id, tu.field_name
        """,
    )


def list_units_without_original_variant(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tu.id::text AS id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name,
            tu.original_locale_code
        FROM translation_units tu
        LEFT JOIN translation_variants tv
            ON tv.translation_unit_id = tu.id
            AND tv.is_original = TRUE
        WHERE tu.is_active = TRUE
          AND tv.id IS NULL
        ORDER BY tu.entity_type, tu.entity_id, tu.field_name
        """,
    )


def list_original_variant_mismatches(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tv.id::text AS id,
            tu.id::text AS translation_unit_id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name,
            tu.original_locale_code,
            tv.locale_code,
            tu.source_hash AS unit_source_hash,
            tv.source_hash AS variant_source_hash
        FROM translation_units tu
        JOIN translation_variants tv
            ON tv.translation_unit_id = tu.id
            AND tv.is_original = TRUE
        WHERE tv.locale_code <> tu.original_locale_code
           OR tv.source_hash <> tu.source_hash
        ORDER BY tu.entity_type, tu.entity_id, tu.field_name
        """,
    )


def list_units_without_english_variant(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tu.id::text AS id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name
        FROM translation_units tu
        LEFT JOIN translation_variants tv
            ON tv.translation_unit_id = tu.id
            AND tv.locale_code = 'en'
            AND tv.status NOT IN ('missing', 'fallback', 'stale')
        WHERE tu.is_active = TRUE
          AND tv.id IS NULL
        ORDER BY tu.entity_type, tu.entity_id, tu.field_name
        """,
    )


def list_invalid_reviewed_machine_variants(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            translation_unit_id::text AS translation_unit_id,
            locale_code,
            status,
            method
        FROM translation_variants
        WHERE method = 'machine'
          AND status = 'human_reviewed'
          AND (reviewed_by IS NULL OR reviewed_at IS NULL)
        ORDER BY translation_unit_id, locale_code
        """,
    )


def list_persisted_fallback_variants(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            translation_unit_id::text AS translation_unit_id,
            locale_code,
            status,
            method
        FROM translation_variants
        WHERE status = 'fallback'
          AND method <> 'system'
        ORDER BY translation_unit_id, locale_code
        """,
    )


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

from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


_JOB_COLUMNS = """
    id::text AS id,
    translation_unit_id::text AS translation_unit_id,
    source_locale_code,
    target_locale_code,
    status,
    priority,
    attempts,
    max_attempts,
    provider,
    provider_model,
    error_message,
    locked_at,
    locked_by,
    metadata,
    created_at,
    started_at,
    completed_at,
    failed_at,
    updated_at
"""

_ACTIVE_STATUSES = ("queued", "running", "pending", "processing")


def find_missing_translation_units(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tu.id::text AS translation_unit_id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name,
            tu.original_locale_code,
            tv_original.text AS source_text,
            tu.source_hash
        FROM translation_units tu
        JOIN translation_variants tv_original
            ON tv_original.translation_unit_id = tu.id
           AND tv_original.is_original = TRUE
        LEFT JOIN translation_variants tv_target
            ON tv_target.translation_unit_id = tu.id
           AND tv_target.locale_code = %s
        WHERE tu.is_active = TRUE
          AND tv_target.id IS NULL
          AND NOT EXISTS (
              SELECT 1
              FROM translation_jobs tj
              WHERE tj.translation_unit_id = tu.id
                AND tj.target_locale_code = %s
                AND tj.status IN ('queued', 'running', 'pending', 'processing')
          )
        ORDER BY tu.created_at
        LIMIT %s
        """,
        (target_locale, target_locale, limit),
    )


def find_stale_translation_units(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tu.id::text AS translation_unit_id,
            tu.entity_type,
            tu.entity_id::text AS entity_id,
            tu.field_name,
            tu.original_locale_code,
            tv_original.text AS source_text,
            tu.source_hash,
            tv_target.id::text AS stale_variant_id
        FROM translation_units tu
        JOIN translation_variants tv_original
            ON tv_original.translation_unit_id = tu.id
           AND tv_original.is_original = TRUE
        JOIN translation_variants tv_target
            ON tv_target.translation_unit_id = tu.id
           AND tv_target.locale_code = %s
           AND tv_target.is_original = FALSE
        WHERE tu.is_active = TRUE
          AND tv_target.source_hash <> tu.source_hash
          AND NOT EXISTS (
              SELECT 1
              FROM translation_jobs tj
              WHERE tj.translation_unit_id = tu.id
                AND tj.target_locale_code = %s
                AND tj.status IN ('queued', 'running', 'pending', 'processing')
          )
        ORDER BY tu.updated_at DESC
        LIMIT %s
        """,
        (target_locale, target_locale, limit),
    )


def create_translation_job(
    connection: Connection[Any],
    translation_unit_id: str,
    source_locale_code: str,
    target_locale_code: str,
    priority: int = 100,
    provider: str | None = None,
    provider_model: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    import json

    meta_json = json.dumps(metadata or {})
    return fetch_one(
        connection,
        f"""
        INSERT INTO translation_jobs (
            translation_unit_id,
            source_locale_code,
            target_locale_code,
            status,
            priority,
            provider,
            provider_model,
            metadata
        ) VALUES (
            %s, %s, %s, 'pending', %s, %s, %s, %s::jsonb
        )
        ON CONFLICT DO NOTHING
        RETURNING {_JOB_COLUMNS}
        """,
        (
            translation_unit_id,
            source_locale_code,
            target_locale_code,
            priority,
            provider,
            provider_model,
            meta_json,
        ),
    )


def _batch_create_translation_jobs(
    connection: Connection[Any],
    units: list[dict[str, Any]],
    target_locale: str,
    priority: int,
) -> list[dict[str, Any]]:
    if not units:
        return []
    placeholders = ", ".join(
        "(%s, %s, %s, 'pending', %s, NULL, NULL, '{}'::jsonb)" for _ in units
    )
    params: list[Any] = []
    for unit in units:
        params.extend(
            [
                unit["translation_unit_id"],
                unit["original_locale_code"],
                target_locale,
                priority,
            ]
        )
    return fetch_all(
        connection,
        f"""
        INSERT INTO translation_jobs (
            translation_unit_id,
            source_locale_code,
            target_locale_code,
            status,
            priority,
            provider,
            provider_model,
            metadata
        )
        VALUES {placeholders}
        ON CONFLICT DO NOTHING
        RETURNING {_JOB_COLUMNS}
        """,
        params,
    )


def create_missing_translation_jobs(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
    priority: int = 100,
) -> list[dict[str, Any]]:
    units = find_missing_translation_units(connection, target_locale, limit)
    return _batch_create_translation_jobs(
        connection, units, target_locale, priority
    )


def create_stale_translation_jobs(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
    priority: int = 80,
) -> list[dict[str, Any]]:
    units = find_stale_translation_units(connection, target_locale, limit)
    return _batch_create_translation_jobs(
        connection, units, target_locale, priority
    )


def list_translation_jobs(
    connection: Connection[Any],
    status: str | None = None,
    target_locale: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    conditions = []
    params: list[Any] = []
    if status:
        conditions.append("status = %s")
        params.append(status)
    if target_locale:
        conditions.append("target_locale_code = %s")
        params.append(target_locale)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [limit, offset]
    return fetch_all(
        connection,
        f"SELECT {_JOB_COLUMNS} FROM translation_jobs {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
        params,
    )


def count_translation_jobs(
    connection: Connection[Any],
    status: str | None = None,
    target_locale: str | None = None,
) -> int:
    conditions = []
    params: list[Any] = []
    if status:
        conditions.append("status = %s")
        params.append(status)
    if target_locale:
        conditions.append("target_locale_code = %s")
        params.append(target_locale)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    row = fetch_one(
        connection,
        f"SELECT COUNT(*) AS total FROM translation_jobs {where}",
        params,
    )
    return int(row["total"]) if row else 0


def lock_next_pending_job(
    connection: Connection[Any],
    worker_id: str,
    target_locale: str | None = None,
) -> dict[str, Any] | None:
    locale_clause = "AND target_locale_code = %s" if target_locale else ""
    params: list[Any] = []
    if target_locale:
        params.append(target_locale)
    params.append(worker_id)
    return fetch_one(
        connection,
        f"""
        WITH next_job AS (
            SELECT id
            FROM translation_jobs
            WHERE status IN ('queued', 'pending')
              AND attempts < max_attempts
              {locale_clause}
            ORDER BY priority ASC, created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        UPDATE translation_jobs tj
        SET
            status = 'processing',
            locked_at = NOW(),
            locked_by = %s,
            started_at = COALESCE(started_at, NOW()),
            attempts = attempts + 1,
            updated_at = NOW()
        FROM next_job
        WHERE tj.id = next_job.id
        RETURNING
            tj.id::text AS id,
            tj.translation_unit_id::text AS translation_unit_id,
            tj.source_locale_code,
            tj.target_locale_code,
            tj.status,
            tj.priority,
            tj.attempts,
            tj.max_attempts,
            tj.provider,
            tj.provider_model,
            tj.error_message,
            tj.locked_at,
            tj.locked_by,
            tj.metadata,
            tj.created_at,
            tj.started_at,
            tj.completed_at,
            tj.failed_at,
            tj.updated_at
        """,
        params,
    )


def list_pending_jobs_for_preview(
    connection: Connection[Any],
    target_locale: str | None = None,
    limit: int = 1,
) -> list[dict[str, Any]]:
    locale_clause = "AND target_locale_code = %s" if target_locale else ""
    params: list[Any] = []
    if target_locale:
        params.append(target_locale)
    params.append(limit)
    return fetch_all(
        connection,
        f"""
        SELECT {_JOB_COLUMNS}
        FROM translation_jobs
        WHERE status IN ('queued', 'pending')
          AND attempts < max_attempts
          {locale_clause}
        ORDER BY priority ASC, created_at ASC
        LIMIT %s
        """,
        params,
    )


def recover_stale_processing_jobs(
    connection: Connection[Any], timeout_seconds: int, limit: int = 100
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        UPDATE translation_jobs
        SET
            status = 'pending',
            attempts = GREATEST(attempts - 1, 0),
            locked_at = NULL,
            locked_by = NULL,
            started_at = NULL,
            error_message = NULL,
            updated_at = NOW()
        WHERE id IN (
            SELECT id
            FROM translation_jobs
            WHERE status = 'processing'
              AND locked_at < NOW() - (%s * INTERVAL '1 second')
            ORDER BY locked_at ASC
            LIMIT %s
            FOR UPDATE SKIP LOCKED
        )
        RETURNING {_JOB_COLUMNS}
        """,
        (timeout_seconds, limit),
    )


def mark_job_completed(
    connection: Connection[Any],
    job_id: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE translation_jobs
        SET status = 'completed', completed_at = NOW(), updated_at = NOW()
        WHERE id = %s
        RETURNING {_JOB_COLUMNS}
        """,
        (job_id,),
    )


def mark_job_failed(
    connection: Connection[Any],
    job_id: str,
    error_message: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE translation_jobs
        SET status = 'failed', failed_at = NOW(), error_message = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING {_JOB_COLUMNS}
        """,
        (error_message, job_id),
    )


def reset_failed_jobs(
    connection: Connection[Any],
    target_locale: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    locale_clause = "AND target_locale_code = %s" if target_locale else ""
    params: list[Any] = []
    if target_locale:
        params.append(target_locale)
    params.append(limit)
    return fetch_all(
        connection,
        f"""
        UPDATE translation_jobs
        SET status = 'pending', locked_at = NULL, locked_by = NULL,
            failed_at = NULL, error_message = NULL, updated_at = NOW()
        WHERE id IN (
            SELECT id FROM translation_jobs
            WHERE status = 'failed'
              AND attempts < max_attempts
              {locale_clause}
            ORDER BY created_at
            LIMIT %s
        )
        RETURNING {_JOB_COLUMNS}
        """,
        params,
    )


def save_translation_variant(
    connection: Connection[Any],
    translation_unit_id: str,
    locale_code: str,
    text: str,
    source_locale_code: str,
    source_hash: str,
    provider: str,
    provider_model: str,
    method: str = "machine",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        INSERT INTO translation_variants (
            translation_unit_id,
            locale_code,
            text,
            status,
            method,
            source_locale_code,
            source_hash,
            is_original,
            provider,
            provider_model
        ) VALUES (
            %s, %s, %s, 'machine_translated', %s, %s, %s, FALSE, %s, %s
        )
        ON CONFLICT (translation_unit_id, locale_code)
        DO UPDATE SET
            text = EXCLUDED.text,
            status = 'machine_translated',
            method = EXCLUDED.method,
            source_locale_code = EXCLUDED.source_locale_code,
            source_hash = EXCLUDED.source_hash,
            provider = EXCLUDED.provider,
            provider_model = EXCLUDED.provider_model,
            updated_at = NOW()
        WHERE translation_variants.is_original = FALSE
        RETURNING id::text AS id, locale_code, text, status, method, is_original, source_hash
        """,
        (
            translation_unit_id,
            locale_code,
            text,
            method,
            source_locale_code,
            source_hash,
            provider,
            provider_model,
        ),
    )


def get_translation_unit_for_job(
    connection: Connection[Any],
    translation_unit_id: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            tu.id::text AS id,
            tu.original_locale_code,
            tu.source_hash,
            tv.text AS source_text
        FROM translation_units tu
        JOIN translation_variants tv
            ON tv.translation_unit_id = tu.id
           AND tv.is_original = TRUE
        WHERE tu.id = %s
        """,
        (translation_unit_id,),
    )

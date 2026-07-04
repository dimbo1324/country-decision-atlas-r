from __future__ import annotations

from app.core.config import get_settings
from app.repositories import translation_jobs as repo
from app.services.translation_providers import (
    FakeTranslationProvider,
    TranslationInput,
    TranslationProvider,
)
from app.services.translation_validation import validate_translation
from psycopg import Connection
from typing import Any


def discover_missing_jobs(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
    priority: int = 100,
) -> list[dict[str, Any]]:
    return repo.create_missing_translation_jobs(
        connection, target_locale, limit, priority
    )


def discover_stale_jobs(
    connection: Connection[Any],
    target_locale: str,
    limit: int = 50,
    priority: int = 80,
) -> list[dict[str, Any]]:
    return repo.create_stale_translation_jobs(
        connection, target_locale, limit, priority
    )


def list_jobs(
    connection: Connection[Any],
    status: str | None,
    target_locale: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    items = repo.list_translation_jobs(
        connection, status, target_locale, limit, offset
    )
    total = repo.count_translation_jobs(connection, status, target_locale)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


def process_next_job(
    connection: Connection[Any],
    worker_id: str,
    target_locale: str | None = None,
    provider: TranslationProvider | None = None,
    dry_run: bool = False,
) -> dict[str, Any] | None:
    effective_provider = provider or FakeTranslationProvider()
    if dry_run:
        jobs = repo.list_pending_jobs_for_preview(connection, target_locale, 1)
        job = jobs[0] if jobs else None
    else:
        settings = get_settings()
        repo.recover_stale_processing_jobs(
            connection,
            settings.translation_job_lock_timeout_seconds,
            settings.translation_job_max_batch_size,
        )
        job = repo.lock_next_pending_job(connection, worker_id, target_locale)
    if job is None:
        return None

    return _process_job(
        connection, job, target_locale, effective_provider, not dry_run
    )


def _process_job(
    connection: Connection[Any],
    job: dict[str, Any],
    target_locale: str | None,
    provider: TranslationProvider,
    persist: bool,
) -> dict[str, Any]:
    job_id = job["id"]
    unit_id = job.get("translation_unit_id")
    target = job.get("target_locale_code") or target_locale

    if not unit_id or not target:
        if persist:
            repo.mark_job_failed(
                connection,
                job_id,
                "missing translation_unit_id or target_locale_code",
            )
        return {
            "job_id": job_id,
            "status": "failed",
            "error": "missing unit or locale",
        }

    unit = repo.get_translation_unit_for_job(connection, unit_id)
    if not unit or not unit.get("source_text"):
        if persist:
            repo.mark_job_failed(connection, job_id, "source text not found")
        return {
            "job_id": job_id,
            "status": "failed",
            "error": "source text not found",
        }

    translation_input = TranslationInput(
        source_text=unit["source_text"],
        source_locale=unit["original_locale_code"],
        target_locale=target,
    )

    try:
        result = provider.translate(translation_input)

        ok, validation_error = validate_translation(
            source_text=unit["source_text"],
            translated_text=result.text,
            source_locale=unit["original_locale_code"],
            target_locale=target,
        )

        if not ok:
            if persist:
                repo.mark_job_failed(
                    connection, job_id, f"validation_failed: {validation_error}"
                )
            return {
                "job_id": job_id,
                "status": "failed",
                "error": f"validation_failed: {validation_error}",
            }

        usage_metadata: dict[str, Any] = {
            "provider": result.provider,
            "provider_model": result.provider_model,
            "input_chars": result.input_chars,
            "output_chars": result.output_chars,
            "duration_ms": result.duration_ms,
            "dry_run": not persist,
        }
        if result.raw_metadata:
            usage_metadata.update(result.raw_metadata)

        if not persist:
            return {
                "job_id": job_id,
                "status": "dry_run",
                "target_locale_code": target,
                "variant_id": None,
                "translated_text": result.text,
                "metadata": usage_metadata,
            }

        variant = repo.save_translation_variant(
            connection,
            translation_unit_id=unit_id,
            locale_code=target,
            text=result.text,
            source_locale_code=unit["original_locale_code"],
            source_hash=unit["source_hash"],
            provider=result.provider,
            provider_model=result.provider_model,
        )
        repo.mark_job_completed(connection, job_id)
        return {
            "job_id": job_id,
            "status": "completed",
            "target_locale_code": target,
            "variant_id": variant["id"] if variant else None,
            "metadata": usage_metadata,
        }
    except Exception as exc:
        if persist:
            repo.mark_job_failed(connection, job_id, str(exc))
        return {"job_id": job_id, "status": "failed", "error": str(exc)}


def process_batch(
    connection: Connection[Any],
    worker_id: str,
    target_locale: str | None = None,
    limit: int = 10,
    provider: TranslationProvider | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    completed = 0
    failed = 0
    effective_provider = provider or FakeTranslationProvider()
    if dry_run:
        pending_jobs = repo.list_pending_jobs_for_preview(
            connection, target_locale, limit
        )
        for job in pending_jobs:
            preview_result = _process_job(
                connection, job, target_locale, effective_provider, False
            )
            results.append(preview_result)
            if preview_result.get("status") == "dry_run":
                completed += 1
            else:
                failed += 1
    else:
        for _ in range(limit):
            processed_result = process_next_job(
                connection, worker_id, target_locale, effective_provider, False
            )
            if processed_result is None:
                break
            connection.commit()
            results.append(processed_result)
            if processed_result.get("status") == "completed":
                completed += 1
            else:
                failed += 1
    return {
        "processed": len(results),
        "completed": completed,
        "failed": failed,
        "results": results,
    }


def retry_failed_jobs(
    connection: Connection[Any],
    target_locale: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return repo.reset_failed_jobs(connection, target_locale, limit)

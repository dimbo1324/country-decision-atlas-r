from app.repositories import translation_jobs as repo
from app.services.translation_providers import (
    FakeTranslationProvider,
    TranslationProvider,
)
from psycopg import Connection
from typing import Any


_default_provider = FakeTranslationProvider()


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
    items = repo.list_translation_jobs(connection, status, target_locale, limit, offset)
    total = repo.count_translation_jobs(connection, status, target_locale)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


def process_next_job(
    connection: Connection[Any],
    worker_id: str,
    target_locale: str | None = None,
    provider: TranslationProvider | None = None,
) -> dict[str, Any] | None:
    effective_provider = provider or _default_provider
    job = repo.lock_next_pending_job(connection, worker_id, target_locale)
    if job is None:
        return None

    job_id = job["id"]
    unit_id = job.get("translation_unit_id")
    target = job.get("target_locale_code") or target_locale

    if not unit_id or not target:
        repo.mark_job_failed(
            connection, job_id, "missing translation_unit_id or target_locale_code"
        )
        return {"job_id": job_id, "status": "failed", "error": "missing unit or locale"}

    unit = repo.get_translation_unit_for_job(connection, unit_id)
    if not unit or not unit.get("source_text"):
        repo.mark_job_failed(connection, job_id, "source text not found")
        return {"job_id": job_id, "status": "failed", "error": "source text not found"}

    try:
        result = effective_provider.translate(
            source_text=unit["source_text"],
            source_locale=unit["original_locale_code"],
            target_locale=target,
        )
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
        }
    except Exception as exc:
        repo.mark_job_failed(connection, job_id, str(exc))
        return {"job_id": job_id, "status": "failed", "error": str(exc)}


def process_batch(
    connection: Connection[Any],
    worker_id: str,
    target_locale: str | None = None,
    limit: int = 10,
    provider: TranslationProvider | None = None,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    completed = 0
    failed = 0
    for _ in range(limit):
        result = process_next_job(connection, worker_id, target_locale, provider)
        if result is None:
            break
        results.append(result)
        if result.get("status") == "completed":
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

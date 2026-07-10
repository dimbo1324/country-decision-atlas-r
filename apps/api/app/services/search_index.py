from app.repositories import search_index as repository
from datetime import datetime
from hashlib import sha256
from psycopg import Connection
from typing import Any


def content_hash(*parts: str) -> str:
    """Shared with scripts/rebuild_search_index.py so a full rebuild and a
    live incremental sync compute the same hash for the same content — a
    different formula between the two would make every full rebuild look
    like content changed when it didn't."""
    return sha256("|".join(parts).encode("utf-8")).hexdigest()


def upsert_document(
    connection: Connection[Any],
    *,
    entity_type: str,
    entity_id: str,
    country_slug: str | None,
    locale: str,
    title: str,
    summary: str,
    body: str,
    path: str,
    source_updated_at: datetime | None,
) -> None:
    if not title.strip() or not path.strip():
        return
    repository.upsert_search_document(
        connection,
        entity_type=entity_type,
        entity_id=entity_id,
        country_slug=country_slug,
        locale=locale,
        title=title,
        summary=summary,
        body=body,
        path=path,
        status="published",
        content_hash=content_hash(
            entity_type, entity_id, locale, title, summary
        ),
        source_updated_at=source_updated_at,
    )


def remove_document(
    connection: Connection[Any],
    *,
    entity_type: str,
    entity_id: str,
    locale: str,
) -> None:
    repository.delete_search_document(
        connection, entity_type, entity_id, locale
    )


def sync_document(
    connection: Connection[Any],
    *,
    entity_type: str,
    entity_id: str,
    country_slug: str | None,
    locale: str,
    status: str,
    title: str,
    summary: str,
    body: str,
    path: str,
    source_updated_at: datetime | None,
) -> None:
    """Keep one entity's search doc in sync with its current status right
    after a publish-transition commits (P1-7, Аудит-эпизод 5), instead of
    only picking up the change on the next full scripts/rebuild_search_index.py
    pass. Upserts when published, removes the doc otherwise (unpublished,
    archived, etc. must not stay searchable)."""
    if status == "published":
        upsert_document(
            connection,
            entity_type=entity_type,
            entity_id=entity_id,
            country_slug=country_slug,
            locale=locale,
            title=title,
            summary=summary,
            body=body,
            path=path,
            source_updated_at=source_updated_at,
        )
    else:
        remove_document(
            connection,
            entity_type=entity_type,
            entity_id=entity_id,
            locale=locale,
        )

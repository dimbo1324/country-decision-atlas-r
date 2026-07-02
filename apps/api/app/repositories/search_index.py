from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from typing import Any


def upsert_search_document(
    connection: Connection[Any],
    *,
    entity_type: str,
    entity_id: str,
    country_slug: str | None,
    locale: str,
    title: str,
    summary: str | None,
    body: str,
    path: str,
    status: str,
    content_hash: str,
    source_updated_at: datetime | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO search_documents (
            entity_type,
            entity_id,
            country_slug,
            locale,
            title,
            summary,
            body,
            path,
            status,
            content_hash,
            source_updated_at,
            search_vector
        ) VALUES (
            %s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            build_search_vector(%s, %s, %s, %s)
        )
        ON CONFLICT (entity_type, entity_id, locale) DO UPDATE SET
            country_slug = EXCLUDED.country_slug,
            title = EXCLUDED.title,
            summary = EXCLUDED.summary,
            body = EXCLUDED.body,
            path = EXCLUDED.path,
            status = EXCLUDED.status,
            content_hash = EXCLUDED.content_hash,
            source_updated_at = EXCLUDED.source_updated_at,
            indexed_at = NOW(),
            search_vector = EXCLUDED.search_vector
        RETURNING
            id::text AS id,
            entity_type,
            entity_id::text AS entity_id,
            country_slug,
            locale,
            title,
            summary,
            body,
            path,
            status,
            content_hash,
            source_updated_at,
            indexed_at
        """,
        (
            entity_type,
            entity_id,
            country_slug,
            locale,
            title,
            summary,
            body,
            path,
            status,
            content_hash,
            source_updated_at,
            locale,
            title,
            summary,
            body,
        ),
    )


def delete_search_document(
    connection: Connection[Any], entity_type: str, entity_id: str, locale: str
) -> int:
    rows = fetch_all(
        connection,
        """
        DELETE FROM search_documents
        WHERE entity_type = %s
          AND entity_id = %s::uuid
          AND locale = %s
        RETURNING id
        """,
        (entity_type, entity_id, locale),
    )
    return len(rows)


def count_search_documents(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM search_documents")
    return int(row["total"]) if row else 0


def list_indexed_entity_ids(
    connection: Connection[Any], entity_type: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT entity_id::text AS entity_id, locale
        FROM search_documents
        WHERE entity_type = %s
        """,
        (entity_type,),
    )


def delete_search_documents_by_ids(
    connection: Connection[Any], entity_type: str, stale: list[tuple[str, str]]
) -> int:
    if not stale:
        return 0
    deleted = 0
    for entity_id, locale in stale:
        deleted += delete_search_document(connection, entity_type, entity_id, locale)
    return deleted


def list_broken_search_documents(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            entity_type,
            entity_id::text AS entity_id,
            locale,
            path,
            title,
            content_hash
        FROM search_documents
        WHERE BTRIM(path) = ''
           OR BTRIM(title) = ''
           OR BTRIM(content_hash) = ''
        ORDER BY indexed_at DESC
        """,
    )

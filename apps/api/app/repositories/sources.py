from app.core.database import fetch_all, fetch_one
from app.repositories.sorting import resolve_sort_clause
from psycopg import Connection
from typing import Any


SOURCE_SORT_COLUMNS = {
    "title": "s.title",
    "created_at": "s.created_at",
    "published_at": "s.published_at",
    "last_checked_at": "s.last_checked_at",
    "confidence": "s.confidence",
}
EVIDENCE_SORT_COLUMNS = {
    "retrieved_at": "ei.retrieved_at",
    "created_at": "ei.created_at",
    "confidence": "ei.confidence",
}


def list_sources(
    connection: Connection[Any],
    limit: int,
    offset: int,
    country_slug: str | None,
    source_type: str | None,
    language: str | None,
    confidence: str | None,
    status: str,
    sort: str,
    order: str,
) -> list[dict[str, Any]]:
    where_sql, params = _source_filters(
        country_slug, source_type, language, confidence, status
    )
    sort_column, order_sql = resolve_sort_clause(
        sort, order, SOURCE_SORT_COLUMNS, "last_checked_at"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            s.id,
            s.title,
            s.url,
            s.source_type,
            s.publisher,
            s.country_id,
            s.locale_id,
            s.reliability_level,
            s.language,
            s.confidence,
            s.status,
            s.published_at,
            s.accessed_at,
            s.last_checked_at,
            s.notes,
            s.created_at,
            s.updated_at
        FROM sources s
        LEFT JOIN countries c ON c.id = s.country_id
        WHERE {where_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, s.title
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_sources(
    connection: Connection[Any],
    country_slug: str | None,
    source_type: str | None,
    language: str | None,
    confidence: str | None,
    status: str,
) -> int:
    where_sql, params = _source_filters(
        country_slug, source_type, language, confidence, status
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM sources s
        LEFT JOIN countries c ON c.id = s.country_id
        WHERE {where_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def list_evidence_items(
    connection: Connection[Any],
    limit: int,
    offset: int,
    country_slug: str | None,
    source_id: str | None,
    legal_signal_id: str | None,
    confidence: str | None,
    status: str,
    sort: str,
    order: str,
) -> list[dict[str, Any]]:
    where_sql, params = _evidence_filters(
        country_slug, source_id, legal_signal_id, confidence, status
    )
    sort_column, order_sql = resolve_sort_clause(
        sort, order, EVIDENCE_SORT_COLUMNS, "retrieved_at"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            ei.id,
            ei.source_id,
            ei.country_id,
            ei.legal_signal_id,
            ei.title,
            ei.summary,
            ei.url,
            ei.quote,
            ei.evidence_type,
            ei.confidence_level,
            ei.claim,
            ei.excerpt,
            ei.retrieved_at,
            ei.confidence,
            ei.status,
            ei.published_at,
            ei.created_at,
            ei.updated_at
        FROM evidence_items ei
        LEFT JOIN countries c ON c.id = ei.country_id
        WHERE {where_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, ei.title
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_evidence_items(
    connection: Connection[Any],
    country_slug: str | None,
    source_id: str | None,
    legal_signal_id: str | None,
    confidence: str | None,
    status: str,
) -> int:
    where_sql, params = _evidence_filters(
        country_slug, source_id, legal_signal_id, confidence, status
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM evidence_items ei
        LEFT JOIN countries c ON c.id = ei.country_id
        WHERE {where_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def _source_filters(
    country_slug: str | None,
    source_type: str | None,
    language: str | None,
    confidence: str | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["s.status = %s"]
    params: list[Any] = [status]
    if country_slug:
        filters.append("c.slug = %s")
        params.append(country_slug)
    if source_type:
        filters.append("s.source_type = %s")
        params.append(source_type)
    if language:
        filters.append("s.language = %s")
        params.append(language)
    if confidence:
        filters.append("s.confidence = %s")
        params.append(confidence)
    return " AND ".join(filters), tuple(params)


def _evidence_filters(
    country_slug: str | None,
    source_id: str | None,
    legal_signal_id: str | None,
    confidence: str | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["ei.status = %s"]
    params: list[Any] = [status]
    if country_slug:
        filters.append("c.slug = %s")
        params.append(country_slug)
    if source_id:
        filters.append("ei.source_id::text = %s")
        params.append(source_id)
    if legal_signal_id:
        filters.append("ei.legal_signal_id::text = %s")
        params.append(legal_signal_id)
    if confidence:
        filters.append("ei.confidence = %s")
        params.append(confidence)
    return " AND ".join(filters), tuple(params)

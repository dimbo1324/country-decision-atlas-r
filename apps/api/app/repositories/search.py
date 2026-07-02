from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def _ts_config(locale: str) -> str:
    return "russian" if locale == "ru" else "simple"


def search_documents(
    connection: Connection[Any],
    query: str,
    locale: str,
    entity_types: list[str] | None,
    country_slug: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    config = _ts_config(locale)
    filters = ["sd.status = 'published'", "sd.locale = %s"]
    params: list[Any] = [locale]
    if entity_types:
        filters.append("sd.entity_type = ANY(%s)")
        params.append(entity_types)
    if country_slug:
        filters.append("sd.country_slug = %s")
        params.append(country_slug)
    where_sql = " AND ".join(filters)
    return fetch_all(
        connection,
        f"""
        SELECT
            sd.id::text AS id,
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            sd.country_slug,
            sd.title,
            sd.path,
            ts_rank(sd.search_vector, query) AS rank,
            ts_headline(
                %s,
                coalesce(sd.summary, sd.body, ''),
                query,
                'MaxWords=30, MinWords=10, ShortWord=3, HighlightAll=false'
            ) AS snippet
        FROM search_documents sd, websearch_to_tsquery(%s, %s) query
        WHERE {where_sql}
          AND sd.search_vector @@ query
        ORDER BY rank DESC, sd.indexed_at DESC
        LIMIT %s OFFSET %s
        """,
        (config, config, query, *params, limit, offset),
    )


def count_search_documents_matching(
    connection: Connection[Any],
    query: str,
    locale: str,
    entity_types: list[str] | None,
    country_slug: str | None,
) -> int:
    config = _ts_config(locale)
    filters = ["sd.status = 'published'", "sd.locale = %s"]
    params: list[Any] = [locale]
    if entity_types:
        filters.append("sd.entity_type = ANY(%s)")
        params.append(entity_types)
    if country_slug:
        filters.append("sd.country_slug = %s")
        params.append(country_slug)
    where_sql = " AND ".join(filters)
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM search_documents sd, websearch_to_tsquery(%s, %s) query
        WHERE {where_sql}
          AND sd.search_vector @@ query
        """,
        (config, query, *params),
    )
    return int(row["total"]) if row else 0

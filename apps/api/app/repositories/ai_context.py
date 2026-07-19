from app.core.database import fetch_all
from app.repositories.staleness import SOURCE_FRESHNESS_STALE_AFTER_DAYS
from psycopg import Connection
from typing import Any


def _ts_config(locale: str) -> str:
    return "russian" if locale == "ru" else "simple"


def search_ai_context_items(
    conn: Connection[Any],
    *,
    query: str,
    locale: str,
    types: list[str] | None,
    country_slug: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    normalized = query.strip()
    if not normalized:
        return _latest_search_documents(
            conn, locale, types, country_slug, limit
        )
    config = _ts_config(locale)
    filters = ["sd.status = 'published'", "sd.locale = %s"]
    params: list[Any] = [locale]
    if types:
        filters.append("sd.entity_type = ANY(%s)")
        params.append(types)
    if country_slug:
        filters.append("sd.country_slug = %s")
        params.append(country_slug)
    where_sql = " AND ".join(filters)
    return fetch_all(
        conn,
        f"""
        SELECT
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            sd.country_slug,
            sd.title,
            COALESCE(sd.summary, sd.body, '') AS excerpt,
            sd.path AS url_path,
            ARRAY[]::text[] AS source_ids,
            ARRAY[]::text[] AS evidence_item_ids,
            'medium' AS confidence,
            CASE
                WHEN sd.source_updated_at IS NULL THEN 'unknown'
                WHEN sd.source_updated_at < NOW() - INTERVAL '{SOURCE_FRESHNESS_STALE_AFTER_DAYS} days' THEN 'stale'
                ELSE 'fresh'
            END AS freshness_status,
            sd.source_updated_at::text AS last_verified_at,
            ts_rank(sd.search_vector, query) AS rank
        FROM search_documents sd, websearch_to_tsquery(%s, %s) query
        WHERE {where_sql}
          AND sd.search_vector @@ query
        ORDER BY rank DESC, sd.indexed_at DESC
        LIMIT %s
        """,
        (config, normalized, *params, limit),
    )


def get_country_ai_context(
    conn: Connection[Any],
    *,
    country_slug: str,
    locale: str,
    limit: int,
) -> list[dict[str, Any]]:
    return _latest_search_documents(conn, locale, None, country_slug, limit)


def get_route_ai_context(
    conn: Connection[Any],
    *,
    route_id: str | None,
    route_slug: str | None,
    country_slug: str | None,
    locale: str,
    limit: int,
) -> list[dict[str, Any]]:
    filters = [
        "sd.status = 'published'",
        "sd.locale = %s",
        "sd.entity_type IN ('route', 'route_checklist_item')",
    ]
    params: list[Any] = [locale]
    if route_id:
        filters.append("sd.entity_id = %s::uuid")
        params.append(route_id)
    if route_slug:
        filters.append("sd.path LIKE %s")
        params.append(f"%{route_slug}%")
    if country_slug:
        filters.append("sd.country_slug = %s")
        params.append(country_slug)
    where_sql = " AND ".join(filters)
    return fetch_all(
        conn,
        f"""
        SELECT
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            sd.country_slug,
            sd.title,
            COALESCE(sd.summary, sd.body, '') AS excerpt,
            sd.path AS url_path,
            ARRAY[]::text[] AS source_ids,
            ARRAY[]::text[] AS evidence_item_ids,
            'medium' AS confidence,
            CASE
                WHEN sd.source_updated_at IS NULL THEN 'unknown'
                WHEN sd.source_updated_at < NOW() - INTERVAL '{SOURCE_FRESHNESS_STALE_AFTER_DAYS} days' THEN 'stale'
                ELSE 'fresh'
            END AS freshness_status,
            sd.source_updated_at::text AS last_verified_at,
            1.0 AS rank
        FROM search_documents sd
        WHERE {where_sql}
        ORDER BY sd.indexed_at DESC
        LIMIT %s
        """,
        (*params, limit),
    )


def get_metric_ai_context(
    conn: Connection[Any],
    *,
    country_slug: str,
    metric_key: str | None,
    scenario_slug: str | None,
    locale: str,
    limit: int,
) -> list[dict[str, Any]]:
    rows = _stored_metric_context(
        conn, country_slug, metric_key, scenario_slug, limit
    )
    remaining = max(limit - len(rows), 0)
    if remaining == 0:
        return rows
    query = " ".join(
        part
        for part in [
            country_slug,
            metric_key,
            scenario_slug,
            "trust drift metric",
        ]
        if part
    )
    return rows + search_ai_context_items(
        conn,
        query=query,
        locale=locale,
        types=[
            "country",
            "legal_signal",
            "source",
            "evidence_item",
            "methodology",
        ],
        country_slug=country_slug,
        limit=remaining,
    )


def get_decision_ai_context(
    conn: Connection[Any],
    *,
    country_slugs: list[str],
    scenario_slug: str | None,
    persona_slug: str | None,
    origin_country_slug: str | None,
    locale: str,
    limit: int,
) -> list[dict[str, Any]]:
    query = " ".join(
        part
        for part in [
            scenario_slug,
            persona_slug,
            origin_country_slug,
            "decision route",
        ]
        if part
    )
    if country_slugs:
        rows: list[dict[str, Any]] = []
        per_country_limit = max(1, limit // len(country_slugs))
        for slug in country_slugs:
            rows.extend(
                search_ai_context_items(
                    conn,
                    query=query,
                    locale=locale,
                    types=["country", "route", "legal_signal", "source"],
                    country_slug=slug,
                    limit=per_country_limit,
                )
            )
        return rows[:limit]
    return search_ai_context_items(
        conn,
        query=query,
        locale=locale,
        types=["country", "route", "legal_signal", "source"],
        country_slug=None,
        limit=limit,
    )


def _latest_search_documents(
    conn: Connection[Any],
    locale: str,
    types: list[str] | None,
    country_slug: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    filters = ["sd.status = 'published'", "sd.locale = %s"]
    params: list[Any] = [locale]
    if types:
        filters.append("sd.entity_type = ANY(%s)")
        params.append(types)
    if country_slug:
        filters.append("sd.country_slug = %s")
        params.append(country_slug)
    where_sql = " AND ".join(filters)
    return fetch_all(
        conn,
        f"""
        SELECT
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            sd.country_slug,
            sd.title,
            COALESCE(sd.summary, sd.body, '') AS excerpt,
            sd.path AS url_path,
            ARRAY[]::text[] AS source_ids,
            ARRAY[]::text[] AS evidence_item_ids,
            'medium' AS confidence,
            CASE
                WHEN sd.source_updated_at IS NULL THEN 'unknown'
                WHEN sd.source_updated_at < NOW() - INTERVAL '{SOURCE_FRESHNESS_STALE_AFTER_DAYS} days' THEN 'stale'
                ELSE 'fresh'
            END AS freshness_status,
            sd.source_updated_at::text AS last_verified_at,
            1.0 AS rank
        FROM search_documents sd
        WHERE {where_sql}
        ORDER BY sd.indexed_at DESC
        LIMIT %s
        """,
        (*params, limit),
    )


def _stored_metric_context(
    conn: Connection[Any],
    country_slug: str,
    metric_key: str | None,
    scenario_slug: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT *
        FROM (
            SELECT
                'platform_metric' AS entity_type,
                cpm.id::text AS entity_id,
                c.slug AS country_slug,
                cpm.metric_key AS title,
                CONCAT(
                    cpm.metric_key,
                    ': value=',
                    COALESCE(cpm.value::text, 'n/a'),
                    ', label=',
                    cpm.label,
                    ', confidence=',
                    cpm.confidence,
                    ', freshness=',
                    cpm.freshness_status
                ) AS excerpt,
                CONCAT('/countries/', c.slug) AS url_path,
                ARRAY[]::text[] AS source_ids,
                ARRAY[]::text[] AS evidence_item_ids,
                cpm.confidence,
                cpm.freshness_status,
                cpm.computed_at::text AS last_verified_at,
                1.0 AS rank
            FROM country_platform_metrics cpm
            JOIN countries c ON c.id = cpm.country_id
            WHERE c.slug = %s
              AND (%s::text IS NULL OR cpm.metric_key = %s)
              AND (%s::text IS NULL OR cpm.scenario_slug = %s)
            UNION ALL
            SELECT
                'trust_score' AS entity_type,
                cts.id::text AS entity_id,
                c.slug AS country_slug,
                'trust_score' AS title,
                CONCAT(
                    'trust_score: value=',
                    COALESCE(cts.trust_score::text, 'n/a'),
                    ', label=',
                    cts.trust_label,
                    ', confidence=',
                    cts.confidence,
                    ', freshness=',
                    cts.freshness_status
                ) AS excerpt,
                CONCAT('/countries/', c.slug) AS url_path,
                ARRAY[]::text[] AS source_ids,
                ARRAY[]::text[] AS evidence_item_ids,
                cts.confidence,
                cts.freshness_status,
                cts.last_verified_at::text AS last_verified_at,
                1.0 AS rank
            FROM country_trust_scores cts
            JOIN countries c ON c.id = cts.country_id
            WHERE c.slug = %s
              AND (%s::text IS NULL OR %s = 'trust_score')
            UNION ALL
            SELECT
                'country_drift' AS entity_type,
                cds.id::text AS entity_id,
                c.slug AS country_slug,
                'country_drift' AS title,
                CONCAT(
                    'country_drift: label=',
                    cds.label,
                    ', net_score=',
                    COALESCE(cds.net_score::text, 'n/a'),
                    ', confidence=',
                    cds.confidence
                ) AS excerpt,
                CONCAT('/countries/', c.slug) AS url_path,
                ARRAY[]::text[] AS source_ids,
                ARRAY[]::text[] AS evidence_item_ids,
                cds.confidence,
                'fresh' AS freshness_status,
                cds.computed_at::text AS last_verified_at,
                1.0 AS rank
            FROM country_drift_snapshots cds
            JOIN countries c ON c.id = cds.country_id
            WHERE c.slug = %s
              AND (%s::text IS NULL OR %s = 'country_drift')
        ) metric_context
        ORDER BY rank DESC, last_verified_at DESC NULLS LAST
        LIMIT %s
        """,
        (
            country_slug,
            metric_key,
            metric_key,
            scenario_slug,
            scenario_slug,
            country_slug,
            metric_key,
            metric_key,
            country_slug,
            metric_key,
            metric_key,
            limit,
        ),
    )

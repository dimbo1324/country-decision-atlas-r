from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def _filters(
    country_slug: str | None,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    affected_group: str | None,
    year_from: int | None,
    year_to: int | None,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["ls.status = 'published'"]
    params: list[Any] = []
    for value, expression in [
        (country_slug, "c.slug = %s"),
        (signal_type, "ls.signal_type = %s"),
        (impact_direction, "lse.impact_direction = %s"),
        (impact_level, "lse.impact_level = %s"),
    ]:
        if value:
            filters.append(expression)
            params.append(value)
    if affected_group:
        filters.append("lse.affected_groups ? %s")
        params.append(affected_group)
    if year_from is not None:
        filters.append("lse.event_date >= make_date(%s, 1, 1)")
        params.append(year_from)
    if year_to is not None:
        filters.append("lse.event_date < make_date(%s + 1, 1, 1)")
        params.append(year_to)
    return " AND ".join(filters), tuple(params)


def list_timeline_events(
    connection: Connection[Any],
    country_slug: str | None,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    affected_group: str | None,
    year_from: int | None,
    year_to: int | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    where_sql, params = _filters(
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        affected_group,
        year_from,
        year_to,
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            lse.id::text AS id,
            lse.legal_signal_id::text AS legal_signal_id,
            lse.country_id::text AS country_id,
            c.slug AS country_slug,
            c.name AS country_name,
            lse.event_date,
            EXTRACT(YEAR FROM lse.event_date)::int AS event_year,
            lse.event_type,
            lse.impact_direction,
            lse.impact_level,
            lse.affected_groups,
            lse.title,
            lse.summary,
            ls.signal_type,
            ls.title_ru,
            COALESCE(ls.title_en, ls.title, '') AS title_en,
            ls.summary_ru,
            COALESCE(ls.summary_en, ls.summary, '') AS summary_en,
            s.id::text AS source_ref_id,
            s.title AS source_title,
            s.url AS source_url,
            s.publisher AS source_publisher,
            s.source_type,
            s.confidence AS source_confidence,
            ei.id::text AS evidence_ref_id,
            COALESCE(ei.claim, ei.title) AS evidence_claim,
            COALESCE(ei.excerpt, ei.quote) AS evidence_excerpt,
            ei.url AS evidence_url,
            COALESCE(ei.confidence, ei.confidence_level) AS evidence_confidence,
            lse.created_at
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        JOIN countries c ON c.id = lse.country_id
        LEFT JOIN sources s ON s.id = lse.source_id
        LEFT JOIN evidence_items ei ON ei.id = lse.evidence_item_id
        WHERE {where_sql}
        ORDER BY
            lse.event_date DESC,
            CASE lse.impact_level
                WHEN 'critical' THEN 4
                WHEN 'high' THEN 3
                WHEN 'medium' THEN 2
                ELSE 1
            END DESC,
            lse.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_timeline_events(
    connection: Connection[Any],
    country_slug: str | None,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    affected_group: str | None,
    year_from: int | None,
    year_to: int | None,
) -> int:
    where_sql, params = _filters(
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        affected_group,
        year_from,
        year_to,
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        JOIN countries c ON c.id = lse.country_id
        WHERE {where_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def list_timeline_years(
    connection: Connection[Any], country_slug: str | None = None
) -> list[int]:
    where_sql = "WHERE ls.status = 'published'"
    params: tuple[Any, ...] = ()
    if country_slug:
        where_sql += " AND c.slug = %s"
        params = (country_slug,)
    rows = fetch_all(
        connection,
        f"""
        SELECT DISTINCT EXTRACT(YEAR FROM lse.event_date)::int AS year
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        JOIN countries c ON c.id = lse.country_id
        {where_sql}
        ORDER BY year DESC
        """,
        params,
    )
    return [int(row["year"]) for row in rows]


def country_exists(connection: Connection[Any], country_slug: str) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT 1 AS found FROM countries WHERE slug = %s AND is_active = TRUE",
            (country_slug,),
        )
        is not None
    )

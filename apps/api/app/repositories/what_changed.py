from app.core.database import fetch_all
from datetime import datetime
from psycopg import Connection
from typing import Any


DOMAIN_EVENT_TYPES = (
    "legal_signal.published",
    "route.published",
    "drift.changed",
)


def list_country_domain_events_since(
    conn: Connection[Any], country_slug: str, since: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            de.id::text AS id,
            de.event_type,
            de.aggregate_type AS entity_type,
            de.aggregate_id::text AS entity_id,
            de.country_slug,
            de.payload,
            de.created_at AS occurred_at
        FROM domain_events de
        WHERE de.country_slug = %s
          AND de.event_type = ANY(%s)
          AND de.created_at >= %s
        ORDER BY de.created_at DESC
        LIMIT %s
        """,
        (country_slug, list(DOMAIN_EVENT_TYPES), since, limit),
    )


def list_country_data_journal_since(
    conn: Connection[Any], country_slug: str, since: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        WITH journal_entries AS (
            SELECT
                de.id::text AS id,
                de.event_type,
                de.aggregate_type AS entity_type,
                de.aggregate_id::text AS entity_id,
                de.country_slug,
                de.payload,
                de.created_at AS occurred_at
            FROM domain_events de
            WHERE de.country_slug = %s
              AND de.event_type = ANY(%s)
              AND de.created_at >= %s

            UNION ALL

            SELECT
                CONCAT('legal_signal:', ls.id::text) AS id,
                'legal_signal.published' AS event_type,
                'legal_signal' AS entity_type,
                ls.id::text AS entity_id,
                c.slug AS country_slug,
                jsonb_build_object(
                    'title', COALESCE(ls.title_en, ls.title_ru, ls.title),
                    'signal_type', ls.signal_type,
                    'impact_level', ls.impact_level
                ) AS payload,
                COALESCE(ls.updated_at, ls.published_date::timestamptz) AS occurred_at
            FROM legal_signals ls
            JOIN countries c ON c.id = ls.country_id
            WHERE c.slug = %s
              AND ls.status = 'published'
              AND COALESCE(ls.updated_at, ls.published_date::timestamptz) >= %s

            UNION ALL

            SELECT
                CONCAT('route:', r.id::text) AS id,
                'route.published' AS event_type,
                'route' AS entity_type,
                r.id::text AS entity_id,
                c.slug AS country_slug,
                jsonb_build_object(
                    'title', COALESCE(r.title, r.title_ru),
                    'route_type', r.route_type
                ) AS payload,
                r.updated_at AS occurred_at
            FROM routes r
            JOIN countries c ON c.id = r.country_id
            WHERE c.slug = %s
              AND r.status = 'published'
              AND r.updated_at >= %s
        )
        SELECT *
        FROM (
            SELECT DISTINCT ON (entity_type, entity_id, event_type)
                id, event_type, entity_type, entity_id, country_slug, payload, occurred_at
            FROM journal_entries
            ORDER BY entity_type, entity_id, event_type, occurred_at DESC
        ) deduplicated
        ORDER BY occurred_at DESC
        LIMIT %s
        """,
        (
            country_slug,
            list(DOMAIN_EVENT_TYPES),
            since,
            country_slug,
            since,
            country_slug,
            since,
            limit,
        ),
    )


def list_country_drift_changes_since(
    conn: Connection[Any], country_slug: str, since: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug,
            cds.label,
            cds.previous_label,
            cds.confidence,
            cds.computed_at AS occurred_at
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE c.slug = %s
          AND cds.computed_at >= %s
          AND cds.previous_label IS DISTINCT FROM cds.label
        ORDER BY cds.computed_at DESC
        LIMIT %s
        """,
        (country_slug, since, limit),
    )


def list_country_route_changes_since(
    conn: Connection[Any], country_slug: str, since: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            r.id::text AS id,
            c.slug AS country_slug,
            COALESCE(r.title, r.title_ru) AS title,
            r.route_type,
            r.slug AS route_slug,
            r.updated_at AS occurred_at
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = %s
          AND r.status = 'published'
          AND r.updated_at >= %s
        ORDER BY r.updated_at DESC
        LIMIT %s
        """,
        (country_slug, since, limit),
    )


def list_country_legal_signal_changes_since(
    conn: Connection[Any], country_slug: str, since: datetime, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            ls.id::text AS id,
            c.slug AS country_slug,
            COALESCE(ls.title_en, ls.title_ru, ls.title) AS title,
            ls.signal_type,
            ls.impact_level,
            COALESCE(ls.updated_at, ls.published_date::timestamptz) AS occurred_at
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = %s
          AND ls.status = 'published'
          AND COALESCE(ls.updated_at, ls.published_date::timestamptz) >= %s
        ORDER BY occurred_at DESC
        LIMIT %s
        """,
        (country_slug, since, limit),
    )

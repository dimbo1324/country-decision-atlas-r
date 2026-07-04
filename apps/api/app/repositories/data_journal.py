from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


PUBLIC_EVENT_TYPES = (
    "legal_signal.published",
    "legal_signal_event.published",
    "route.published",
    "user_story.published",
)


def list_country_data_journal_entries(
    conn: Connection[Any], country_slug: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        WITH journal_entries AS (
            SELECT
                de.id::text AS id,
                de.event_type,
                de.country_slug,
                de.aggregate_type AS entity_type,
                de.aggregate_id::text AS entity_id,
                de.payload,
                de.created_at AS event_date,
                'domain_events' AS source,
                TRUE AS is_source_backed,
                de.created_at AS last_verified_at
            FROM domain_events de
            WHERE de.country_slug = %s
              AND de.event_type = ANY(%s)

            UNION ALL

            SELECT
                CONCAT('legal_signal:', ls.id::text) AS id,
                'legal_signal.published' AS event_type,
                c.slug AS country_slug,
                'legal_signal' AS entity_type,
                ls.id::text AS entity_id,
                jsonb_build_object(
                    'title', COALESCE(ls.title_en, ls.title_ru, ls.title),
                    'signal_type', ls.signal_type,
                    'impact_direction', ls.impact_direction,
                    'impact_level', ls.impact_level
                ) AS payload,
                COALESCE(ls.updated_at, ls.published_date::timestamptz) AS event_date,
                'published_content' AS source,
                TRUE AS is_source_backed,
                COALESCE(ls.updated_at, ls.published_date::timestamptz) AS last_verified_at
            FROM legal_signals ls
            JOIN countries c ON c.id = ls.country_id
            WHERE c.slug = %s
              AND ls.status = 'published'

            UNION ALL

            SELECT
                CONCAT('route:', r.id::text) AS id,
                'route.published' AS event_type,
                c.slug AS country_slug,
                'route' AS entity_type,
                r.id::text AS entity_id,
                jsonb_build_object(
                    'title', COALESCE(r.title, r.title_ru),
                    'route_type', r.route_type,
                    'legal_status', r.legal_status
                ) AS payload,
                r.updated_at AS event_date,
                'published_content' AS source,
                TRUE AS is_source_backed,
                r.updated_at AS last_verified_at
            FROM routes r
            JOIN countries c ON c.id = r.country_id
            WHERE c.slug = %s
              AND r.status = 'published'
        )
        SELECT *
        FROM (
            SELECT DISTINCT ON (entity_type, entity_id, event_type)
                id,
                event_type,
                country_slug,
                entity_type,
                entity_id,
                payload,
                event_date,
                source,
                is_source_backed,
                last_verified_at
            FROM journal_entries
            ORDER BY entity_type, entity_id, event_type, event_date DESC
        ) deduplicated
        ORDER BY event_date DESC, id
        LIMIT %s OFFSET %s
        """,
        (
            country_slug,
            list(PUBLIC_EVENT_TYPES),
            country_slug,
            country_slug,
            limit,
            offset,
        ),
    )


def count_country_data_journal_entries(
    conn: Connection[Any], country_slug: str
) -> int:
    row = fetch_one(
        conn,
        """
        SELECT COUNT(*) AS total
        FROM (
            SELECT de.aggregate_type, de.aggregate_id, de.event_type
            FROM domain_events de
            WHERE de.country_slug = %s
              AND de.event_type = ANY(%s)

            UNION

            SELECT 'legal_signal', ls.id, 'legal_signal.published'
            FROM legal_signals ls
            JOIN countries c ON c.id = ls.country_id
            WHERE c.slug = %s
              AND ls.status = 'published'

            UNION

            SELECT 'route', r.id, 'route.published'
            FROM routes r
            JOIN countries c ON c.id = r.country_id
            WHERE c.slug = %s
              AND r.status = 'published'
        ) entries
        """,
        (country_slug, list(PUBLIC_EVENT_TYPES), country_slug, country_slug),
    )
    return int(row["total"]) if row else 0


def get_country_last_verified_at(
    conn: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        SELECT MAX(last_verified_at) AS last_verified_at
        FROM (
            SELECT de.created_at AS last_verified_at
            FROM domain_events de
            WHERE de.country_slug = %s
              AND de.event_type = ANY(%s)

            UNION ALL

            SELECT COALESCE(ls.updated_at, ls.published_date::timestamptz)
            FROM legal_signals ls
            JOIN countries c ON c.id = ls.country_id
            WHERE c.slug = %s
              AND ls.status = 'published'

            UNION ALL

            SELECT r.updated_at
            FROM routes r
            JOIN countries c ON c.id = r.country_id
            WHERE c.slug = %s
              AND r.status = 'published'
        ) timestamps
        """,
        (country_slug, list(PUBLIC_EVENT_TYPES), country_slug, country_slug),
    )

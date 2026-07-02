from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_domain_events_with_unknown_country(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT de.id::text AS id, de.event_type, de.country_slug
        FROM domain_events de
        LEFT JOIN countries c ON c.slug = de.country_slug
        WHERE de.country_slug IS NOT NULL
          AND c.id IS NULL
        ORDER BY de.created_at DESC
        """,
    )


def list_domain_events_referencing_non_published_content(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            de.id::text AS id,
            de.event_type,
            de.aggregate_id::text AS aggregate_id,
            r.status AS route_status
        FROM domain_events de
        JOIN routes r ON r.id = de.aggregate_id
        WHERE de.event_type = 'route.published'
          AND r.status <> 'published'

        UNION ALL

        SELECT
            de.id::text AS id,
            de.event_type,
            de.aggregate_id::text AS aggregate_id,
            ls.status AS route_status
        FROM domain_events de
        JOIN legal_signals ls ON ls.id = de.aggregate_id
        WHERE de.event_type = 'legal_signal.published'
          AND ls.status <> 'published'
        """,
    )

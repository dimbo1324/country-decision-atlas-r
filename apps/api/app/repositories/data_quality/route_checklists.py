from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_published_checklist_items_missing_title(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            rci.id::text AS id,
            r.slug AS route_slug,
            c.slug AS country_slug
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE rci.status = 'published'
          AND NULLIF(TRIM(rci.title), '') IS NULL
        ORDER BY c.slug, r.slug, rci.step_order
        """,
    )


def list_duplicate_step_order_checklist_items(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            rci.route_id::text AS route_id,
            r.slug AS route_slug,
            c.slug AS country_slug,
            rci.step_order,
            COUNT(*) AS item_count
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        GROUP BY rci.route_id, r.slug, c.slug, rci.step_order
        HAVING COUNT(*) > 1
        ORDER BY c.slug, r.slug, rci.step_order
        """,
    )

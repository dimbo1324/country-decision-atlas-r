from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_published_legal_signals_for_country_slugs(
    connection: Connection[Any], country_slugs: list[str]
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id::text AS id,
            c.slug AS country_slug,
            ls.title,
            ls.summary,
            ls.signal_type,
            ls.severity,
            ls.impact_level,
            ls.source_id::text AS source_id
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = ANY(%s)
          AND ls.status = 'published'
        ORDER BY c.slug, ls.published_at DESC NULLS LAST, ls.updated_at DESC
        """,
        (country_slugs,),
    )

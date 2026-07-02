from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_search_documents_referencing_non_published_content(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            sd.id::text AS id,
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            r.status AS referenced_status
        FROM search_documents sd
        JOIN routes r ON r.id = sd.entity_id
        WHERE sd.entity_type = 'route'
          AND sd.status = 'published'
          AND r.status <> 'published'

        UNION ALL

        SELECT
            sd.id::text AS id,
            sd.entity_type,
            sd.entity_id::text AS entity_id,
            ls.status AS referenced_status
        FROM search_documents sd
        JOIN legal_signals ls ON ls.id = sd.entity_id
        WHERE sd.entity_type = 'legal_signal'
          AND sd.status = 'published'
          AND ls.status <> 'published'
        """,
    )

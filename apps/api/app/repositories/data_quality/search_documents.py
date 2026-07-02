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


def list_published_routes_missing_from_index(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT r.id::text AS id, r.slug, c.slug AS country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
          AND NOT EXISTS (
              SELECT 1 FROM search_documents sd
              WHERE sd.entity_type = 'route' AND sd.entity_id = r.id
          )
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_legal_signals_missing_from_index(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT ls.id::text AS id, c.slug AS country_slug
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE ls.status = 'published'
          AND NOT EXISTS (
              SELECT 1 FROM search_documents sd
              WHERE sd.entity_type = 'legal_signal' AND sd.entity_id = ls.id
          )
        ORDER BY c.slug
        """,
    )


def list_active_countries_missing_from_index(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT c.id::text AS id, c.slug
        FROM countries c
        WHERE c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM search_documents sd
              WHERE sd.entity_type = 'country' AND sd.entity_id = c.id
          )
        ORDER BY c.slug
        """,
    )


def list_published_sources_missing_from_index(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT s.id::text AS id
        FROM sources s
        WHERE s.status = 'published'
          AND NOT EXISTS (
              SELECT 1 FROM search_documents sd
              WHERE sd.entity_type = 'source' AND sd.entity_id = s.id
          )
        ORDER BY s.id
        """,
    )


def list_published_evidence_missing_from_index(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT ei.id::text AS id
        FROM evidence_items ei
        WHERE ei.status = 'published'
          AND NOT EXISTS (
              SELECT 1 FROM search_documents sd
              WHERE sd.entity_type = 'evidence_item' AND sd.entity_id = ei.id
          )
        ORDER BY ei.id
        """,
    )


def list_search_documents_with_incomplete_locale_coverage(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            entity_type,
            entity_id::text AS entity_id,
            COUNT(DISTINCT locale) AS locale_count
        FROM search_documents
        WHERE status = 'published'
        GROUP BY entity_type, entity_id
        HAVING COUNT(DISTINCT locale) < 2
        ORDER BY entity_type, entity_id
        """,
    )

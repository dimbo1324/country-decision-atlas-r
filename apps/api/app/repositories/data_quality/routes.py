from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_published_routes_without_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        LEFT JOIN route_sources rs ON rs.route_id = r.id
        WHERE r.status = 'published'
          AND rs.route_id IS NULL
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_routes_missing_required_text(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug,
            CASE
                WHEN NULLIF(TRIM(r.title), '') IS NULL THEN 'title'
                WHEN NULLIF(TRIM(r.summary), '') IS NULL THEN 'summary'
                WHEN NULLIF(TRIM(r.eligibility_summary), '') IS NULL THEN 'eligibility_summary'
                ELSE 'unknown'
            END AS missing_field
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
          AND (
              NULLIF(TRIM(r.title), '') IS NULL
              OR NULLIF(TRIM(r.summary), '') IS NULL
              OR NULLIF(TRIM(r.eligibility_summary), '') IS NULL
          )
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_routes_with_all_eligibility_unknown(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
          AND r.allows_work = 'unknown'
          AND r.allows_family = 'unknown'
          AND r.leads_to_pr = 'unknown'
          AND r.leads_to_citizenship = 'unknown'
          AND r.requires_income_proof = 'unknown'
          AND r.requires_local_address = 'unknown'
          AND r.requires_criminal_record_check = 'unknown'
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_routes_without_documents(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        LEFT JOIN route_documents rd ON rd.route_id = r.id
        WHERE r.status = 'published'
          AND rd.route_id IS NULL
        ORDER BY c.slug, r.slug
        """,
    )


def list_route_source_country_mismatches(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            c.slug AS country_slug,
            s.id::text AS source_id,
            sc.slug AS source_country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        JOIN route_sources rs ON rs.route_id = r.id
        JOIN sources s ON s.id = rs.source_id
        JOIN countries sc ON sc.id = s.country_id
        WHERE r.status = 'published'
          AND s.country_id IS NOT NULL
          AND r.country_id <> s.country_id
        ORDER BY c.slug, r.slug
        """,
    )


def list_route_evidence_country_mismatches(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            c.slug AS country_slug,
            ei.id::text AS evidence_item_id,
            ec.slug AS evidence_country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        JOIN route_evidence re ON re.route_id = r.id
        JOIN evidence_items ei ON ei.id = re.evidence_item_id
        JOIN countries ec ON ec.id = ei.country_id
        WHERE r.status = 'published'
          AND ei.country_id IS NOT NULL
          AND r.country_id <> ei.country_id
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_routes_missing_legal_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
          AND r.legal_status IS NULL
        ORDER BY c.slug, r.slug
        """,
    )


def list_published_routes_with_unknown_legal_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            r.id::text AS id,
            r.slug,
            r.route_type,
            c.slug AS country_slug,
            r.legal_status
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.status = 'published'
          AND r.legal_status = 'unknown'
        ORDER BY c.slug, r.slug
        """,
    )

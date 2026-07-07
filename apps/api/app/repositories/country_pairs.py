from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


COUNTRY_PAIR_FIELDS = """
    cpc.id::text AS id,
    cpc.origin_country_id::text AS origin_country_id,
    cpc.destination_country_id::text AS destination_country_id,
    oc.slug AS origin_slug,
    oc.name AS origin_name,
    oc.iso2 AS origin_iso2,
    dc.slug AS destination_slug,
    dc.name AS destination_name,
    dc.iso2 AS destination_iso2,
    cpc.status,
    cpc.visa_note,
    cpc.tax_treaty_note,
    cpc.banking_note,
    cpc.flight_logistics_note,
    cpc.timezone_note,
    cpc.language_note,
    cpc.migration_restriction_note,
    cpc.practical_summary,
    cpc.compatibility_label,
    cpc.confidence,
    cpc.freshness_status,
    cpc.last_verified_at,
    cpc.created_at,
    cpc.updated_at
"""


def get_country_pair_compatibility(
    connection: Connection[Any], origin_slug: str, destination_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {COUNTRY_PAIR_FIELDS}
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE oc.slug = %s
          AND dc.slug = %s
          AND cpc.status = 'published'
          AND oc.is_demo = FALSE
          AND dc.is_demo = FALSE
        """,
        (origin_slug, destination_slug),
    )


def list_destination_compatibility(
    connection: Connection[Any], origin_slug: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {COUNTRY_PAIR_FIELDS}
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE oc.slug = %s
          AND cpc.status = 'published'
          AND oc.is_demo = FALSE
          AND dc.is_demo = FALSE
        ORDER BY dc.slug
        """,
        (origin_slug,),
    )


def list_pair_sources(
    connection: Connection[Any], pair_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            s.id::text AS id,
            s.title,
            s.url,
            s.source_type,
            s.publisher,
            COALESCE(s.confidence, s.reliability_level) AS confidence,
            c.slug AS country_slug
        FROM country_pair_compatibility_sources cps
        JOIN sources s ON s.id = cps.source_id
        LEFT JOIN countries c ON c.id = s.country_id
        WHERE cps.country_pair_id::text = %s
          AND s.status = 'published'
        ORDER BY
            CASE s.source_type
                WHEN 'official' THEN 1
                WHEN 'dataset' THEN 2
                WHEN 'research' THEN 3
                ELSE 4
            END,
            s.title
        """,
        (pair_id,),
    )


def list_pair_evidence(
    connection: Connection[Any], pair_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ei.id::text AS id,
            ei.source_id::text AS source_id,
            COALESCE(ei.claim, ei.title) AS claim,
            COALESCE(ei.excerpt, ei.summary) AS excerpt,
            COALESCE(ei.confidence, ei.confidence_level) AS confidence,
            c.slug AS country_slug,
            s.title AS source_title,
            s.url AS source_url
        FROM country_pair_compatibility_evidence cpe
        JOIN evidence_items ei ON ei.id = cpe.evidence_item_id
        LEFT JOIN sources s ON s.id = ei.source_id
        LEFT JOIN countries c ON c.id = ei.country_id
        WHERE cpe.country_pair_id::text = %s
          AND ei.status = 'published'
        ORDER BY COALESCE(ei.retrieved_at, ei.created_at) DESC NULLS LAST, ei.title
        """,
        (pair_id,),
    )


def count_published_pairs(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM country_pair_compatibility WHERE status = 'published'",
    )
    return int(row["total"]) if row else 0


def list_pair_quality_findings(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpc.id::text AS id,
            oc.slug AS origin_slug,
            dc.slug AS destination_slug
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        LEFT JOIN country_pair_compatibility_sources cps ON cps.country_pair_id = cpc.id
        WHERE cpc.status = 'published'
          AND cps.country_pair_id IS NULL
        ORDER BY oc.slug, dc.slug
        """,
    )

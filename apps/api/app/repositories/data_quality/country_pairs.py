from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_published_pairs_without_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            cpc.id::text AS id,
            oc.slug AS origin_slug,
            dc.slug AS destination_slug
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        LEFT JOIN country_pair_compatibility_sources cps
            ON cps.country_pair_id = cpc.id
        WHERE cpc.status = 'published'
          AND cps.country_pair_id IS NULL
        ORDER BY oc.slug, dc.slug
        """,
    )


def list_published_pairs_missing_last_verified_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            cpc.id::text AS id,
            oc.slug AS origin_slug,
            dc.slug AS destination_slug
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE cpc.status = 'published'
          AND cpc.last_verified_at IS NULL
        ORDER BY oc.slug, dc.slug
        """,
    )


def list_stale_published_pairs(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            cpc.id::text AS id,
            oc.slug AS origin_slug,
            dc.slug AS destination_slug,
            cpc.freshness_status
        FROM country_pair_compatibility cpc
        JOIN countries oc ON oc.id = cpc.origin_country_id
        JOIN countries dc ON dc.id = cpc.destination_country_id
        WHERE cpc.status = 'published'
          AND cpc.freshness_status = 'stale'
        ORDER BY oc.slug, dc.slug
        """,
    )

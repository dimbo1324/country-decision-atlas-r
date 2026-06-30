from app.repositories.data_quality._shared import (
    fetch_all,
)
from psycopg import Connection
from typing import Any


REQUIRED_METHODOLOGY_SLUGS = [
    "what_is_cii",
    "what_is_trust_score",
    "what_is_confidence",
    "what_is_freshness",
    "legal_disclaimer",
]

REQUIRED_GLOSSARY_SLUGS = [
    "trust_score",
    "confidence",
    "freshness",
    "cii",
    "source",
]


def list_active_countries_missing_trust_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT c.slug
        FROM countries c
        WHERE c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM country_trust_scores cts
              WHERE cts.country_id = c.id
          )
        ORDER BY c.slug
        """,
        (),
    )


def list_invalid_trust_score_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cts.id::text AS id,
            c.slug AS country_slug,
            cts.trust_score,
            cts.trust_label
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE
            (cts.trust_score IS NOT NULL AND (cts.trust_score < 0 OR cts.trust_score > 100))
            OR cts.trust_label NOT IN (
                'very_low', 'low', 'medium', 'high', 'very_high', 'insufficient_data'
            )
            OR cts.confidence NOT IN ('low', 'medium', 'high')
            OR cts.freshness_status NOT IN ('fresh', 'aging', 'stale', 'unknown')
        ORDER BY c.slug
        """,
        (),
    )


def list_inconsistent_trust_insufficient_data(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cts.id::text AS id,
            c.slug AS country_slug,
            cts.trust_score,
            cts.trust_label
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE
            (cts.trust_label = 'insufficient_data' AND cts.trust_score IS NOT NULL)
            OR (cts.trust_label <> 'insufficient_data' AND cts.trust_score IS NULL)
        ORDER BY c.slug
        """,
        (),
    )


def list_stale_trust_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cts.id::text AS id,
            c.slug AS country_slug,
            cts.computed_at,
            EXTRACT(EPOCH FROM (NOW() - cts.computed_at)) / 86400 AS days_old
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE cts.computed_at < NOW() - INTERVAL '30 days'
        ORDER BY cts.computed_at ASC
        """,
        (),
    )


def list_missing_required_methodology_sections(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT required.slug
        FROM (
            SELECT UNNEST(%s::text[]) AS slug
        ) required
        WHERE NOT EXISTS (
            SELECT 1
            FROM methodology_sections ms
            WHERE ms.slug = required.slug
              AND ms.status = 'published'
        )
        ORDER BY required.slug
        """,
        (list(REQUIRED_METHODOLOGY_SLUGS),),
    )


def list_missing_required_glossary_terms(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT required.slug
        FROM (
            SELECT UNNEST(%s::text[]) AS slug
        ) required
        WHERE NOT EXISTS (
            SELECT 1
            FROM glossary_terms gt
            WHERE gt.slug = required.slug
              AND gt.status = 'published'
        )
        ORDER BY required.slug
        """,
        (list(REQUIRED_GLOSSARY_SLUGS),),
    )

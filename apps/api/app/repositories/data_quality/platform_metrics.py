from app.repositories.data_quality._shared import (
    MVP_COUNTRY_SLUGS,
    MVP_SCENARIO_SLUGS,
    fetch_all,
)
from psycopg import Connection
from typing import Any


STALE_DAYS_THRESHOLD = 30


def list_mvp_countries_missing_global_platform_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT c.slug
        FROM countries c
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM country_platform_metrics cpm
              WHERE cpm.country_id = c.id
                AND cpm.metric_key IN (
                    'legal_velocity_index',
                    'contradiction_score'
                )
                AND cpm.scenario_slug = '__global__'
          )
        ORDER BY c.slug
        """,
        (MVP_COUNTRY_SLUGS,),
    )


def list_mvp_countries_missing_scenario_risk_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT c.slug, s.slug AS scenario_slug
        FROM countries c
        CROSS JOIN scenarios s
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND s.slug = ANY(%s)
          AND s.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM country_platform_metrics cpm
              WHERE cpm.country_id = c.id
                AND cpm.metric_key = 'scenario_specific_risk_score'
                AND cpm.scenario_slug = s.slug
          )
        ORDER BY c.slug, s.slug
        """,
        (MVP_COUNTRY_SLUGS, MVP_SCENARIO_SLUGS),
    )


def list_invalid_platform_metric_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.value,
            cpm.label,
            cpm.confidence,
            cpm.freshness_status
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE
            (cpm.value IS NOT NULL AND (cpm.value < 0 OR cpm.value > 100))
            OR cpm.label NOT IN (
                'insufficient_data', 'low', 'moderate', 'elevated', 'high', 'critical'
            )
            OR cpm.confidence NOT IN ('low', 'medium', 'high')
            OR cpm.freshness_status NOT IN ('fresh', 'stale', 'unknown')
        ORDER BY c.slug, cpm.metric_key
        """,
        (),
    )


def list_inconsistent_insufficient_data_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.value,
            cpm.label
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE
            (cpm.label = 'insufficient_data' AND cpm.value IS NOT NULL)
            OR (cpm.label <> 'insufficient_data' AND cpm.value IS NULL)
        ORDER BY c.slug, cpm.metric_key
        """,
        (),
    )


def list_stale_platform_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.computed_at,
            EXTRACT(EPOCH FROM (NOW() - cpm.computed_at)) / 86400 AS days_old
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE cpm.computed_at IS NOT NULL
          AND cpm.computed_at < NOW() - INTERVAL '30 days'
        ORDER BY cpm.computed_at ASC
        """,
        (),
    )


def list_platform_metrics_with_missing_methodology(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key,
            cpm.methodology_version
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE cpm.methodology_version IS NULL OR cpm.methodology_version = ''
        ORDER BY c.slug, cpm.metric_key
        """,
        (),
    )


def list_platform_metrics_with_missing_computed_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE cpm.computed_at IS NULL
        ORDER BY c.slug, cpm.metric_key
        """,
        (),
    )


def list_high_confidence_low_sample_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cpm.id::text AS id,
            c.slug AS country_slug,
            cpm.metric_key,
            cpm.confidence,
            cpm.signal_count,
            cpm.event_count
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE cpm.confidence = 'high'
          AND cpm.label <> 'insufficient_data'
          AND (cpm.signal_count + cpm.event_count) < 3
        ORDER BY c.slug, cpm.metric_key
        """,
        (),
    )

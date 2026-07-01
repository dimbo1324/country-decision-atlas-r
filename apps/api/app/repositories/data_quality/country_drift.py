from app.repositories.data_quality._shared import fetch_all
from psycopg import Connection
from typing import Any


def list_active_countries_missing_drift_snapshots(
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
              FROM country_drift_snapshots cds
              WHERE cds.country_id = c.id
          )
        ORDER BY c.slug
        """,
        (),
    )


def list_invalid_drift_snapshot_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug,
            cds.label,
            cds.confidence,
            cds.net_score
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE
            cds.label NOT IN (
                'insufficient_data', 'negative', 'stable', 'mildly_positive', 'positive'
            )
            OR cds.confidence NOT IN ('low', 'medium', 'high')
            OR (cds.net_score IS NOT NULL AND (cds.net_score < -100 OR cds.net_score > 100))
        ORDER BY c.slug
        """,
        (),
    )


def list_drift_snapshots_insufficient_data_inconsistent(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug,
            cds.label,
            cds.event_count,
            cds.total_weight
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE
            (cds.label = 'insufficient_data' AND cds.event_count >= 3 AND cds.total_weight > 0)
            OR (cds.label <> 'insufficient_data' AND cds.event_count < 3)
        ORDER BY c.slug
        """,
        (),
    )


def list_drift_snapshots_insufficient_data_with_high_confidence(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug,
            cds.label,
            cds.confidence
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE cds.label = 'insufficient_data'
          AND cds.confidence <> 'low'
        ORDER BY c.slug
        """,
        (),
    )


def list_drift_snapshots_missing_methodology_version(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE cds.methodology_version IS NULL OR cds.methodology_version = ''
        ORDER BY c.slug
        """,
        (),
    )


def list_drift_snapshots_missing_computed_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE cds.computed_at IS NULL
        ORDER BY c.slug
        """,
        (),
    )


def list_drift_snapshots_with_non_object_input_summary(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cds.id::text AS id,
            c.slug AS country_slug
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE jsonb_typeof(cds.input_summary) <> 'object'
        ORDER BY c.slug
        """,
        (),
    )


def list_duplicate_drift_changed_event_keys(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT event_key, COUNT(*) AS occurrences
        FROM domain_events
        WHERE event_type = 'drift.changed'
        GROUP BY event_key
        HAVING COUNT(*) > 1
        ORDER BY event_key
        """,
        (),
    )


def list_drift_changed_events_missing_payload_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            event_key,
            payload
        FROM domain_events
        WHERE event_type = 'drift.changed'
          AND (
              payload->>'previous_label' IS NULL
              OR payload->>'new_label' IS NULL
          )
        ORDER BY event_key
        """,
        (),
    )

from app.core.database import execute_one, fetch_all, fetch_one
from datetime import date, datetime
from decimal import Decimal
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


_SNAPSHOT_COLUMNS = """
    cds.id::text AS id,
    cds.country_id::text AS country_id,
    cds.period_start,
    cds.period_end,
    cds.window_days,
    cds.label,
    cds.previous_label,
    cds.confidence,
    cds.net_score,
    cds.positive_weight,
    cds.negative_weight,
    cds.neutral_weight,
    cds.mixed_weight,
    cds.uncertain_weight,
    cds.total_weight,
    cds.event_count,
    cds.positive_count,
    cds.negative_count,
    cds.neutral_count,
    cds.mixed_count,
    cds.uncertain_count,
    cds.methodology_version,
    cds.input_summary,
    cds.computed_at,
    cds.expires_at,
    cds.created_at,
    cds.updated_at
"""


def list_countries_for_drift(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS country_id,
            slug,
            name
        FROM countries
        WHERE is_active = TRUE
        ORDER BY slug
        """,
    )


def get_country_for_drift(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id::text AS id,
            slug,
            name,
            is_demo
        FROM countries
        WHERE slug = %s
          AND is_active = TRUE
        """,
        (country_slug,),
    )


def list_drift_input_events(
    connection: Connection[Any],
    country_slug: str,
    period_start: date,
    period_end: date,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            lse.id::text AS event_id,
            lse.legal_signal_id::text AS legal_signal_id,
            lse.country_id::text AS country_id,
            c.slug AS country_slug,
            lse.event_date,
            lse.impact_direction,
            lse.impact_level,
            ls.signal_type,
            lse.affected_groups,
            ls.legal_status,
            lse.source_id::text AS source_id,
            lse.evidence_item_id::text AS evidence_item_id,
            COALESCE(evidence_summary.evidence_count, 0) AS evidence_count,
            evidence_summary.sample_evidence_item_id
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        JOIN countries c ON c.id = lse.country_id
        LEFT JOIN LATERAL (
            SELECT
                COUNT(*) AS evidence_count,
                MIN(ei.id::text) AS sample_evidence_item_id
            FROM evidence_items ei
            WHERE ei.legal_signal_id = ls.id
        ) evidence_summary ON TRUE
        WHERE c.slug = %s
          AND ls.status = 'published'
          AND lse.event_date >= %s
          AND lse.event_date <= %s
          AND lse.event_date <= CURRENT_DATE
        ORDER BY lse.event_date ASC, lse.id
        """,
        (country_slug, period_start, period_end),
    )


def get_latest_drift_snapshot(
    connection: Connection[Any],
    country_slug: str,
    methodology_version: str = "v1.0",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {_SNAPSHOT_COLUMNS},
            c.slug AS country_slug
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE c.slug = %s
          AND cds.methodology_version = %s
        ORDER BY cds.period_end DESC, cds.computed_at DESC
        LIMIT 1
        """,
        (country_slug, methodology_version),
    )


def get_previous_drift_snapshot(
    connection: Connection[Any],
    country_id: str,
    period_end: date,
    methodology_version: str = "v1.0",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {_SNAPSHOT_COLUMNS}
        FROM country_drift_snapshots cds
        WHERE cds.country_id::text = %s
          AND cds.period_end < %s
          AND cds.methodology_version = %s
        ORDER BY cds.period_end DESC, cds.computed_at DESC
        LIMIT 1
        """,
        (country_id, period_end, methodology_version),
    )


def upsert_drift_snapshot(
    connection: Connection[Any],
    *,
    country_id: str,
    period_start: date,
    period_end: date,
    window_days: int,
    label: str,
    previous_label: str | None,
    confidence: str,
    net_score: Decimal | None,
    positive_weight: Decimal,
    negative_weight: Decimal,
    neutral_weight: Decimal,
    mixed_weight: Decimal,
    uncertain_weight: Decimal,
    total_weight: Decimal,
    event_count: int,
    positive_count: int,
    negative_count: int,
    neutral_count: int,
    mixed_count: int,
    uncertain_count: int,
    methodology_version: str,
    input_summary: dict[str, Any],
    computed_at: datetime,
    expires_at: datetime | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO country_drift_snapshots AS cds (
            country_id,
            period_start,
            period_end,
            window_days,
            label,
            previous_label,
            confidence,
            net_score,
            positive_weight,
            negative_weight,
            neutral_weight,
            mixed_weight,
            uncertain_weight,
            total_weight,
            event_count,
            positive_count,
            negative_count,
            neutral_count,
            mixed_count,
            uncertain_count,
            methodology_version,
            input_summary,
            computed_at,
            expires_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON CONFLICT (country_id, period_start, period_end, methodology_version)
        DO UPDATE SET
            label = EXCLUDED.label,
            previous_label = EXCLUDED.previous_label,
            confidence = EXCLUDED.confidence,
            net_score = EXCLUDED.net_score,
            positive_weight = EXCLUDED.positive_weight,
            negative_weight = EXCLUDED.negative_weight,
            neutral_weight = EXCLUDED.neutral_weight,
            mixed_weight = EXCLUDED.mixed_weight,
            uncertain_weight = EXCLUDED.uncertain_weight,
            total_weight = EXCLUDED.total_weight,
            event_count = EXCLUDED.event_count,
            positive_count = EXCLUDED.positive_count,
            negative_count = EXCLUDED.negative_count,
            neutral_count = EXCLUDED.neutral_count,
            mixed_count = EXCLUDED.mixed_count,
            uncertain_count = EXCLUDED.uncertain_count,
            input_summary = EXCLUDED.input_summary,
            computed_at = EXCLUDED.computed_at,
            expires_at = EXCLUDED.expires_at,
            updated_at = NOW()
        RETURNING
            {_SNAPSHOT_COLUMNS}
        """,
        (
            country_id,
            period_start,
            period_end,
            window_days,
            label,
            previous_label,
            confidence,
            net_score,
            positive_weight,
            negative_weight,
            neutral_weight,
            mixed_weight,
            uncertain_weight,
            total_weight,
            event_count,
            positive_count,
            negative_count,
            neutral_count,
            mixed_count,
            uncertain_count,
            methodology_version,
            Jsonb(input_summary),
            computed_at,
            expires_at,
        ),
    )


def list_drift_snapshots(
    connection: Connection[Any],
    country_slug: str,
    limit: int = 12,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {_SNAPSHOT_COLUMNS},
            c.slug AS country_slug
        FROM country_drift_snapshots cds
        JOIN countries c ON c.id = cds.country_id
        WHERE c.slug = %s
        ORDER BY cds.period_end DESC, cds.computed_at DESC
        LIMIT %s
        """,
        (country_slug, limit),
    )


def count_drift_snapshots(
    connection: Connection[Any], country_slug: str | None = None
) -> int:
    if country_slug is not None:
        row = fetch_one(
            connection,
            """
            SELECT COUNT(*) AS total
            FROM country_drift_snapshots cds
            JOIN countries c ON c.id = cds.country_id
            WHERE c.slug = %s
            """,
            (country_slug,),
        )
    else:
        row = fetch_one(
            connection,
            "SELECT COUNT(*) AS total FROM country_drift_snapshots",
        )
    return int(row["total"]) if row else 0

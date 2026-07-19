from app.core.database import execute_one, fetch_all, fetch_one
from app.repositories.staleness import RECOMPUTE_STALE_AFTER_DAYS
from psycopg import Connection
from typing import Any


def get_trust_inputs_for_country(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            c.id AS country_id,
            c.slug AS country_slug,
            COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'published') AS source_count,
            COUNT(DISTINCT ei.id) FILTER (WHERE ei.status = 'published') AS evidence_count,
            COUNT(DISTINCT ls.id) FILTER (WHERE ls.status = 'published') AS legal_signal_count,
            COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'published') AS route_count,
            COUNT(DISTINCT cpm.id) AS platform_metric_count,
            MAX(
                GREATEST(
                    s.updated_at,
                    ei.updated_at,
                    ls.updated_at
                )
            ) AS last_verified_at,
            (
                SELECT cpm2.value
                FROM country_platform_metrics cpm2
                WHERE cpm2.country_id = c.id
                  AND cpm2.metric_key = 'contradiction_score'
                  AND cpm2.scenario_slug = '__global__'
                LIMIT 1
            ) AS contradiction_score_value
        FROM countries c
        LEFT JOIN sources s ON s.country_id = c.id
        LEFT JOIN evidence_items ei ON ei.country_id = c.id
        LEFT JOIN legal_signals ls ON ls.country_id = c.id
        LEFT JOIN routes r ON r.country_id = c.id
        LEFT JOIN country_platform_metrics cpm ON cpm.country_id = c.id
        WHERE c.slug = %s
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        """,
        (country_slug,),
    )


def upsert_country_trust_score(
    connection: Connection[Any], payload: dict[str, Any]
) -> dict[str, Any] | None:
    return execute_one(
        connection,
        """
        INSERT INTO country_trust_scores (
            country_id,
            trust_score,
            trust_label,
            confidence,
            freshness_status,
            source_count,
            evidence_count,
            legal_signal_count,
            route_count,
            platform_metric_count,
            contradiction_score,
            freshness_score,
            evidence_depth_score,
            source_quality_score,
            review_coverage_score,
            last_verified_at,
            computed_at,
            expires_at,
            methodology_version,
            input_summary
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (country_id) DO UPDATE SET
            trust_score = EXCLUDED.trust_score,
            trust_label = EXCLUDED.trust_label,
            confidence = EXCLUDED.confidence,
            freshness_status = EXCLUDED.freshness_status,
            source_count = EXCLUDED.source_count,
            evidence_count = EXCLUDED.evidence_count,
            legal_signal_count = EXCLUDED.legal_signal_count,
            route_count = EXCLUDED.route_count,
            platform_metric_count = EXCLUDED.platform_metric_count,
            contradiction_score = EXCLUDED.contradiction_score,
            freshness_score = EXCLUDED.freshness_score,
            evidence_depth_score = EXCLUDED.evidence_depth_score,
            source_quality_score = EXCLUDED.source_quality_score,
            review_coverage_score = EXCLUDED.review_coverage_score,
            last_verified_at = EXCLUDED.last_verified_at,
            computed_at = EXCLUDED.computed_at,
            expires_at = EXCLUDED.expires_at,
            methodology_version = EXCLUDED.methodology_version,
            input_summary = EXCLUDED.input_summary,
            updated_at = NOW()
        RETURNING
            id::text,
            trust_score,
            trust_label,
            confidence,
            freshness_status,
            computed_at
        """,
        (
            payload["country_id"],
            payload.get("trust_score"),
            payload["trust_label"],
            payload["confidence"],
            payload["freshness_status"],
            payload.get("source_count", 0),
            payload.get("evidence_count", 0),
            payload.get("legal_signal_count", 0),
            payload.get("route_count", 0),
            payload.get("platform_metric_count", 0),
            payload.get("contradiction_score"),
            payload.get("freshness_score"),
            payload.get("evidence_depth_score"),
            payload.get("source_quality_score"),
            payload.get("review_coverage_score"),
            payload.get("last_verified_at"),
            payload.get("computed_at"),
            payload.get("expires_at"),
            payload.get("methodology_version", "v1.0"),
            payload["input_summary"],
        ),
    )


def get_country_trust_score(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            cts.trust_score,
            cts.trust_label,
            cts.confidence,
            cts.freshness_status,
            cts.source_count,
            cts.evidence_count,
            cts.legal_signal_count,
            cts.route_count,
            cts.platform_metric_count,
            cts.contradiction_score,
            cts.freshness_score,
            cts.evidence_depth_score,
            cts.source_quality_score,
            cts.review_coverage_score,
            cts.last_verified_at,
            cts.computed_at,
            cts.expires_at,
            cts.methodology_version,
            cts.input_summary
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE c.slug = %s
          AND c.is_active = TRUE
          AND c.is_demo = FALSE
        """,
        (country_slug,),
    )


def list_country_trust_scores(
    connection: Connection[Any], country_slugs: list[str] | None = None
) -> list[dict[str, Any]]:
    if country_slugs is not None:
        return fetch_all(
            connection,
            """
            SELECT
                c.slug AS country_slug,
                cts.trust_score,
                cts.trust_label,
                cts.confidence,
                cts.freshness_status,
                cts.source_count,
                cts.evidence_count,
                cts.legal_signal_count,
                cts.route_count,
                cts.platform_metric_count,
                cts.contradiction_score,
                cts.freshness_score,
                cts.evidence_depth_score,
                cts.source_quality_score,
                cts.review_coverage_score,
                cts.last_verified_at,
                cts.computed_at,
                cts.expires_at,
                cts.methodology_version,
                cts.input_summary
            FROM country_trust_scores cts
            JOIN countries c ON c.id = cts.country_id
            WHERE c.slug = ANY(%s)
              AND c.is_active = TRUE
              AND c.is_demo = FALSE
            ORDER BY c.slug
            """,
            (country_slugs,),
        )
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            cts.trust_score,
            cts.trust_label,
            cts.confidence,
            cts.freshness_status,
            cts.source_count,
            cts.evidence_count,
            cts.legal_signal_count,
            cts.route_count,
            cts.platform_metric_count,
            cts.contradiction_score,
            cts.freshness_score,
            cts.evidence_depth_score,
            cts.source_quality_score,
            cts.review_coverage_score,
            cts.last_verified_at,
            cts.computed_at,
            cts.expires_at,
            cts.methodology_version,
            cts.input_summary
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE c.is_active = TRUE AND c.is_demo = FALSE
        ORDER BY c.slug
        """,
    )


def list_active_countries(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id, slug FROM countries WHERE is_active = TRUE ORDER BY slug
        """,
    )


def count_missing_country_trust_scores(
    connection: Connection[Any],
) -> int:
    result = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS count
        FROM countries c
        WHERE c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM country_trust_scores cts
              WHERE cts.country_id = c.id
          )
        """,
    )
    return int(result["count"]) if result else 0


def list_stale_country_trust_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            c.slug AS country_slug,
            cts.computed_at,
            EXTRACT(EPOCH FROM (NOW() - cts.computed_at)) / 86400 AS days_old
        FROM country_trust_scores cts
        JOIN countries c ON c.id = cts.country_id
        WHERE cts.computed_at < NOW() - INTERVAL '{RECOMPUTE_STALE_AFTER_DAYS} days'
        ORDER BY cts.computed_at ASC
        """,
    )

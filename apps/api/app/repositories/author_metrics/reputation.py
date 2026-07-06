from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def get_reputation_inputs_for_author(
    connection: Connection[Any], author_user_id: str
) -> dict[str, Any]:
    row = fetch_one(
        connection,
        """
        SELECT
            COUNT(DISTINCT amd.id) FILTER (
                WHERE amd.status = 'published'
            ) AS published_metric_count,
            COUNT(amv.id) AS total_values,
            COUNT(amv.id) FILTER (
                WHERE amv.source_url IS NOT NULL
            ) AS sourced_values,
            MAX(amv.updated_at) AS last_value_updated_at,
            (
                SELECT COUNT(*) FROM countries WHERE is_active = TRUE
            ) AS active_country_count
        FROM author_metric_definitions amd
        LEFT JOIN author_metric_values amv ON amv.metric_id = amd.id
        WHERE amd.author_user_id::text = %s AND amd.status = 'published'
        """,
        (author_user_id,),
    )
    return dict(row) if row else {}


def list_authors_with_published_metrics(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT DISTINCT amd.author_user_id::text AS author_user_id
        FROM author_metric_definitions amd
        WHERE amd.status = 'published'
        ORDER BY author_user_id
        """,
    )


def upsert_author_reputation(
    connection: Connection[Any], payload: dict[str, Any]
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO author_reputation (
            author_user_id,
            coverage_score,
            freshness_score,
            sourcing_score,
            subscriber_count,
            published_metric_count,
            computed_at,
            methodology_version
        ) VALUES (
            %s::uuid, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (author_user_id) DO UPDATE SET
            coverage_score = EXCLUDED.coverage_score,
            freshness_score = EXCLUDED.freshness_score,
            sourcing_score = EXCLUDED.sourcing_score,
            subscriber_count = EXCLUDED.subscriber_count,
            published_metric_count = EXCLUDED.published_metric_count,
            computed_at = EXCLUDED.computed_at,
            methodology_version = EXCLUDED.methodology_version
        RETURNING
            author_user_id::text AS author_user_id,
            coverage_score,
            freshness_score,
            sourcing_score,
            subscriber_count,
            published_metric_count,
            computed_at,
            methodology_version
        """,
        (
            payload["author_user_id"],
            payload["coverage_score"],
            payload["freshness_score"],
            payload["sourcing_score"],
            payload["subscriber_count"],
            payload["published_metric_count"],
            payload["computed_at"],
            payload["methodology_version"],
        ),
    )


def get_author_reputation(
    connection: Connection[Any], author_user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            author_user_id::text AS author_user_id,
            coverage_score,
            freshness_score,
            sourcing_score,
            subscriber_count,
            published_metric_count,
            computed_at,
            methodology_version
        FROM author_reputation
        WHERE author_user_id::text = %s
        """,
        (author_user_id,),
    )


def list_stale_author_reputation(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            author_user_id::text AS author_user_id,
            computed_at,
            EXTRACT(EPOCH FROM (NOW() - computed_at)) / 86400 AS days_old
        FROM author_reputation
        WHERE computed_at < NOW() - INTERVAL '30 days'
        ORDER BY computed_at ASC
        """,
    )

from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


REQUIRED_NUMERIC_PARAMETER_SQL = """
    VALUES
        ('score_label.weak_below', 0::numeric, 100::numeric),
        ('score_label.limited_below', 0::numeric, 100::numeric),
        ('score_label.moderate_below', 0::numeric, 100::numeric),
        ('score_label.strong_below', 0::numeric, 100::numeric),
        ('strength.min_score', 0::numeric, 100::numeric),
        ('weakness.max_score', 0::numeric, 100::numeric),
        ('confidence.high_min_average', 1::numeric, 3::numeric),
        ('confidence.medium_min_average', 1::numeric, 3::numeric),
        ('recommendation.tie_delta_below', 0::numeric, 100::numeric),
        ('recommendation.medium_confidence_delta_below', 0::numeric, 100::numeric),
        ('board.max_active_posts', 1::numeric, 1000::numeric),
        ('board.max_contact_requests_per_day', 1::numeric, 1000::numeric),
        ('board.max_reports_per_day', 1::numeric, 1000::numeric),
        ('flows.k_anonymity', 1::numeric, 100000::numeric),
        ('trip.warning.high_impact_min_rank', 1::numeric, 4::numeric),
        ('trip.warning.restrictive_pair_severity_rank', 1::numeric, 4::numeric),
        ('trip.warning.missing_pair_severity_rank', 1::numeric, 4::numeric)
"""


def list_missing_required_methodology_parameters(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        f"""
        WITH active_version AS (
            SELECT version
            FROM methodology_parameters
            WHERE effective_from <= NOW()
            GROUP BY version
            ORDER BY MAX(effective_from) DESC, version DESC
            LIMIT 1
        ),
        required(param_key, min_value, max_value) AS (
            {REQUIRED_NUMERIC_PARAMETER_SQL}
        )
        SELECT
            COALESCE(av.version, '') AS version,
            required.param_key
        FROM required
        LEFT JOIN active_version av ON TRUE
        LEFT JOIN methodology_parameters mp
            ON mp.version = av.version
            AND mp.param_key = required.param_key
            AND mp.effective_from <= NOW()
        WHERE av.version IS NULL
           OR mp.id IS NULL
        ORDER BY required.param_key
        """,
    )


def list_methodology_parameters_out_of_range(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        f"""
        WITH active_version AS (
            SELECT version
            FROM methodology_parameters
            WHERE effective_from <= NOW()
            GROUP BY version
            ORDER BY MAX(effective_from) DESC, version DESC
            LIMIT 1
        ),
        required(param_key, min_value, max_value) AS (
            {REQUIRED_NUMERIC_PARAMETER_SQL}
        )
        SELECT
            av.version,
            required.param_key,
            mp.value_numeric,
            required.min_value,
            required.max_value
        FROM active_version av
        JOIN required ON TRUE
        JOIN methodology_parameters mp
            ON mp.version = av.version
            AND mp.param_key = required.param_key
            AND mp.effective_from <= NOW()
        WHERE mp.value_numeric IS NULL
           OR mp.value_numeric < required.min_value
           OR mp.value_numeric > required.max_value
        ORDER BY required.param_key
        """,
    )


def list_invalid_methodology_threshold_order(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        WITH active_version AS (
            SELECT version
            FROM methodology_parameters
            WHERE effective_from <= NOW()
            GROUP BY version
            ORDER BY MAX(effective_from) DESC, version DESC
            LIMIT 1
        ),
        params AS (
            SELECT
                av.version,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'score_label.weak_below'
                ) AS weak_below,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'score_label.limited_below'
                ) AS limited_below,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'score_label.moderate_below'
                ) AS moderate_below,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'score_label.strong_below'
                ) AS strong_below,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'confidence.medium_min_average'
                ) AS confidence_medium,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'confidence.high_min_average'
                ) AS confidence_high,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'recommendation.tie_delta_below'
                ) AS recommendation_tie,
                MAX(mp.value_numeric) FILTER (
                    WHERE mp.param_key = 'recommendation.medium_confidence_delta_below'
                ) AS recommendation_medium
            FROM active_version av
            JOIN methodology_parameters mp
                ON mp.version = av.version
                AND mp.effective_from <= NOW()
            GROUP BY av.version
        )
        SELECT *
        FROM params
        WHERE NOT (
            weak_below < limited_below
            AND limited_below < moderate_below
            AND moderate_below < strong_below
            AND confidence_medium < confidence_high
            AND recommendation_tie < recommendation_medium
        )
        """,
    )

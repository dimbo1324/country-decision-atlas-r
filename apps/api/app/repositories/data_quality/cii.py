from app.repositories import data_quality as data_quality_repository
from app.repositories.data_quality._shared import (
    MVP_COUNTRY_SLUGS,
    MVP_SCENARIO_SLUGS,
)
from psycopg import Connection
from typing import Any


def list_mvp_countries_missing_cii(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT c.slug AS country_slug
        FROM countries c
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM country_cii_scores ccs
              WHERE ccs.country_id = c.id AND ccs.version = 'v1.0'
          )
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_scores_missing_formula_metadata(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.formula_version,
            ccs.aggregation_method
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND (
              ccs.formula_version IS NULL
              OR ccs.formula_version = ''
              OR ccs.aggregation_method IS NULL
              OR ccs.aggregation_method = ''
          )
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_metric_weights_with_invalid_sum(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            version,
            scenario_slug,
            ROUND(SUM(weight)::numeric, 4) AS weight_sum
        FROM scenario_metric_weights
        GROUP BY version, scenario_slug
        HAVING ABS(SUM(weight) - 1.0) > 0.001
        ORDER BY version, scenario_slug
        """,
        (),
    )


def list_mvp_scenarios_missing_cii_weights(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT expected.scenario_slug, m.slug AS metric_slug
        FROM unnest(%s::text[]) AS expected(scenario_slug)
        CROSS JOIN cii_metric_definitions m
        LEFT JOIN scenario_metric_weights smw
            ON smw.scenario_slug = expected.scenario_slug
           AND smw.metric_id = m.id
           AND smw.version = 'v1.0'
        WHERE m.is_active = TRUE
          AND smw.id IS NULL
        ORDER BY expected.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_cii_scenario_weights_with_negative_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT smw.scenario_slug, m.slug AS metric_slug, smw.weight::float AS weight
        FROM scenario_metric_weights smw
        JOIN cii_metric_definitions m ON m.id = smw.metric_id
        WHERE smw.scenario_slug = ANY(%s)
          AND smw.weight < 0
        ORDER BY smw.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_cii_scenario_weights_exceeding_one(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT smw.scenario_slug, m.slug AS metric_slug, smw.weight::float AS weight
        FROM scenario_metric_weights smw
        JOIN cii_metric_definitions m ON m.id = smw.metric_id
        WHERE smw.scenario_slug = ANY(%s)
          AND smw.weight > 1
        ORDER BY smw.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_mvp_scenarios_missing_cii_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT expected_c.country_slug, expected_s.scenario_slug
        FROM unnest(%s::text[]) AS expected_c(country_slug)
        CROSS JOIN unnest(%s::text[]) AS expected_s(scenario_slug)
        LEFT JOIN countries c
            ON c.slug = expected_c.country_slug AND c.is_active = TRUE
        LEFT JOIN country_cii_scores ccs
            ON ccs.country_id = c.id
           AND ccs.scenario_slug = expected_s.scenario_slug
           AND ccs.version = 'v1.0'
        WHERE c.id IS NULL OR ccs.id IS NULL
        ORDER BY expected_c.country_slug, expected_s.scenario_slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_cii_scenario_scores_missing_formula_metadata(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.scenario_slug,
            ccs.formula_version,
            ccs.aggregation_method
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND ccs.scenario_slug = ANY(%s)
          AND (
              ccs.formula_version IS NULL
              OR ccs.formula_version = ''
              OR ccs.aggregation_method IS NULL
              OR ccs.aggregation_method = ''
          )
        ORDER BY c.slug, ccs.scenario_slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_mvp_metrics_missing_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            expected.country_slug,
            m.slug AS metric_slug
        FROM unnest(%s::text[]) AS expected(country_slug)
        CROSS JOIN cii_metric_definitions m
        LEFT JOIN country_metric_values cmv
            ON cmv.country_id = (
                SELECT id FROM countries
                WHERE slug = expected.country_slug AND is_active = TRUE
                LIMIT 1
            )
            AND cmv.metric_id = m.id
        WHERE m.is_active = TRUE
          AND cmv.id IS NULL
        ORDER BY expected.country_slug, m.display_order
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_scores_out_of_range(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.overall_score
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND (ccs.overall_score < 0 OR ccs.overall_score > 100)
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_inactive_mvp_scenarios(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT expected.scenario_slug
        FROM unnest(%s::text[]) AS expected(scenario_slug)
        LEFT JOIN scenarios s
            ON s.slug = expected.scenario_slug
            AND s.is_active = TRUE
        WHERE s.id IS NULL
        ORDER BY expected.scenario_slug
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_cii_scores_with_non_geometric_aggregation(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.scenario_slug,
            ccs.aggregation_method
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND ccs.scenario_slug = ANY(%s)
          AND ccs.aggregation_method IS NOT NULL
          AND ccs.aggregation_method <> 'geometric'
        ORDER BY c.slug, ccs.scenario_slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_cii_metric_definitions_without_polarity(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT slug, polarity
        FROM cii_metric_definitions
        WHERE is_active = TRUE
          AND (polarity IS NULL OR polarity = '')
        ORDER BY display_order
        """,
    )

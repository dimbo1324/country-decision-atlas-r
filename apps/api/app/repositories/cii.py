from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def get_country_cii(
    connection: Connection[Any],
    country_slug: str,
    version: str = "v1.0",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            ccs.overall_score::float AS overall_score,
            ccs.confidence,
            ccs.drift::float AS drift,
            ccs.version,
            ccs.formula_version,
            ccs.aggregation_method,
            ccs.metric_scores AS metrics,
            ccs.calculated_at
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = %s
          AND ccs.version = %s
        """,
        (country_slug, version),
    )


def get_cii_for_countries(
    connection: Connection[Any],
    country_slugs: list[str],
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            c.name AS country_name,
            c.iso2,
            ccs.overall_score::float AS cii_score,
            ccs.confidence AS cii_confidence,
            ccs.drift::float AS country_drift,
            ccs.formula_version,
            ccs.aggregation_method
        FROM countries c
        LEFT JOIN country_cii_scores ccs
            ON ccs.country_id = c.id AND ccs.version = %s
        WHERE c.slug = ANY(%s)
        ORDER BY c.slug
        """,
        (version, country_slugs),
    )


def get_active_cii_metric_definitions(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            slug,
            name_en,
            name_ru,
            polarity,
            display_order
        FROM cii_metric_definitions
        WHERE is_active = TRUE
        ORDER BY display_order
        """,
        (),
    )


def get_cii_metric_values_for_countries(
    connection: Connection[Any],
    country_slugs: list[str],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            m.slug AS metric_slug,
            cmv.normalized_value::float AS value,
            m.polarity
        FROM country_metric_values cmv
        JOIN countries c ON c.id = cmv.country_id
        JOIN cii_metric_definitions m ON m.id = cmv.metric_id
        WHERE c.slug = ANY(%s)
          AND m.is_active = TRUE
        ORDER BY c.slug, m.display_order
        """,
        (country_slugs,),
    )


def get_scenario_for_cii_comparison(
    connection: Connection[Any],
    scenario_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            s.slug,
            COALESCE(lv.text, s.name) AS title
        FROM scenarios s
        LEFT JOIN translation_units tu
            ON tu.entity_type = 'scenario'
            AND tu.entity_id::uuid = s.id
            AND tu.field_name = 'name'
        LEFT JOIN translation_variants lv
            ON lv.translation_unit_id = tu.id
            AND lv.locale_code = %s
            AND lv.status IN ('machine_translated', 'human_reviewed')
        WHERE s.slug = %s
        """,
        (locale, scenario_slug),
    )

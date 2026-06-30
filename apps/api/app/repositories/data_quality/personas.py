from app.repositories import data_quality as data_quality_repository
from app.repositories.data_quality._shared import (
    MVP_SCENARIO_SLUGS,
)
from psycopg import Connection
from typing import Any


def list_active_personas_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT p.slug AS persona_slug, missing.missing_field
        FROM personas p
        CROSS JOIN LATERAL (
            VALUES
                ('slug', p.slug),
                ('name', p.name),
                ('name_ru', p.name_ru)
        ) AS missing(missing_field, field_value)
        WHERE p.is_active = TRUE
          AND COALESCE(BTRIM(missing.field_value), '') = ''
        ORDER BY p.display_order, p.slug, missing.missing_field
        """,
        (),
    )


def list_active_personas_missing_metric_modifiers(
    connection: Connection[Any],
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            p.slug AS persona_slug,
            m.slug AS metric_slug,
            %s::text AS version
        FROM personas p
        CROSS JOIN cii_metric_definitions m
        LEFT JOIN persona_metric_modifiers pmm
            ON pmm.persona_slug = p.slug
            AND pmm.metric_id = m.id
            AND pmm.version = %s
        WHERE p.is_active = TRUE
          AND m.is_active = TRUE
          AND pmm.id IS NULL
        ORDER BY p.display_order, p.slug, m.display_order
        """,
        (version, version),
    )


def list_persona_modifiers_out_of_range(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            pmm.persona_slug,
            m.slug AS metric_slug,
            pmm.modifier::float AS modifier,
            pmm.version
        FROM persona_metric_modifiers pmm
        JOIN cii_metric_definitions m ON m.id = pmm.metric_id
        WHERE pmm.modifier < -0.5
           OR pmm.modifier > 0.5
        ORDER BY pmm.persona_slug, m.display_order, pmm.version
        """,
        (),
    )


def list_inactive_personas_with_modifiers(
    connection: Connection[Any],
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            p.slug AS persona_slug,
            COUNT(pmm.id)::int AS modifier_count,
            %s::text AS version
        FROM personas p
        JOIN persona_metric_modifiers pmm
            ON pmm.persona_slug = p.slug
            AND pmm.version = %s
        WHERE p.is_active = FALSE
        GROUP BY p.slug
        ORDER BY p.slug
        """,
        (version, version),
    )


def list_active_personas_missing_descriptions(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT p.slug AS persona_slug, missing.missing_field
        FROM personas p
        CROSS JOIN LATERAL (
            VALUES
                ('description', p.description),
                ('description_ru', p.description_ru)
        ) AS missing(missing_field, field_value)
        WHERE p.is_active = TRUE
          AND COALESCE(BTRIM(missing.field_value), '') = ''
        ORDER BY p.display_order, p.slug, missing.missing_field
        """,
        (),
    )


def list_persona_adjusted_weight_inputs(
    connection: Connection[Any],
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            p.slug AS persona_slug,
            scenario_scope.scenario_slug,
            m.id::text AS metric_id,
            m.slug AS metric_slug,
            m.name_en AS metric_name,
            smw.weight::float AS base_weight,
            pmm.modifier::float AS modifier,
            %s::text AS version
        FROM personas p
        CROSS JOIN unnest(%s::text[]) AS scenario_scope(scenario_slug)
        JOIN scenario_metric_weights smw
            ON smw.scenario_slug = scenario_scope.scenario_slug
            AND smw.version = %s
        JOIN cii_metric_definitions m
            ON m.id = smw.metric_id
            AND m.is_active = TRUE
        LEFT JOIN persona_metric_modifiers pmm
            ON pmm.persona_slug = p.slug
            AND pmm.metric_id = m.id
            AND pmm.version = %s
        WHERE p.is_active = TRUE
        ORDER BY p.display_order, p.slug, scenario_scope.scenario_slug, m.display_order
        """,
        (version, list(MVP_SCENARIO_SLUGS), version, version),
    )

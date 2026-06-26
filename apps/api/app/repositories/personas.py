from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def list_personas(conn: Connection[Any], locale: str) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            p.id,
            p.slug,
            CASE
                WHEN %s = 'ru' THEN p.name_ru
                ELSE p.name
            END AS name,
            CASE
                WHEN %s = 'ru' THEN COALESCE(p.description_ru, p.description)
                ELSE COALESCE(p.description, p.description_ru)
            END AS description,
            p.is_active,
            p.display_order
        FROM personas p
        WHERE p.is_active = TRUE
        ORDER BY p.display_order, p.slug
        """,
        (locale, locale),
    )


def get_persona_by_slug(
    conn: Connection[Any],
    persona_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        SELECT
            p.id,
            p.slug,
            CASE
                WHEN %s = 'ru' THEN p.name_ru
                ELSE p.name
            END AS name,
            CASE
                WHEN %s = 'ru' THEN COALESCE(p.description_ru, p.description)
                ELSE COALESCE(p.description, p.description_ru)
            END AS description,
            p.is_active,
            p.display_order
        FROM personas p
        WHERE p.slug = %s
          AND p.is_active = TRUE
        """,
        (locale, locale, persona_slug),
    )


def list_persona_modifiers(
    conn: Connection[Any],
    persona_slug: str,
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            pmm.persona_slug,
            pmm.version,
            pmm.metric_id,
            cmd.slug AS metric_slug,
            cmd.name_en AS metric_name,
            pmm.modifier
        FROM persona_metric_modifiers pmm
        INNER JOIN cii_metric_definitions cmd
            ON cmd.id = pmm.metric_id
            AND cmd.is_active = TRUE
        WHERE pmm.persona_slug = %s
          AND pmm.version = %s
        ORDER BY cmd.display_order
        """,
        (persona_slug, version),
    )


def list_active_persona_slugs(conn: Connection[Any]) -> list[str]:
    rows = fetch_all(
        conn,
        """
        SELECT slug
        FROM personas
        WHERE is_active = TRUE
        ORDER BY display_order, slug
        """,
        (),
    )
    return [row["slug"] for row in rows]


def list_active_cii_metrics(conn: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            id,
            slug,
            name_en AS name,
            polarity,
            display_order
        FROM cii_metric_definitions
        WHERE is_active = TRUE
        ORDER BY display_order
        """,
        (),
    )


def list_base_scenario_weights(
    conn: Connection[Any],
    scenario_slug: str,
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            smw.scenario_slug,
            smw.version,
            smw.metric_id,
            cmd.slug AS metric_slug,
            smw.weight AS base_weight
        FROM scenario_metric_weights smw
        INNER JOIN cii_metric_definitions cmd
            ON cmd.id = smw.metric_id
            AND cmd.is_active = TRUE
        WHERE smw.scenario_slug = %s
          AND smw.version = %s
        ORDER BY cmd.display_order
        """,
        (scenario_slug, version),
    )


def list_persona_weight_inputs(
    conn: Connection[Any],
    scenario_slug: str,
    persona_slug: str,
    version: str = "v1.0",
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            smw.metric_id,
            cmd.slug AS metric_slug,
            cmd.name_en AS metric_name,
            smw.weight AS base_weight,
            pmm.modifier
        FROM scenario_metric_weights smw
        INNER JOIN cii_metric_definitions cmd
            ON cmd.id = smw.metric_id
            AND cmd.is_active = TRUE
        LEFT JOIN persona_metric_modifiers pmm
            ON pmm.metric_id = smw.metric_id
            AND pmm.persona_slug = %s
            AND pmm.version = %s
        WHERE smw.scenario_slug = %s
          AND smw.version = %s
        ORDER BY cmd.display_order
        """,
        (persona_slug, version, scenario_slug, version),
    )

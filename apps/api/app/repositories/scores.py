from app.core.database import fetch_all, fetch_one
from app.schemas.common import localized_column, validate_locale
from psycopg import Connection
from typing import Any


def list_country_scores(
    connection: Connection[Any],
    country_id: str,
    locale: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    scenario_name_column = localized_column(
        requested_locale, "s.title_en", "s.title_ru"
    )
    summary_column = localized_column(
        requested_locale, "cs.explanation_en", "cs.explanation_ru"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            cs.id,
            cs.country_id,
            cs.scenario_id,
            s.slug AS scenario_slug,
            COALESCE({scenario_name_column}, t_name.translated_value, s.name, '') AS scenario_name,
            cs.score::float AS score,
            cs.score_label,
            COALESCE({summary_column}, cs.summary, '') AS summary,
            cs.created_at,
            cs.updated_at,
            {scenario_name_column} IS NOT NULL AND {summary_column} IS NOT NULL AS is_translated,
            CASE
                WHEN {scenario_name_column} IS NOT NULL AND {summary_column} IS NOT NULL THEN 'exact'
                WHEN s.title_en IS NOT NULL OR cs.explanation_en IS NOT NULL OR s.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN locales l ON l.code = %s
        LEFT JOIN translations t_name
            ON t_name.entity_type = 'scenario'
            AND t_name.entity_id = s.id
            AND t_name.field_name = 'name'
            AND t_name.locale_id = l.id
            AND t_name.status IN ('reviewed', 'approved')
        WHERE c.id::text = %s OR c.slug = %s
        ORDER BY s.slug
        LIMIT %s OFFSET %s
        """,
        (requested_locale.value, country_id, country_id, limit, offset),
    )


def count_country_scores(connection: Connection[Any], country_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        WHERE c.id::text = %s OR c.slug = %s
        """,
        (country_id, country_id),
    )
    return int(row["total"]) if row else 0


def run_scenario(
    connection: Connection[Any],
    scenario_slug: str,
    country_ids: list[str],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id AS country_id,
            c.slug AS country_slug,
            cs.score::float AS score,
            cs.score_label,
            cs.summary
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        WHERE s.slug = %s AND c.id = ANY(%s::uuid[])
        ORDER BY cs.score DESC, c.slug
        """,
        (scenario_slug, country_ids),
    )

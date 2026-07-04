from app.core.database import fetch_all, fetch_one
from app.core.locales import SOURCE_LOCALE, validate_locale
from psycopg import Connection
from typing import Any


def list_scenarios(
    connection: Connection[Any],
    locale: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    if requested_locale == SOURCE_LOCALE:
        name_column = "s.name"
        resolved_locale_sql = "'en'"
        status_sql = (
            "CASE WHEN s.name IS NOT NULL THEN 'source' ELSE 'missing' END"
        )
    else:
        name_column = "COALESCE(t_name.translated_value, s.name)"
        resolved_locale_sql = "CASE WHEN t_name.translated_value IS NOT NULL THEN 'ru' ELSE 'en' END"
        status_sql = """
            CASE
                WHEN t_name.translated_value IS NOT NULL THEN 'translated'
                WHEN s.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    rows = fetch_all(
        connection,
        f"""
        SELECT
            s.id,
            s.slug,
            {name_column} AS name,
            s.description,
            s.is_active,
            s.created_at,
            s.updated_at,
            t_name.translated_value IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM scenarios s
        LEFT JOIN locales l ON l.code = %s
        LEFT JOIN translations t_name
            ON t_name.entity_type = 'scenario'
            AND t_name.entity_id = s.id
            AND t_name.field_name = 'name'
            AND t_name.locale_id = l.id
            AND t_name.status IN ('reviewed', 'approved')
        WHERE s.is_active = TRUE
        ORDER BY s.slug
        LIMIT %s OFFSET %s
        """,
        (requested_locale, limit, offset),
    )
    criteria = fetch_all(
        connection,
        """
        SELECT
            sc.id,
            sc.scenario_id,
            sc.key,
            sc.label,
            sc.weight::float AS weight,
            sc.is_required,
            sc.created_at,
            sc.updated_at
        FROM scenario_criteria sc
        ORDER BY sc.key
        """,
    )
    criteria_by_scenario: dict[str, list[dict[str, Any]]] = {}
    for criterion in criteria:
        criteria_by_scenario.setdefault(
            str(criterion["scenario_id"]), []
        ).append(criterion)
    for row in rows:
        row["criteria"] = criteria_by_scenario.get(str(row["id"]), [])
    return rows


def count_scenarios(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM scenarios WHERE is_active = TRUE",
    )
    return int(row["total"]) if row else 0

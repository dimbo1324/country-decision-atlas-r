from typing import Any
from app.core.database import fetch_all, fetch_one
from psycopg import Connection
COUNTRY_SELECT = """
SELECT
    c.id,
    c.slug,
    c.iso2,
    c.iso3,
    COALESCE(t_name.translated_value, c.name) AS name,
    c.official_name,
    c.region,
    c.subregion,
    c.capital,
    c.currency_code,
    c.is_active,
    c.created_at,
    c.updated_at,
    t_name.translated_value IS NOT NULL AS is_translated
FROM countries c
LEFT JOIN locales l ON l.code = %s
LEFT JOIN translations t_name
    ON t_name.entity_type = 'country'
    AND t_name.entity_id = c.id
    AND t_name.field_name = 'name'
    AND t_name.locale_id = l.id
    AND t_name.status IN ('reviewed', 'approved')
"""
def list_countries(
    connection: Connection[Any],
    locale: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        COUNTRY_SELECT
        + """
        WHERE c.is_active = TRUE
        ORDER BY c.name
        LIMIT %s OFFSET %s
        """,
        (locale, limit, offset),
    )
def count_countries(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM countries WHERE is_active = TRUE")
    return int(row["total"]) if row else 0
def get_country(
    connection: Connection[Any],
    country_id: str,
    locale: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        COUNTRY_SELECT
        + """
        WHERE c.id::text = %s OR c.slug = %s
        """,
        (locale, country_id, country_id),
    )
def get_profile(
    connection: Connection[Any],
    country_id: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            cp.id,
            cp.country_id,
            cp.summary,
            cp.residence_overview,
            cp.citizenship_overview,
            cp.tax_overview,
            cp.business_overview,
            cp.quality_of_life_overview,
            cp.risk_overview,
            cp.created_at,
            cp.updated_at
        FROM country_profiles cp
        JOIN countries c ON c.id = cp.country_id
        WHERE c.id::text = %s OR c.slug = %s
        """,
        (country_id, country_id),
    )

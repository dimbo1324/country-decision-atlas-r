from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


VALUE_SELECT = """
    amv.id::text AS id,
    amv.metric_id::text AS metric_id,
    amv.country_id::text AS country_id,
    c.slug AS country_slug,
    COALESCE(c.name, c.slug) AS country_name,
    amv.value,
    amv.source_url,
    amv.is_personal_experience,
    amv.note,
    amv.valid_as_of,
    amv.created_at,
    amv.updated_at
"""

VALUE_JOINS = """
FROM author_metric_values amv
JOIN countries c ON c.id = amv.country_id
"""


def upsert_value(
    connection: Connection[Any],
    *,
    metric_id: str,
    country_id: str,
    value: float,
    source_url: str | None,
    is_personal_experience: bool,
    note: str | None,
    valid_as_of: Any,
) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO author_metric_values (
            metric_id,
            country_id,
            value,
            source_url,
            is_personal_experience,
            note,
            valid_as_of
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s)
        ON CONFLICT (metric_id, country_id) DO UPDATE SET
            value = EXCLUDED.value,
            source_url = EXCLUDED.source_url,
            is_personal_experience = EXCLUDED.is_personal_experience,
            note = EXCLUDED.note,
            valid_as_of = EXCLUDED.valid_as_of,
            updated_at = NOW()
        """,
        (
            metric_id,
            country_id,
            value,
            source_url,
            is_personal_experience,
            note,
            valid_as_of,
        ),
    )
    value_row = get_value(
        connection, metric_id=metric_id, country_id=country_id
    )
    if value_row is None:
        raise RuntimeError(
            "Expected author metric value to exist after upsert."
        )
    return value_row


def get_value(
    connection: Connection[Any], *, metric_id: str, country_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {VALUE_SELECT}
        {VALUE_JOINS}
        WHERE amv.metric_id = %s::uuid AND amv.country_id = %s::uuid
        """,
        (metric_id, country_id),
    )


def list_values_for_definition(
    connection: Connection[Any], metric_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {VALUE_SELECT}
        {VALUE_JOINS}
        WHERE amv.metric_id = %s::uuid
        ORDER BY c.slug
        """,
        (metric_id,),
    )


def count_countries_with_values(
    connection: Connection[Any], metric_id: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM author_metric_values
        WHERE metric_id = %s::uuid
        """,
        (metric_id,),
    )
    return int(row["total"]) if row else 0

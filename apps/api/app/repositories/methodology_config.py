from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


PARAMETER_FIELDS = """
    id::text AS id,
    version,
    param_key,
    value_numeric,
    value_json,
    description,
    effective_from,
    created_at
"""


def get_active_methodology_version(
    connection: Connection[Any],
) -> str | None:
    row = fetch_one(
        connection,
        """
        SELECT version
        FROM methodology_parameters
        WHERE effective_from <= NOW()
        GROUP BY version
        ORDER BY MAX(effective_from) DESC, version DESC
        LIMIT 1
        """,
    )
    return str(row["version"]) if row else None


def list_parameters_for_version(
    connection: Connection[Any], version: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {PARAMETER_FIELDS}
        FROM methodology_parameters
        WHERE version = %s
          AND effective_from <= NOW()
        ORDER BY param_key
        """,
        (version,),
    )

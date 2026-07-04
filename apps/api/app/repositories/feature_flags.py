from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


FEATURE_FLAG_FIELDS = """
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled,
    metadata,
    created_at,
    updated_at
"""


FEATURE_ACCESS_RULE_FIELDS = """
    feature_key,
    access_tier,
    is_enabled,
    metadata,
    created_at
"""


def list_feature_flags(conn: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT
            {FEATURE_FLAG_FIELDS}
        FROM feature_flags
        ORDER BY key
        """,
        (),
    )


def get_feature_flag(
    conn: Connection[Any], feature_key: str
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        SELECT
            {FEATURE_FLAG_FIELDS}
        FROM feature_flags
        WHERE key = %s
        """,
        (feature_key,),
    )


def list_feature_access_rules(
    conn: Connection[Any], feature_key: str
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT
            {FEATURE_ACCESS_RULE_FIELDS}
        FROM feature_access_rules
        WHERE feature_key = %s
        ORDER BY access_tier
        """,
        (feature_key,),
    )


def list_all_feature_access_rules(
    conn: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT
            {FEATURE_ACCESS_RULE_FIELDS}
        FROM feature_access_rules
        ORDER BY feature_key, access_tier
        """,
        (),
    )


def count_feature_flags(conn: Connection[Any]) -> int:
    row = fetch_one(conn, "SELECT COUNT(*) AS total FROM feature_flags", ())
    return int(row["total"]) if row else 0

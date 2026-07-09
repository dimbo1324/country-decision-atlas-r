from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


CAPABILITY_FIELDS = """
    id::text AS id,
    user_id::text AS user_id,
    capability,
    granted_by::text AS granted_by,
    granted_at,
    revoked_at,
    note
"""


def has_active_grant(
    connection: Connection[Any], user_id: str, capability: str
) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM user_capabilities
        WHERE user_id = %s::uuid
          AND capability = %s
          AND revoked_at IS NULL
        """,
        (user_id, capability),
    )
    return row is not None


def grant_capability(
    connection: Connection[Any],
    *,
    user_id: str,
    capability: str,
    granted_by: str,
    note: str | None,
) -> dict[str, Any]:
    row = fetch_one(
        connection,
        f"""
        INSERT INTO user_capabilities (
            user_id,
            capability,
            granted_by,
            note
        )
        VALUES (%s::uuid, %s, %s::uuid, %s)
        ON CONFLICT (user_id, capability) DO UPDATE
        SET
            granted_by = EXCLUDED.granted_by,
            granted_at = NOW(),
            revoked_at = NULL,
            note = EXCLUDED.note
        RETURNING
            {CAPABILITY_FIELDS}
        """,
        (user_id, capability, granted_by, note),
    )
    assert row is not None
    return row


def revoke_capability_by_id(
    connection: Connection[Any], capability_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE user_capabilities
        SET revoked_at = NOW()
        WHERE id = %s::uuid
          AND revoked_at IS NULL
        RETURNING
            {CAPABILITY_FIELDS}
        """,
        (capability_id,),
    )


def get_capability_by_id(
    connection: Connection[Any], capability_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {CAPABILITY_FIELDS}
        FROM user_capabilities
        WHERE id = %s::uuid
        """,
        (capability_id,),
    )


def list_capabilities(
    connection: Connection[Any],
    *,
    user_id: str | None,
    capability: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if user_id is not None:
        filters.append("user_id = %s::uuid")
        params.append(user_id)
    if capability is not None:
        filters.append("capability = %s")
        params.append(capability)
    if active_only:
        filters.append("revoked_at IS NULL")
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            {CAPABILITY_FIELDS},
            COUNT(*) OVER() AS total_count
        FROM user_capabilities
        WHERE {where_sql}
        ORDER BY granted_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )

import json
from app.core.database import execute_one, fetch_all
from collections.abc import Mapping
from psycopg import Connection
from typing import Any
from uuid import UUID


def insert_audit_event(
    conn: Connection[Any],
    *,
    entity_type: str,
    entity_id: UUID,
    action: str,
    changed_by: str,
    changes: Mapping[str, Any],
) -> dict[str, Any]:
    return execute_one(
        conn,
        """
        INSERT INTO audit_events (
            entity_type,
            entity_id,
            action,
            changed_by,
            changes
        )
        VALUES (%s, %s::uuid, %s, %s, %s::jsonb)
        RETURNING
            id,
            entity_type,
            entity_id,
            action,
            changed_by,
            changed_at,
            changes
        """,
        (
            entity_type,
            str(entity_id),
            action,
            changed_by,
            json.dumps(dict(changes), default=str),
        ),
    )


def list_audit_events(
    connection: Connection[Any],
    *,
    entity_type: str | None,
    action: str | None,
    changed_by: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if entity_type is not None:
        filters.append("entity_type = %s")
        params.append(entity_type)
    if action is not None:
        filters.append("action = %s")
        params.append(action)
    if changed_by is not None:
        filters.append("changed_by = %s")
        params.append(changed_by)
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            id,
            entity_type,
            entity_id,
            action,
            changed_by,
            changed_at,
            changes,
            COUNT(*) OVER() AS total_count
        FROM audit_events
        WHERE {where_sql}
        ORDER BY changed_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )

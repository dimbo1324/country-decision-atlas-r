from app.core.database import execute_one
from collections.abc import Mapping
import json
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

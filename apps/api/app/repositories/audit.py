from app.core.database import execute_one
import json
from psycopg import Connection
from typing import Any


def create_audit_event(
    connection: Connection[Any],
    entity_type: str,
    entity_id: str,
    action: str,
    changed_by: str,
    changes: dict[str, Any],
) -> dict[str, Any]:
    return execute_one(
        connection,
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
            entity_id,
            action,
            changed_by,
            json.dumps(changes, default=str),
        ),
    )

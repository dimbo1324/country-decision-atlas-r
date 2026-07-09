from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


NOTIFICATION_FIELDS = """
    id::text AS id,
    user_id::text AS user_id,
    session_id::text AS session_id,
    event_type,
    device_label,
    ip_display,
    created_at,
    acknowledged_at
"""


def create_new_device_login_notification(
    connection: Connection[Any],
    *,
    user_id: str,
    session_id: str,
    device_label: str | None,
    ip_display: str | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO user_security_notifications (
            user_id, session_id, event_type, device_label, ip_display
        ) VALUES (%s, %s, 'new_device_login', %s, %s)
        RETURNING
            {NOTIFICATION_FIELDS}
        """,
        (user_id, session_id, device_label, ip_display),
    )


def list_unacknowledged_notifications(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {NOTIFICATION_FIELDS}
        FROM user_security_notifications
        WHERE user_id = %s::uuid AND acknowledged_at IS NULL
        ORDER BY created_at DESC
        """,
        (user_id,),
    )


def acknowledge_notification(
    connection: Connection[Any], notification_id: str, user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE user_security_notifications
        SET acknowledged_at = NOW()
        WHERE id = %s::uuid AND user_id = %s::uuid AND acknowledged_at IS NULL
        RETURNING
            {NOTIFICATION_FIELDS}
        """,
        (notification_id, user_id),
    )

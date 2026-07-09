from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from typing import Any


THREAD_FIELDS = """
    ct.id::text AS id,
    ct.contact_request_id::text AS contact_request_id,
    ct.status,
    ct.closed_by_user_id::text AS closed_by_user_id,
    ct.closed_at,
    ct.created_at,
    ct.updated_at,
    mbcr.post_id::text AS post_id,
    mbp.title AS post_title,
    mbcr.from_user_id::text AS from_user_id,
    fu.display_name AS from_user_display_name,
    mbcr.to_user_id::text AS to_user_id,
    tu.display_name AS to_user_display_name
"""

THREAD_JOINS = """
    FROM contact_threads ct
    JOIN migration_board_contact_requests mbcr ON mbcr.id = ct.contact_request_id
    JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
    JOIN users fu ON fu.id = mbcr.from_user_id
    JOIN users tu ON tu.id = mbcr.to_user_id
"""


def create_thread_for_contact_request(
    connection: Connection[Any], contact_request_id: str
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO contact_threads (contact_request_id)
        VALUES (%s::uuid)
        ON CONFLICT (contact_request_id) DO NOTHING
        RETURNING id::text AS id
        """,
        (contact_request_id,),
    )
    if row is None:
        existing = get_thread_for_contact_request(
            connection, contact_request_id
        )
        assert existing is not None
        return existing
    thread = get_thread_by_id(connection, str(row["id"]))
    assert thread is not None
    return thread


def get_thread_by_id(
    connection: Connection[Any], thread_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT {THREAD_FIELDS}
        {THREAD_JOINS}
        WHERE ct.id = %s::uuid
        """,
        (thread_id,),
    )


def get_thread_for_contact_request(
    connection: Connection[Any], contact_request_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT {THREAD_FIELDS}
        {THREAD_JOINS}
        WHERE ct.contact_request_id = %s::uuid
        """,
        (contact_request_id,),
    )


def list_my_threads(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT {THREAD_FIELDS}
        {THREAD_JOINS}
        WHERE mbcr.from_user_id = %s::uuid OR mbcr.to_user_id = %s::uuid
        ORDER BY ct.updated_at DESC
        """,
        (user_id, user_id),
    )


MESSAGE_FIELDS = """
    tm.id::text AS id,
    tm.thread_id::text AS thread_id,
    tm.sender_user_id::text AS sender_user_id,
    u.display_name AS sender_display_name,
    tm.body,
    tm.created_at
"""


def list_messages(
    connection: Connection[Any],
    *,
    thread_id: str,
    after: datetime | None,
    limit: int,
) -> list[dict[str, Any]]:
    if after is not None:
        return fetch_all(
            connection,
            f"""
            SELECT {MESSAGE_FIELDS}
            FROM thread_messages tm
            JOIN users u ON u.id = tm.sender_user_id
            WHERE tm.thread_id = %s::uuid AND tm.created_at > %s
            ORDER BY tm.created_at ASC, tm.id ASC
            LIMIT %s
            """,
            (thread_id, after, limit),
        )
    return fetch_all(
        connection,
        f"""
        SELECT {MESSAGE_FIELDS}
        FROM thread_messages tm
        JOIN users u ON u.id = tm.sender_user_id
        WHERE tm.thread_id = %s::uuid
        ORDER BY tm.created_at ASC, tm.id ASC
        LIMIT %s
        """,
        (thread_id, limit),
    )


def create_message(
    connection: Connection[Any],
    *,
    thread_id: str,
    sender_user_id: str,
    body: str,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO thread_messages (thread_id, sender_user_id, body)
        VALUES (%s::uuid, %s::uuid, %s)
        RETURNING id::text AS id, created_at
        """,
        (thread_id, sender_user_id, body),
    )
    connection.execute(
        "UPDATE contact_threads SET updated_at = NOW() WHERE id = %s::uuid",
        (thread_id,),
    )
    return {
        "id": row["id"],
        "thread_id": thread_id,
        "sender_user_id": sender_user_id,
        "body": body,
        "created_at": row["created_at"],
    }


def count_messages_created_since(
    connection: Connection[Any], user_id: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM thread_messages
        WHERE sender_user_id = %s::uuid AND created_at >= NOW() - INTERVAL '1 day'
        """,
        (user_id,),
    )
    return int(row["total"]) if row else 0


def close_thread(
    connection: Connection[Any], *, thread_id: str, closed_by_user_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE contact_threads
        SET status = 'closed', closed_by_user_id = %s::uuid, closed_at = NOW()
        WHERE id = %s::uuid AND status = 'open'
        RETURNING id::text AS id
        """,
        (closed_by_user_id, thread_id),
    )
    return get_thread_by_id(connection, thread_id) if row is not None else None


def freeze_threads_between_users(
    connection: Connection[Any], *, user_a_id: str, user_b_id: str
) -> int:
    cursor = connection.execute(
        """
        UPDATE contact_threads ct
        SET status = 'frozen'
        FROM migration_board_contact_requests mbcr
        WHERE ct.contact_request_id = mbcr.id
          AND ct.status = 'open'
          AND (
              (mbcr.from_user_id = %s::uuid AND mbcr.to_user_id = %s::uuid)
              OR (mbcr.from_user_id = %s::uuid AND mbcr.to_user_id = %s::uuid)
          )
        """,
        (user_a_id, user_b_id, user_b_id, user_a_id),
    )
    return cursor.rowcount

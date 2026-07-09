from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def create_contact_request(
    connection: Connection[Any],
    *,
    post_id: str,
    from_user_id: str,
    to_user_id: str,
    message: str,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO migration_board_contact_requests (
            post_id,
            from_user_id,
            to_user_id,
            message,
            expires_at
        )
        VALUES (%s::uuid, %s::uuid, %s::uuid, %s, NOW() + INTERVAL '30 days')
        RETURNING id::text AS id
        """,
        (post_id, from_user_id, to_user_id, message),
    )
    request = get_contact_request_by_id(connection, str(row["id"]))
    if request is None:
        raise RuntimeError("Expected contact request to exist after insert.")
    return request


def get_contact_request_by_id(
    connection: Connection[Any], request_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.id = %s::uuid
        """,
        (request_id,),
    )


def list_incoming_contact_requests(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.to_user_id = %s::uuid
          AND NOT EXISTS (
              SELECT 1
              FROM migration_board_blocks mbb
              WHERE mbb.blocker_user_id = mbcr.to_user_id
                AND mbb.blocked_user_id = mbcr.from_user_id
          )
        ORDER BY mbcr.created_at DESC
        """,
        (user_id,),
    )


def list_outgoing_contact_requests(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.from_user_id = %s::uuid
        ORDER BY mbcr.created_at DESC
        """,
        (user_id,),
    )


def update_contact_request_status(
    connection: Connection[Any],
    *,
    request_id: str,
    status: str,
    response_note: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_contact_requests
        SET
            status = %s,
            responded_at = CASE WHEN %s IN ('accepted', 'declined') THEN NOW() ELSE responded_at END,
            cancelled_at = CASE WHEN %s = 'cancelled' THEN NOW() ELSE cancelled_at END,
            response_note = %s
        WHERE id = %s::uuid AND status = 'pending'
        RETURNING id::text AS id
        """,
        (status, status, status, response_note, request_id),
    )
    return (
        get_contact_request_by_id(connection, request_id)
        if row is not None
        else None
    )


def pending_contact_request_exists(
    connection: Connection[Any], *, post_id: str, from_user_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM migration_board_contact_requests
        WHERE post_id = %s::uuid AND from_user_id = %s::uuid AND status = 'pending'
        """,
        (post_id, from_user_id),
    )
    return row is not None


def count_contact_requests_created_since(
    connection: Connection[Any], *, user_id: str, since_sql: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM migration_board_contact_requests
        WHERE from_user_id = %s::uuid AND created_at >= NOW() - INTERVAL '1 day'
        """,
        (user_id,),
    )
    _ = since_sql
    return int(row["total"]) if row else 0

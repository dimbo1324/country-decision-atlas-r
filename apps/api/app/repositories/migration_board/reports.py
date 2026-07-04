from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def create_report(
    connection: Connection[Any],
    *,
    reporter_user_id: str,
    post_id: str | None,
    contact_request_id: str | None,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO migration_board_reports (
            reporter_user_id,
            post_id,
            contact_request_id,
            reason,
            details
        )
        VALUES (%s::uuid, %s::uuid, %s::uuid, %s, %s)
        RETURNING
            id::text AS id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_at,
            resolution_note
        """,
        (reporter_user_id, post_id, contact_request_id, reason, details),
    )


def get_report_by_id(
    connection: Connection[Any], report_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id::text AS id,
            reporter_user_id::text AS reporter_user_id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_by::text AS reviewed_by,
            reviewed_at,
            resolution_note
        FROM migration_board_reports
        WHERE id::text = %s
        """,
        (report_id,),
    )


def list_reports_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if status is not None:
        filters.append("status = %s")
        params.append(status)
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            id::text AS id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_at,
            resolution_note,
            COUNT(*) OVER() AS total_count
        FROM migration_board_reports
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def update_report_status(
    connection: Connection[Any],
    *,
    report_id: str,
    status: str,
    reviewed_by: str,
    resolution_note: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_reports
        SET
            status = %s,
            reviewed_by = %s::uuid,
            reviewed_at = NOW(),
            resolution_note = %s
        WHERE id::text = %s AND status IN ('pending', 'reviewing')
        RETURNING id::text AS id
        """,
        (status, reviewed_by, resolution_note, report_id),
    )
    return get_report_by_id(connection, report_id) if row is not None else None


def existing_pending_report_exists(
    connection: Connection[Any],
    *,
    reporter_user_id: str,
    post_id: str | None,
    contact_request_id: str | None,
) -> bool:
    if post_id is not None:
        row = fetch_one(
            connection,
            """
            SELECT 1
            FROM migration_board_reports
            WHERE reporter_user_id::text = %s
              AND post_id::text = %s
              AND status IN ('pending', 'reviewing')
            """,
            (reporter_user_id, post_id),
        )
        return row is not None
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM migration_board_reports
        WHERE reporter_user_id::text = %s
          AND contact_request_id::text = %s
          AND status IN ('pending', 'reviewing')
        """,
        (reporter_user_id, contact_request_id),
    )
    return row is not None


def count_reports_created_today(
    connection: Connection[Any], user_id: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM migration_board_reports
        WHERE reporter_user_id::text = %s AND created_at >= NOW() - INTERVAL '1 day'
        """,
        (user_id,),
    )
    return int(row["total"]) if row else 0

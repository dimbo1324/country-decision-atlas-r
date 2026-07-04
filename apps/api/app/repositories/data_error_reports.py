from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


DATA_ERROR_REPORT_FIELDS = """
    id,
    entity_type,
    entity_id,
    country_slug,
    route_id,
    report_type,
    message,
    status,
    created_by_identity_type,
    created_by_identity_id,
    created_at,
    reviewed_at,
    reviewed_by,
    resolution_note
"""


def insert_data_error_report(
    conn: Connection[Any],
    *,
    entity_type: str,
    entity_id: str | None,
    country_slug: str | None,
    route_id: str | None,
    report_type: str,
    message: str,
    created_by_identity_type: str,
    created_by_identity_id: str,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO data_error_reports (
            entity_type,
            entity_id,
            country_slug,
            route_id,
            report_type,
            message,
            created_by_identity_type,
            created_by_identity_id
        )
        VALUES (%s, %s::uuid, %s, %s::uuid, %s, %s, %s, %s)
        RETURNING {DATA_ERROR_REPORT_FIELDS}
        """,
        (
            entity_type,
            entity_id,
            country_slug,
            route_id,
            report_type,
            message,
            created_by_identity_type,
            created_by_identity_id,
        ),
    )
    if row is None:
        raise RuntimeError(
            "Expected data_error_reports insert to return a row."
        )
    return row


def get_data_error_report(
    conn: Connection[Any], report_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        SELECT {DATA_ERROR_REPORT_FIELDS}
        FROM data_error_reports
        WHERE id = %s::uuid
        """,
        (report_id,),
    )


def list_data_error_reports_for_admin(
    conn: Connection[Any],
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {DATA_ERROR_REPORT_FIELDS}
        FROM data_error_reports
        WHERE (%s::text IS NULL OR status = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, limit),
    )


def update_data_error_report_status(
    conn: Connection[Any],
    report_id: str,
    status: str,
    reviewed_by: str | None = None,
    resolution_note: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE data_error_reports
        SET
            status = %s,
            reviewed_by = COALESCE(%s, reviewed_by),
            resolution_note = COALESCE(%s, resolution_note),
            reviewed_at = NOW()
        WHERE id = %s::uuid
        RETURNING {DATA_ERROR_REPORT_FIELDS}
        """,
        (status, reviewed_by, resolution_note, report_id),
    )


def count_data_error_reports(
    conn: Connection[Any], status: str | None = None
) -> int:
    row = fetch_one(
        conn,
        """
        SELECT COUNT(*) AS total
        FROM data_error_reports
        WHERE (%s::text IS NULL OR status = %s)
        """,
        (status, status),
    )
    return int(row["total"]) if row else 0


def count_pending_data_error_reports(conn: Connection[Any]) -> int:
    return count_data_error_reports(conn, status="pending")

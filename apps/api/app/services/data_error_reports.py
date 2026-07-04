from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import data_error_reports as repository
from app.repositories.domain_events import insert_domain_event
from app.schemas.data_error_reports import DataErrorReportCreate
from app.services.community import ensure_feature_enabled
from psycopg import Connection
from typing import Any


def submit_data_error_report(
    connection: Connection[Any],
    settings: Settings,
    payload: DataErrorReportCreate,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, settings, "community_enabled")
    ensure_feature_enabled(
        connection, settings, "community_error_reports_enabled"
    )
    row = repository.insert_data_error_report(
        connection,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        country_slug=payload.country_slug,
        route_id=payload.route_id,
        report_type=payload.report_type,
        message=payload.message,
        created_by_identity_type=payload.created_by_identity_type,
        created_by_identity_id=payload.created_by_identity_id,
    )
    insert_domain_event(
        connection,
        event_key=f"data_error_report:{row['id']}:data_error_report.submitted",
        event_type="data_error_report.submitted",
        aggregate_type="data_error_report",
        aggregate_id=row["id"],
        country_slug=row.get("country_slug"),
        payload={"report_type": row["report_type"], "status": row["status"]},
        status="pending",
        notifiable=False,
    )
    return row


def list_data_error_reports_for_admin(
    connection: Connection[Any], *, status: str | None, limit: int
) -> list[dict[str, Any]]:
    return repository.list_data_error_reports_for_admin(
        connection, status=status, limit=limit
    )


def update_data_error_report_status(
    connection: Connection[Any],
    report_id: str,
    status: str,
    reviewed_by: str | None,
    resolution_note: str | None,
) -> dict[str, Any]:
    row = repository.update_data_error_report_status(
        connection,
        report_id,
        status,
        reviewed_by=reviewed_by,
        resolution_note=resolution_note,
    )
    if row is None:
        raise api_error(
            404, "data_error_report_not_found", f"Report not found: {report_id}"
        )
    return row

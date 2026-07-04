from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.services.migration_board import helpers
from psycopg import Connection
from typing import Any


def report_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    _validate_report(reason, details)
    if repository.get_post_by_id(connection, post_id) is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return _create_report(
        connection,
        current_user=current_user,
        post_id=post_id,
        contact_request_id=None,
        reason=reason,
        details=details,
    )


def report_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    _validate_report(reason, details)
    request = repository.get_contact_request_by_id(connection, request_id)
    if request is None or current_user.id not in {
        request["from_user_id"],
        request["to_user_id"],
    }:
        raise api_error(
            404,
            "contact_request_not_found",
            "Contact request was not found.",
            {},
        )
    return _create_report(
        connection,
        current_user=current_user,
        post_id=None,
        contact_request_id=request_id,
        reason=reason,
        details=details,
    )


def list_reports_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    rows = repository.list_reports_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )
    return {
        "items": [helpers._report(row) for row in rows],
        "total": helpers._total(rows),
    }


def resolve_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    resolution_note: str | None,
    hide_related_post: bool,
) -> dict[str, Any]:
    return _review_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        status="resolved",
        resolution_note=resolution_note,
        hide_related_post=hide_related_post,
    )


def dismiss_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    resolution_note: str | None,
) -> dict[str, Any]:
    return _review_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        status="dismissed",
        resolution_note=resolution_note,
        hide_related_post=False,
    )


def _create_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str | None,
    contact_request_id: str | None,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    if (
        repository.count_reports_created_today(connection, current_user.id)
        >= helpers.MAX_REPORTS_PER_DAY
    ):
        raise api_error(
            429,
            "report_limit_exceeded",
            "Daily report limit exceeded.",
            {"limit": helpers.MAX_REPORTS_PER_DAY},
        )
    if repository.existing_pending_report_exists(
        connection,
        reporter_user_id=current_user.id,
        post_id=post_id,
        contact_request_id=contact_request_id,
    ):
        raise api_error(
            409,
            "duplicate_pending_report",
            "A pending report already exists.",
            {},
        )
    report = repository.create_report(
        connection,
        reporter_user_id=current_user.id,
        post_id=post_id,
        contact_request_id=contact_request_id,
        reason=reason,
        details=details,
    )
    helpers._audit(
        connection,
        {"id": post_id or contact_request_id},
        "report_created",
        current_user,
        {"reason": {"new": reason}},
    )
    helpers._track_event(
        connection,
        "migration_board_report_created",
        entity_id=post_id or contact_request_id,
        metadata={"reason": reason},
    )
    return helpers._report(report)


def _validate_report(reason: str, details: str | None) -> None:
    if reason not in helpers.ALLOWED_REPORT_REASONS:
        raise api_error(
            422, "invalid_report_reason", "Report reason is invalid.", {}
        )
    if details is not None and len(details) > 1000:
        raise api_error(
            422, "report_details_too_long", "Report details are too long.", {}
        )


def _review_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    status: str,
    resolution_note: str | None,
    hide_related_post: bool,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    report = repository.get_report_by_id(connection, report_id)
    if report is None:
        raise api_error(404, "report_not_found", "Report was not found.", {})
    updated = repository.update_report_status(
        connection,
        report_id=report_id,
        status=status,
        reviewed_by=current_user.id,
        resolution_note=resolution_note,
    )
    if updated is None:
        raise api_error(
            409, "invalid_report_status", "Report cannot be reviewed.", {}
        )
    if hide_related_post and updated.get("post_id"):
        repository.hide_post(
            connection,
            post_id=updated["post_id"],
            moderator_user_id=current_user.id,
            reason=resolution_note,
        )
    helpers._audit(
        connection,
        {"id": report_id},
        f"report_{status}",
        current_user,
        {"status": {"old": report["status"], "new": status}},
    )
    return helpers._report(updated)

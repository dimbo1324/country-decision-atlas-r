from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.services import capabilities as capabilities_service
from app.services.migration_board import helpers
from datetime import datetime
from psycopg import Connection
from typing import Any


def list_my_threads(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.THREADS_FEATURE_KEY)
    rows = repository.list_my_threads(connection, current_user.id)
    return {
        "items": [helpers._thread(row, current_user.id) for row in rows],
        "total": len(rows),
    }


def list_thread_messages(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    thread_id: str,
    after: datetime | None,
    limit: int,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.THREADS_FEATURE_KEY)
    _get_owned_thread_or_404(
        connection, thread_id=thread_id, user_id=current_user.id
    )
    rows = repository.list_messages(
        connection, thread_id=thread_id, after=after, limit=limit
    )
    return {
        "items": [helpers._thread_message(row) for row in rows],
        "total": len(rows),
    }


def send_thread_message(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    thread_id: str,
    body: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.THREADS_FEATURE_KEY)
    thread = _get_owned_thread_or_404(
        connection, thread_id=thread_id, user_id=current_user.id
    )
    if thread["status"] != "open":
        raise api_error(
            409,
            "thread_not_open",
            "Thread is not open for new messages.",
            {"status": thread["status"]},
        )
    if not body.strip():
        raise api_error(
            422, "empty_message_body", "Message body cannot be empty.", {}
        )
    limit = helpers.max_thread_messages_per_day(connection)
    if (
        repository.count_messages_created_since(connection, current_user.id)
        >= limit
    ):
        raise api_error(
            429,
            "thread_message_limit_exceeded",
            "Daily message limit exceeded.",
            {"limit": limit},
        )
    message = repository.create_message(
        connection,
        thread_id=thread_id,
        sender_user_id=current_user.id,
        body=body,
    )
    helpers._audit(
        connection,
        {"id": thread_id},
        "thread_message_sent",
        current_user,
        {"thread_id": {"new": thread_id}},
    )
    return helpers._thread_message(message)


def close_thread(
    connection: Connection[Any], *, current_user: CurrentUser, thread_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.THREADS_FEATURE_KEY)
    _get_owned_thread_or_404(
        connection, thread_id=thread_id, user_id=current_user.id
    )
    updated = repository.close_thread(
        connection, thread_id=thread_id, closed_by_user_id=current_user.id
    )
    if updated is None:
        raise api_error(409, "thread_not_open", "Thread is not open.", {})
    helpers._audit(
        connection,
        {"id": thread_id},
        "thread_closed",
        current_user,
        {"thread_id": {"new": thread_id}},
    )
    return helpers._thread(updated, current_user.id)


def get_thread_messages_for_moderation(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    thread_id: str,
    report_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    thread = repository.get_thread_by_id(connection, thread_id)
    if thread is None:
        raise api_error(404, "thread_not_found", "Thread was not found.", {})
    report = repository.get_report_by_id(connection, report_id)
    if report is None or report.get("contact_request_id") != thread.get(
        "contact_request_id"
    ):
        raise api_error(
            403,
            "report_required_for_thread_access",
            "Moderator access to a thread requires a report filed against "
            "its contact request.",
            {},
        )
    capabilities_service.assert_no_moderation_conflict(
        current_user, [thread["from_user_id"], thread["to_user_id"]]
    )
    rows = repository.list_messages(
        connection, thread_id=thread_id, after=None, limit=500
    )
    helpers._audit(
        connection,
        {"id": thread_id},
        "thread_viewed_by_moderator",
        current_user,
        {"report_id": {"new": report_id}},
    )
    return {
        "items": [helpers._thread_message(row) for row in rows],
        "total": len(rows),
    }


def _get_owned_thread_or_404(
    connection: Connection[Any], *, thread_id: str, user_id: str
) -> dict[str, Any]:
    thread = repository.get_thread_by_id(connection, thread_id)
    if thread is None or user_id not in {
        thread["from_user_id"],
        thread["to_user_id"],
    }:
        raise api_error(404, "thread_not_found", "Thread was not found.", {})
    return thread

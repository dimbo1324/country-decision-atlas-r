from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.services.migration_board import helpers
from psycopg import Connection
from typing import Any


def create_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    message: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.CONTACT_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None or not _can_receive_contact_request(post):
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    if post["user_id"] == current_user.id:
        raise api_error(
            422, "self_contact_not_allowed", "You cannot contact yourself.", {}
        )
    if repository.is_user_blocked(
        connection, user_a_id=current_user.id, user_b_id=post["user_id"]
    ):
        raise api_error(
            403, "contact_blocked", "Contact request is blocked.", {}
        )
    if repository.pending_contact_request_exists(
        connection, post_id=post_id, from_user_id=current_user.id
    ):
        raise api_error(
            409,
            "duplicate_pending_contact_request",
            "A pending request already exists.",
            {},
        )
    limit = helpers.max_contact_requests_per_day(connection)
    if (
        repository.count_contact_requests_created_since(
            connection, user_id=current_user.id, since_sql="1 day"
        )
        >= limit
    ):
        raise api_error(
            429,
            "contact_request_limit_exceeded",
            "Daily contact request limit exceeded.",
            {"limit": limit},
        )
    request = repository.create_contact_request(
        connection,
        post_id=post_id,
        from_user_id=current_user.id,
        to_user_id=post["user_id"],
        message=message,
    )
    helpers._audit(
        connection,
        post,
        "contact_request_created",
        current_user,
        {"contact_request_id": {"new": request["id"]}},
    )
    helpers._track_event(
        connection,
        "migration_board_contact_request_created",
        entity_id=post_id,
        metadata=helpers._safe_post_metadata(post),
    )
    return helpers._contact_request(request)


def list_incoming_requests(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    rows = repository.list_incoming_contact_requests(
        connection, current_user.id
    )
    return {
        "items": [helpers._contact_request(row) for row in rows],
        "total": len(rows),
    }


def list_outgoing_requests(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    rows = repository.list_outgoing_contact_requests(
        connection, current_user.id
    )
    return {
        "items": [helpers._contact_request(row) for row in rows],
        "total": len(rows),
    }


def accept_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    response_note: str | None,
) -> dict[str, Any]:
    request = _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="accepted",
        response_note=response_note,
        expected_user_field="to_user_id",
        action="accepted",
    )
    repository.create_thread_for_contact_request(connection, request["id"])
    return request


def decline_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    response_note: str | None,
) -> dict[str, Any]:
    return _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="declined",
        response_note=response_note,
        expected_user_field="to_user_id",
        action="declined",
    )


def cancel_contact_request(
    connection: Connection[Any], *, current_user: CurrentUser, request_id: str
) -> dict[str, Any]:
    return _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="cancelled",
        response_note=None,
        expected_user_field="from_user_id",
        action="cancelled",
    )


def block_user(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    blocked_user_id: str,
    reason: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    if blocked_user_id == current_user.id:
        raise api_error(
            422, "self_block_not_allowed", "You cannot block yourself.", {}
        )
    if not repository.user_exists(connection, blocked_user_id):
        raise api_error(404, "user_not_found", "User was not found.", {})
    row = repository.block_user(
        connection,
        blocker_user_id=current_user.id,
        blocked_user_id=blocked_user_id,
        reason=reason,
    )
    repository.freeze_threads_between_users(
        connection, user_a_id=current_user.id, user_b_id=blocked_user_id
    )
    helpers._audit(
        connection,
        {"id": blocked_user_id},
        "user_blocked",
        current_user,
        {"blocked_user_id": {"new": blocked_user_id}},
    )
    return row


def unblock_user(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    blocked_user_id: str,
) -> None:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    repository.unblock_user(
        connection,
        blocker_user_id=current_user.id,
        blocked_user_id=blocked_user_id,
    )
    helpers._audit(
        connection,
        {"id": blocked_user_id},
        "user_unblocked",
        current_user,
        {"blocked_user_id": {"old": blocked_user_id}},
    )


def list_blocked_users(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    rows = repository.list_blocked_users(connection, current_user.id)
    return {"items": rows, "total": len(rows)}


def _can_receive_contact_request(post: dict[str, Any]) -> bool:
    return (
        post["status"] == "published"
        and post["moderation_status"] == "approved"
        and post["visibility"] in {"public", "members_only"}
        and bool(post["contact_requests_enabled"])
    )


def _change_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    status: str,
    response_note: str | None,
    expected_user_field: str,
    action: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    request = repository.get_contact_request_by_id(connection, request_id)
    if request is None or request[expected_user_field] != current_user.id:
        raise api_error(
            404,
            "contact_request_not_found",
            "Contact request was not found.",
            {},
        )
    updated = repository.update_contact_request_status(
        connection,
        request_id=request_id,
        status=status,
        response_note=response_note,
    )
    if updated is None:
        raise api_error(
            409, "invalid_contact_request_status", "Request cannot change.", {}
        )
    helpers._audit(
        connection,
        {"id": updated["post_id"]},
        f"contact_request_{action}",
        current_user,
        {"contact_request_id": {"new": request_id}, "status": {"new": status}},
    )
    return helpers._contact_request(updated)

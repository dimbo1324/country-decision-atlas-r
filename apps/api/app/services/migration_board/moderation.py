from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.services import capabilities as capabilities_service
from app.services.list_helpers import total_from_window_count
from app.services.migration_board import helpers
from psycopg import Connection
from typing import Any


def list_posts_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    rows = repository.list_posts_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )
    return {
        "items": [helpers._admin_post(row) for row in rows],
        "total": total_from_window_count(rows),
    }


def get_post_for_moderation(
    connection: Connection[Any], post_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return helpers._admin_post(post)


def approve_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    capabilities_service.assert_no_moderation_conflict(
        current_user, [post["user_id"]]
    )
    helpers._require_submit_ready(post)
    updated = repository.publish_post(
        connection, post_id=post_id, moderator_user_id=current_user.id
    )
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be approved.", {}
        )
    helpers._audit(
        connection,
        updated,
        "published",
        current_user,
        {"status": {"old": post["status"], "new": "published"}},
    )
    return helpers._admin_post(updated)


def reject_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    capabilities_service.assert_no_moderation_conflict(
        current_user, [post["user_id"]]
    )
    updated = repository.reject_post(
        connection,
        post_id=post_id,
        moderator_user_id=current_user.id,
        reason=reason,
    )
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be rejected.", {}
        )
    helpers._audit(
        connection,
        updated,
        "rejected",
        current_user,
        {"reason": {"new": reason}},
    )
    return helpers._admin_post(updated)


def hide_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    capabilities_service.assert_no_moderation_conflict(
        current_user, [post["user_id"]]
    )
    updated = repository.hide_post(
        connection,
        post_id=post_id,
        moderator_user_id=current_user.id,
        reason=reason,
    )
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be hidden.", {}
        )
    helpers._audit(
        connection, updated, "hidden", current_user, {"reason": {"new": reason}}
    )
    return helpers._admin_post(updated)

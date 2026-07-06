from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import author_metrics as repository
from app.services.author_metrics import helpers
from psycopg import Connection
from typing import Any


DEFAULT_FEED_LIMIT = 50


def create_subscription(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    metric_id: str | None,
    author_user_id: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    if (metric_id is None) == (author_user_id is None):
        raise api_error(
            422,
            "invalid_subscription_target",
            "Provide exactly one of metric_id or author_user_id.",
            {},
        )
    if metric_id is not None:
        definition = repository.get_definition_by_id(connection, metric_id)
        if (
            definition is None
            or definition["status"] != "published"
            or definition["visibility"] != "public"
        ):
            raise api_error(
                404,
                "author_metric_not_found",
                "Author metric definition was not found.",
                {},
            )
    existing = repository.get_subscription_for_target(
        connection,
        user_id=current_user.id,
        metric_id=metric_id,
        author_user_id=author_user_id,
    )
    if existing is not None:
        return helpers._subscription(existing)
    subscription = repository.create_subscription(
        connection,
        user_id=current_user.id,
        metric_id=metric_id,
        author_user_id=author_user_id,
    )
    return helpers._subscription(subscription)


def delete_subscription(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    subscription_id: str,
) -> None:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_subscriptions_for_user(connection, current_user.id)
    if not any(row["id"] == subscription_id for row in rows):
        raise api_error(
            404,
            "subscription_not_found",
            "Subscription was not found.",
            {},
        )
    repository.delete_subscription(connection, subscription_id)


def list_my_subscriptions(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_subscriptions_for_user(connection, current_user.id)
    return {
        "items": [helpers._subscription(row) for row in rows],
        "total": len(rows),
    }


def list_my_feed(
    connection: Connection[Any],
    current_user: CurrentUser,
    limit: int = DEFAULT_FEED_LIMIT,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_feed_values_for_user(
        connection, current_user.id, limit
    )
    return {
        "items": [helpers._feed_entry(row) for row in rows],
        "total": len(rows),
    }

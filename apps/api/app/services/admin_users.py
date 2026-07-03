from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import auth as repository
from psycopg import Connection
from typing import Any


def get_user_or_404(connection: Connection[Any], user_id: str) -> dict[str, Any]:
    user = repository.get_user_by_id(connection, user_id)
    if user is None:
        raise api_error(
            404, "user_not_found", "User was not found.", {"user_id": user_id}
        )
    return user


def update_user_role(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    user_id: str,
    new_role: str,
) -> dict[str, Any]:
    target = get_user_or_404(connection, user_id)
    is_owner_action = target["role"] == "owner" or new_role == "owner"
    if is_owner_action and current_user.role != "owner":
        raise api_error(
            403,
            "insufficient_role",
            "Only an owner can assign or change the owner role.",
            {"target_user_id": user_id},
        )
    updated = repository.set_user_role(connection, user_id, new_role)
    assert updated is not None
    return updated


def update_user_status(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    user_id: str,
    new_status: str,
) -> dict[str, Any]:
    target = get_user_or_404(connection, user_id)
    if target["role"] == "owner" and current_user.role != "owner":
        raise api_error(
            403,
            "insufficient_role",
            "Only an owner can change another owner's status.",
            {"target_user_id": user_id},
        )
    updated = repository.set_user_status(connection, user_id, new_status)
    assert updated is not None
    return updated

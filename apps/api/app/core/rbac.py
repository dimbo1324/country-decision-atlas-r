from app.core.auth import CurrentUser, get_current_active_user
from app.core.errors import api_error
from collections.abc import Callable
from fastapi import Depends
from typing import Annotated


USER = "user"
EDITOR = "editor"
MODERATOR = "moderator"
ADMIN = "admin"
OWNER = "owner"

ROLE_ORDER = (USER, MODERATOR, EDITOR, ADMIN, OWNER)


def has_role(user: CurrentUser, role: str) -> bool:
    return user.role == role


def has_any_role(user: CurrentUser, roles: tuple[str, ...]) -> bool:
    return user.role in roles


def require_roles(*roles: str) -> Callable[..., CurrentUser]:
    def _dependency(
        current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    ) -> CurrentUser:
        if not has_any_role(current_user, roles):
            raise api_error(
                403,
                "insufficient_role",
                "You do not have permission to perform this action.",
                {"required_roles": list(roles), "role": current_user.role},
            )
        return current_user

    return _dependency


require_user = require_roles(USER, MODERATOR, EDITOR, ADMIN, OWNER)
require_moderator = require_roles(MODERATOR, ADMIN, OWNER)
require_editor = require_roles(EDITOR, ADMIN, OWNER)
require_admin = require_roles(ADMIN, OWNER)
require_owner = require_roles(OWNER)

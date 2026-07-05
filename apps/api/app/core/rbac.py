from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.core.errors import api_error
from app.services import capabilities as capabilities_service
from collections.abc import Callable
from fastapi import Depends
from psycopg import Connection
from typing import Annotated, Any


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


def require_capability(capability: str) -> Callable[..., CurrentUser]:
    def _dependency(
        connection: Annotated[Connection[Any], Depends(get_connection)],
        current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    ) -> CurrentUser:
        if not capabilities_service.has_capability(
            connection, current_user, capability
        ):
            raise api_error(
                403,
                "insufficient_capability",
                "You do not have the required capability to perform this action.",
                {"required_capability": capability, "role": current_user.role},
            )
        return current_user

    return _dependency


def require_capability_or_roles(
    capability: str, *roles: str
) -> Callable[..., CurrentUser]:
    def _dependency(
        connection: Annotated[Connection[Any], Depends(get_connection)],
        current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    ) -> CurrentUser:
        if has_any_role(
            current_user, roles
        ) or capabilities_service.has_capability(
            connection, current_user, capability
        ):
            return current_user
        raise api_error(
            403,
            "insufficient_capability",
            "You do not have the required capability to perform this action.",
            {
                "required_capability": capability,
                "allowed_roles": list(roles),
                "role": current_user.role,
            },
        )

    return _dependency

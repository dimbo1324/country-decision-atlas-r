from app.core.database import get_connection
from app.core.errors import api_error
from app.services import auth as auth_service
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg import Connection
from pydantic import BaseModel
from typing import Annotated, Any


bearer_scheme = HTTPBearer(scheme_name="BearerAuth", auto_error=False)


class CurrentUser(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    status: str


class CurrentSessionContext(BaseModel):
    user: CurrentUser
    session_id: str


def _to_current_user(user_row: dict[str, Any]) -> CurrentUser:
    return CurrentUser(
        id=user_row["id"],
        email=user_row["email"],
        display_name=user_row["display_name"],
        role=user_row["role"],
        status=user_row["status"],
    )


def get_current_session_context(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> CurrentSessionContext:
    if credentials is None or not credentials.credentials:
        raise api_error(401, "auth_required", "Authentication is required.", {})
    result = auth_service.validate_session_token(
        connection, credentials.credentials
    )
    return CurrentSessionContext(
        user=_to_current_user(result["user"]),
        session_id=result["session"]["id"],
    )


def get_current_user(
    context: Annotated[
        CurrentSessionContext, Depends(get_current_session_context)
    ],
) -> CurrentUser:
    return context.user


def get_current_active_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    return current_user

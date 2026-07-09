from app.core.config import get_settings
from app.core.database import get_connection
from app.core.errors import api_error
from app.services import auth as auth_service
from fastapi import Depends, Request, Response, Security
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


def _extract_raw_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials is not None and credentials.credentials:
        return credentials.credentials
    cookie_name = get_settings().auth_session_cookie_name
    return request.cookies.get(cookie_name)


def _apply_rotated_token(response: Response, rotated_token: str | None) -> None:
    if rotated_token is None:
        return
    settings = get_settings()
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=rotated_token,
        max_age=settings.auth_session_ttl_hours * 3600,
        httponly=True,
        secure=(settings.app_env == "production"),
        samesite="lax",
        path="/",
    )
    response.headers["X-Session-Token"] = rotated_token


def get_current_session_context(
    request: Request,
    response: Response,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> CurrentSessionContext:
    raw_token = _extract_raw_token(request, credentials)
    if raw_token is None:
        raise api_error(401, "auth_required", "Authentication is required.", {})
    result = auth_service.validate_session_token(connection, raw_token)
    _apply_rotated_token(response, result.get("rotated_token"))
    return CurrentSessionContext(
        user=_to_current_user(result["user"]),
        session_id=result["session"]["id"],
    )


def get_optional_current_user(
    request: Request,
    response: Response,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> CurrentUser | None:
    raw_token = _extract_raw_token(request, credentials)
    if raw_token is None:
        return None
    result = auth_service.validate_session_token(connection, raw_token)
    _apply_rotated_token(response, result.get("rotated_token"))
    return _to_current_user(result["user"])


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

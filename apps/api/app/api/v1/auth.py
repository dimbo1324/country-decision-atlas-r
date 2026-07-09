from app.core.auth import (
    CurrentSessionContext,
    CurrentUser,
    get_current_active_user,
    get_current_session_context,
)
from app.core.config import get_settings
from app.core.database import get_connection
from app.core.errors import api_error
from app.core.request_context import resolve_client_ip
from app.repositories import auth as repository, security_notifications
from app.schemas.auth import (
    AuthSession,
    AuthTokenResponse,
    AuthUser,
    CurrentUserResponse,
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    RevokeAllSessionsRequest,
    RevokeAllSessionsResponse,
    SecurityNotification,
    SecurityNotificationAckResponse,
    SecurityNotificationListResponse,
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramLinkStatusResponse,
    TelegramUnlinkResponse,
    UserSessionListResponse,
)
from app.services import (
    auth as service,
    telegram_web_link as telegram_link_service,
)
from app.services.feature_flags import ensure_feature_enabled
from fastapi import APIRouter, Depends, Request, Response
from psycopg import Connection
from typing import Annotated, Any
from uuid import UUID


TELEGRAM_WEB_LINK_FEATURE_KEY = "telegram_web_link_enabled"


def _require_telegram_web_link_enabled(connection: Connection[Any]) -> None:
    ensure_feature_enabled(
        connection,
        TELEGRAM_WEB_LINK_FEATURE_KEY,
        "Telegram web linking is currently disabled.",
    )


router = APIRouter(prefix="/auth", tags=["auth"])


def _to_auth_user(user_row: dict[str, Any]) -> AuthUser:
    return AuthUser(
        id=user_row["id"],
        email=user_row["email"],
        display_name=user_row["display_name"],
        role=user_row["role"],
        status=user_row["status"],
        created_at=user_row["created_at"],
    )


def _to_auth_session(
    session_row: dict[str, Any], *, current_session_id: str | None = None
) -> AuthSession:
    return AuthSession(
        id=session_row["id"],
        created_at=session_row["created_at"],
        expires_at=session_row["expires_at"],
        last_seen_at=session_row["last_seen_at"],
        revoked_at=session_row["revoked_at"],
        device_label=session_row.get("device_label"),
        ip_display=session_row.get("ip_display"),
        is_current=session_row["id"] == current_session_id,
    )


def _set_session_cookies(
    response: Response, *, raw_token: str, csrf_token: str
) -> None:
    settings = get_settings()
    secure = settings.app_env == "production"
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=raw_token,
        max_age=settings.auth_session_ttl_hours * 3600,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=settings.auth_csrf_cookie_name,
        value=csrf_token,
        max_age=settings.auth_session_ttl_hours * 3600,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
    )


def _clear_session_cookies(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.auth_session_cookie_name, path="/")
    response.delete_cookie(settings.auth_csrf_cookie_name, path="/")


def _to_security_notification(row: dict[str, Any]) -> SecurityNotification:
    return SecurityNotification(
        id=row["id"],
        event_type=row["event_type"],
        device_label=row["device_label"],
        ip_display=row["ip_display"],
        created_at=row["created_at"],
        acknowledged_at=row["acknowledged_at"],
    )


@router.post("/register", response_model=AuthTokenResponse)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> AuthTokenResponse:
    settings = get_settings()
    user = service.register_user(
        connection,
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
    )
    raw_token, session, _is_new_device = service.create_login_session(
        connection,
        user_id=user["id"],
        user_agent=request.headers.get("user-agent"),
        client_ip=resolve_client_ip(request, settings),
        notify_new_device=False,
    )
    connection.commit()
    _set_session_cookies(
        response, raw_token=raw_token, csrf_token=service.generate_csrf_token()
    )
    return AuthTokenResponse(
        token=raw_token,
        user=_to_auth_user(user),
        expires_at=session["expires_at"],
        is_new_device=False,
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> AuthTokenResponse:
    settings = get_settings()
    raw_token, user, session, is_new_device = service.login_user(
        connection,
        email=payload.email,
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        client_ip=resolve_client_ip(request, settings),
    )
    connection.commit()
    _set_session_cookies(
        response, raw_token=raw_token, csrf_token=service.generate_csrf_token()
    )
    return AuthTokenResponse(
        token=raw_token,
        user=_to_auth_user(user),
        expires_at=session["expires_at"],
        is_new_device=is_new_device,
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    context: Annotated[
        CurrentSessionContext, Depends(get_current_session_context)
    ],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> LogoutResponse:
    service.logout_session(
        connection, user_id=context.user.id, session_id=context.session_id
    )
    connection.commit()
    _clear_session_cookies(response)
    return LogoutResponse(ok=True)


@router.get("/me", response_model=CurrentUserResponse)
def me(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> CurrentUserResponse:
    user_row = repository.get_user_by_id(connection, current_user.id)
    if user_row is None:
        raise api_error(
            401, "invalid_auth_token", "Session token is invalid.", {}
        )
    return CurrentUserResponse(user=_to_auth_user(user_row))


@router.get("/sessions", response_model=UserSessionListResponse)
def list_sessions(
    context: Annotated[
        CurrentSessionContext, Depends(get_current_session_context)
    ],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> UserSessionListResponse:
    sessions = repository.list_user_sessions(connection, context.user.id)
    return UserSessionListResponse(
        items=[
            _to_auth_session(row, current_session_id=context.session_id)
            for row in sessions
        ]
    )


@router.delete("/sessions/{session_id}", response_model=LogoutResponse)
def revoke_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> LogoutResponse:
    revoked = repository.revoke_session(
        connection, str(session_id), current_user.id
    )
    connection.commit()
    return LogoutResponse(ok=revoked is not None)


@router.post("/sessions/revoke-all", response_model=RevokeAllSessionsResponse)
def revoke_all_sessions(
    payload: RevokeAllSessionsRequest,
    response: Response,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> RevokeAllSessionsResponse:
    service.require_step_up_reauthentication(
        connection,
        user_id=current_user.id,
        password=payload.current_password,
    )
    revoked_count = repository.revoke_all_user_sessions(
        connection, current_user.id
    )
    connection.commit()
    _clear_session_cookies(response)
    return RevokeAllSessionsResponse(revoked_count=revoked_count)


@router.get(
    "/security-notifications", response_model=SecurityNotificationListResponse
)
def list_security_notifications(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> SecurityNotificationListResponse:
    notifications = security_notifications.list_unacknowledged_notifications(
        connection, current_user.id
    )
    return SecurityNotificationListResponse(
        items=[_to_security_notification(row) for row in notifications]
    )


@router.post(
    "/security-notifications/{notification_id}/ack",
    response_model=SecurityNotificationAckResponse,
)
def acknowledge_security_notification(
    notification_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> SecurityNotificationAckResponse:
    acknowledged = security_notifications.acknowledge_notification(
        connection, str(notification_id), current_user.id
    )
    connection.commit()
    return SecurityNotificationAckResponse(ok=acknowledged is not None)


@router.post("/telegram/link", response_model=TelegramLinkResponse)
def link_telegram(
    payload: TelegramLinkRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TelegramLinkResponse:
    _require_telegram_web_link_enabled(connection)
    link = telegram_link_service.link_telegram_account(
        connection, user_id=current_user.id, code=payload.code
    )
    connection.commit()
    return TelegramLinkResponse(
        linked=True,
        telegram_user_id=link["telegram_user_id"],
        linked_at=link["linked_at"],
    )


@router.delete("/telegram/link", response_model=TelegramUnlinkResponse)
def unlink_telegram(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TelegramUnlinkResponse:
    _require_telegram_web_link_enabled(connection)
    telegram_link_service.unlink_telegram_account(
        connection, user_id=current_user.id
    )
    connection.commit()
    return TelegramUnlinkResponse(ok=True)


@router.get("/telegram/link", response_model=TelegramLinkStatusResponse)
def get_telegram_link_status(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TelegramLinkStatusResponse:
    _require_telegram_web_link_enabled(connection)
    link = telegram_link_service.get_telegram_link_status(
        connection, user_id=current_user.id
    )
    if link is None:
        return TelegramLinkStatusResponse(linked=False)
    return TelegramLinkStatusResponse(
        linked=True,
        telegram_user_id=link["telegram_user_id"],
        linked_at=link["linked_at"],
    )

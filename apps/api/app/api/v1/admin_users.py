from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_admin
from app.repositories import auth as repository
from app.schemas.auth import (
    AdminUser,
    AdminUserListResponse,
    AuthSession,
    RevokeAllSessionsResponse,
    RoleUpdateRequest,
    UserSessionListResponse,
    UserStatusUpdateRequest,
)
from app.services import admin_users as service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin/users", tags=["admin-users"])


def _to_admin_user(row: dict[str, Any]) -> AdminUser:
    return AdminUser(
        id=row["id"],
        email=row["email"],
        display_name=row["display_name"],
        role=row["role"],
        status=row["status"],
        last_login_at=row["last_login_at"],
        last_seen_at=row["last_seen_at"],
        created_at=row["created_at"],
    )


def _to_auth_session(row: dict[str, Any]) -> AuthSession:
    return AuthSession(
        id=row["id"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        last_seen_at=row["last_seen_at"],
        revoked_at=row["revoked_at"],
    )


@router.get("", response_model=AdminUserListResponse)
def list_users(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminUserListResponse:
    users = repository.list_users(connection, limit, offset)
    total = repository.count_users(connection)
    return AdminUserListResponse(
        total=total, items=[_to_admin_user(row) for row in users]
    )


@router.get("/{user_id}", response_model=AdminUser)
def get_user(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> AdminUser:
    user = service.get_user_or_404(connection, user_id)
    return _to_admin_user(user)


@router.patch("/{user_id}/role", response_model=AdminUser)
def update_user_role(
    user_id: str,
    payload: RoleUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_admin)],
) -> AdminUser:
    updated = service.update_user_role(
        connection, current_user=current_user, user_id=user_id, new_role=payload.role
    )
    connection.commit()
    return _to_admin_user(updated)


@router.patch("/{user_id}/status", response_model=AdminUser)
def update_user_status(
    user_id: str,
    payload: UserStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_admin)],
) -> AdminUser:
    updated = service.update_user_status(
        connection,
        current_user=current_user,
        user_id=user_id,
        new_status=payload.status,
    )
    connection.commit()
    return _to_admin_user(updated)


@router.get("/{user_id}/sessions", response_model=UserSessionListResponse)
def list_user_sessions(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> UserSessionListResponse:
    service.get_user_or_404(connection, user_id)
    sessions = repository.list_user_sessions(connection, user_id)
    return UserSessionListResponse(items=[_to_auth_session(row) for row in sessions])


@router.post("/{user_id}/sessions/revoke-all", response_model=RevokeAllSessionsResponse)
def revoke_all_user_sessions(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> RevokeAllSessionsResponse:
    service.get_user_or_404(connection, user_id)
    revoked_count = repository.revoke_all_user_sessions(connection, user_id)
    connection.commit()
    return RevokeAllSessionsResponse(revoked_count=revoked_count)

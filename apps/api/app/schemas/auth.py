from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


UserRole = Literal["user", "editor", "moderator", "admin", "owner"]
UserStatus = Literal["active", "suspended", "deleted"]


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUser(BaseModel):
    id: str
    email: str
    display_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime


class AuthSession(BaseModel):
    id: str
    created_at: datetime
    expires_at: datetime
    last_seen_at: datetime | None
    revoked_at: datetime | None
    device_label: str | None = None
    ip_display: str | None = None
    is_current: bool = False


class AuthTokenResponse(BaseModel):
    token: str
    user: AuthUser
    expires_at: datetime
    is_new_device: bool = False


class CurrentUserResponse(BaseModel):
    user: AuthUser


class LogoutResponse(BaseModel):
    ok: bool


class RevokeAllSessionsRequest(BaseModel):
    current_password: str


class RevokeAllSessionsResponse(BaseModel):
    revoked_count: int = Field(ge=0)


class UserSessionListResponse(BaseModel):
    items: list[AuthSession] = Field(default_factory=list)


class SecurityNotification(BaseModel):
    id: str
    event_type: Literal["new_device_login"]
    device_label: str | None = None
    ip_display: str | None = None
    created_at: datetime
    acknowledged_at: datetime | None = None


class SecurityNotificationListResponse(BaseModel):
    items: list[SecurityNotification] = Field(default_factory=list)


class SecurityNotificationAckResponse(BaseModel):
    ok: bool


class TelegramLinkRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)


class TelegramLinkResponse(BaseModel):
    linked: bool
    telegram_user_id: str
    linked_at: datetime


class TelegramLinkStatusResponse(BaseModel):
    linked: bool
    telegram_user_id: str | None = None
    linked_at: datetime | None = None


class TelegramUnlinkResponse(BaseModel):
    ok: bool


class AdminUser(BaseModel):
    id: str
    email: str
    display_name: str
    role: UserRole
    status: UserStatus
    last_login_at: datetime | None
    last_seen_at: datetime | None
    created_at: datetime


class AdminUserListResponse(BaseModel):
    total: int = Field(ge=0)
    items: list[AdminUser] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    role: UserRole


class UserStatusUpdateRequest(BaseModel):
    status: UserStatus

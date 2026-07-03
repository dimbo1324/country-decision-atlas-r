"""Registration, login, and current-user auth API endpoints."""

from app.api.v1 import auth as auth_api
from app.core.auth import (
    CurrentSessionContext,
    CurrentUser,
    get_current_active_user,
    get_current_session_context,
)
from app.core.database import get_connection
from app.repositories import auth as repository
from app.services import auth as service, telegram_web_link as telegram_link_service
from datetime import UTC, datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()

CURRENT_USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def _user_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": CURRENT_USER.id,
        "email": CURRENT_USER.email,
        "display_name": CURRENT_USER.display_name,
        "role": CURRENT_USER.role,
        "status": CURRENT_USER.status,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    row.update(overrides)
    return row


def _session_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "session-1",
        "expires_at": datetime(2026, 1, 8, tzinfo=UTC),
        "last_seen_at": None,
        "revoked_at": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    row.update(overrides)
    return row


def _client(*, authenticated: bool = False) -> TestClient:
    app = FastAPI()
    app.include_router(auth_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if authenticated:
        app.dependency_overrides[get_current_active_user] = lambda: CURRENT_USER
        app.dependency_overrides[get_current_session_context] = lambda: (
            CurrentSessionContext(user=CURRENT_USER, session_id="session-1")
        )
    return TestClient(app, raise_server_exceptions=False)


def test_register_returns_token_and_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service, "register_user", lambda *_a, **_kw: _user_row())
    monkeypatch.setattr(
        service,
        "create_login_session",
        lambda *_a, **_kw: ("raw-token-value", _session_row()),
    )
    client = _client()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.local",
            "password": "a-long-password",
            "display_name": "User",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token"] == "raw-token-value"
    assert body["user"]["email"] == "user@example.local"


def test_login_returns_token_and_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        service,
        "login_user",
        lambda *_a, **_kw: ("raw-token-value", _user_row(), _session_row()),
    )
    client = _client()
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.local", "password": "a-long-password"},
    )
    assert response.status_code == 200
    assert response.json()["token"] == "raw-token-value"


def test_login_invalid_credentials_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.errors import api_error

    def _raise(*_a: Any, **_kw: Any) -> Any:
        raise api_error(401, "invalid_credentials", "Invalid email or password.", {})

    monkeypatch.setattr(service, "login_user", _raise)
    client = _client()
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.local", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["error"]["code"] == "invalid_credentials"


def test_me_without_token_returns_401() -> None:
    client = _client()
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    client = _client(authenticated=True)
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer session-token"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["id"] == CURRENT_USER.id


def test_logout_without_token_returns_401() -> None:
    client = _client()
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401


def test_logout_revokes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_logout_session(_conn: Any, *, user_id: str, session_id: str) -> None:
        captured["user_id"] = user_id
        captured["session_id"] = session_id

    monkeypatch.setattr(service, "logout_session", fake_logout_session)
    client = _client(authenticated=True)
    response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": "Bearer session-token"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert captured == {"user_id": CURRENT_USER.id, "session_id": "session-1"}


def test_list_sessions_returns_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "list_user_sessions", lambda *_a: [_session_row()])
    client = _client(authenticated=True)
    response = client.get(
        "/api/v1/auth/sessions", headers={"Authorization": "Bearer session-token"}
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_revoke_session_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "revoke_session", lambda *_a: _session_row())
    client = _client(authenticated=True)
    response = client.delete(
        "/api/v1/auth/sessions/session-1",
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_revoke_all_sessions_returns_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "revoke_all_user_sessions", lambda *_a: 3)
    client = _client(authenticated=True)
    response = client.post(
        "/api/v1/auth/sessions/revoke-all",
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    assert response.json()["revoked_count"] == 3


def _enable_telegram_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth_api, "is_feature_enabled_by_key", lambda *_a, **_kw: True)


def _disable_telegram_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth_api, "is_feature_enabled_by_key", lambda *_a, **_kw: False)


def test_telegram_link_feature_disabled_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_telegram_feature(monkeypatch)
    client = _client(authenticated=True)
    response = client.post(
        "/api/v1/auth/telegram/link",
        json={"code": "123456"},
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["error"]["code"] == "feature_disabled"


def test_telegram_link_success_returns_linked(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_telegram_feature(monkeypatch)
    monkeypatch.setattr(
        telegram_link_service,
        "link_telegram_account",
        lambda *_a, **_kw: {
            "telegram_user_id": "tg-1",
            "linked_at": datetime(2026, 1, 1, tzinfo=UTC),
        },
    )
    client = _client(authenticated=True)
    response = client.post(
        "/api/v1/auth/telegram/link",
        json={"code": "123456"},
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["linked"] is True
    assert body["telegram_user_id"] == "tg-1"


def test_telegram_unlink_success_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_telegram_feature(monkeypatch)
    monkeypatch.setattr(
        telegram_link_service, "unlink_telegram_account", lambda *_a, **_kw: None
    )
    client = _client(authenticated=True)
    response = client.delete(
        "/api/v1/auth/telegram/link",
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_telegram_link_status_not_linked(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_telegram_feature(monkeypatch)
    monkeypatch.setattr(
        telegram_link_service, "get_telegram_link_status", lambda *_a, **_kw: None
    )
    client = _client(authenticated=True)
    response = client.get(
        "/api/v1/auth/telegram/link",
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    assert response.json()["linked"] is False


def test_telegram_link_status_linked(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_telegram_feature(monkeypatch)
    monkeypatch.setattr(
        telegram_link_service,
        "get_telegram_link_status",
        lambda *_a, **_kw: {
            "telegram_user_id": "tg-1",
            "linked_at": datetime(2026, 1, 1, tzinfo=UTC),
        },
    )
    client = _client(authenticated=True)
    response = client.get(
        "/api/v1/auth/telegram/link",
        headers={"Authorization": "Bearer session-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["linked"] is True
    assert body["telegram_user_id"] == "tg-1"

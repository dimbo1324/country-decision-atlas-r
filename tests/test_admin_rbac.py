"""Role-based access rules for admin user management: who can promote/demote which roles."""

import pytest
from app.api.v1 import admin_users as admin_users_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import auth as repository
from app.services import admin_users as service
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()

ADMIN_USER = CurrentUser(
    id="admin-id",
    email="admin@example.local",
    display_name="Admin",
    role="admin",
    status="active",
)
OWNER_USER = CurrentUser(
    id="owner-id",
    email="owner@example.local",
    display_name="Owner",
    role="owner",
    status="active",
)
EDITOR_USER = CurrentUser(
    id="editor-id",
    email="editor@example.local",
    display_name="Editor",
    role="editor",
    status="active",
)
REGULAR_USER = CurrentUser(
    id="user-id",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def _user_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "target-id",
        "email": "target@example.local",
        "display_name": "Target",
        "role": "user",
        "status": "active",
        "last_login_at": None,
        "last_seen_at": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    row.update(overrides)
    return row


def test_get_user_or_404_raises_for_missing_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: None)
    with pytest.raises(HTTPException) as exc_info:
        service.get_user_or_404(CONNECTION, "missing-id")
    assert exc_info.value.status_code == 404


def test_update_user_role_blocks_non_owner_from_promoting_to_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    with pytest.raises(HTTPException) as exc_info:
        service.update_user_role(
            CONNECTION,
            current_user=ADMIN_USER,
            user_id="target-id",
            new_role="owner",
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "insufficient_role"


def test_update_user_role_blocks_non_owner_from_demoting_an_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_user_by_id", lambda *_a: _user_row(role="owner")
    )
    with pytest.raises(HTTPException) as exc_info:
        service.update_user_role(
            CONNECTION,
            current_user=ADMIN_USER,
            user_id="target-id",
            new_role="editor",
        )
    assert exc_info.value.status_code == 403


def test_update_user_role_allows_owner_to_promote_to_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    monkeypatch.setattr(
        repository, "set_user_role", lambda *_a: _user_row(role="owner")
    )
    updated = service.update_user_role(
        CONNECTION,
        current_user=OWNER_USER,
        user_id="target-id",
        new_role="owner",
    )
    assert updated["role"] == "owner"


def test_update_user_role_allows_admin_for_non_owner_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    monkeypatch.setattr(
        repository, "set_user_role", lambda *_a: _user_row(role="editor")
    )
    updated = service.update_user_role(
        CONNECTION,
        current_user=ADMIN_USER,
        user_id="target-id",
        new_role="editor",
    )
    assert updated["role"] == "editor"


def test_update_user_status_blocks_non_owner_from_changing_owner_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_user_by_id", lambda *_a: _user_row(role="owner")
    )
    with pytest.raises(HTTPException) as exc_info:
        service.update_user_status(
            CONNECTION,
            current_user=ADMIN_USER,
            user_id="target-id",
            new_status="suspended",
        )
    assert exc_info.value.status_code == 403


def test_update_user_status_allows_owner_to_change_owner_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_user_by_id", lambda *_a: _user_row(role="owner")
    )
    monkeypatch.setattr(
        repository,
        "set_user_status",
        lambda *_a: _user_row(role="owner", status="suspended"),
    )
    updated = service.update_user_status(
        CONNECTION,
        current_user=OWNER_USER,
        user_id="target-id",
        new_status="suspended",
    )
    assert updated["status"] == "suspended"


def test_update_user_status_allows_admin_for_non_owner_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    monkeypatch.setattr(
        repository, "set_user_status", lambda *_a: _user_row(status="suspended")
    )
    updated = service.update_user_status(
        CONNECTION,
        current_user=ADMIN_USER,
        user_id="target-id",
        new_status="suspended",
    )
    assert updated["status"] == "suspended"


def _client(current_user: CurrentUser | None) -> TestClient:
    app = FastAPI()
    app.include_router(admin_users_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app, raise_server_exceptions=False)


def test_list_users_without_auth_returns_401() -> None:
    client = _client(None)
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_list_users_with_regular_user_returns_403() -> None:
    client = _client(REGULAR_USER)
    response = client.get(
        "/api/v1/admin/users", headers={"Authorization": "Bearer user-token"}
    )
    assert response.status_code == 403


def test_list_users_with_editor_returns_403() -> None:
    client = _client(EDITOR_USER)
    response = client.get(
        "/api/v1/admin/users", headers={"Authorization": "Bearer editor-token"}
    )
    assert response.status_code == 403


def test_list_users_with_admin_returns_200(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "list_users", lambda *_a: [_user_row()])
    monkeypatch.setattr(repository, "count_users", lambda *_a: 1)
    client = _client(ADMIN_USER)
    response = client.get(
        "/api/v1/admin/users", headers={"Authorization": "Bearer admin-token"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "target-id"


def test_update_role_endpoint_with_admin_returns_200(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    monkeypatch.setattr(
        repository, "set_user_role", lambda *_a: _user_row(role="editor")
    )
    client = _client(ADMIN_USER)
    response = client.patch(
        "/api/v1/admin/users/target-id/role",
        json={"role": "editor"},
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "editor"


def test_update_role_endpoint_to_owner_with_admin_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    client = _client(ADMIN_USER)
    response = client.patch(
        "/api/v1/admin/users/target-id/role",
        json={"role": "owner"},
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 403


def test_revoke_all_user_sessions_endpoint_returns_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    monkeypatch.setattr(repository, "revoke_all_user_sessions", lambda *_a: 2)
    client = _client(ADMIN_USER)
    response = client.post(
        "/api/v1/admin/users/target-id/sessions/revoke-all",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200
    assert response.json()["revoked_count"] == 2

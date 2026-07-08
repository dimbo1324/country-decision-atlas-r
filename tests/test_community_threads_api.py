"""Community threads API: auth gating, polling params, and role-gated moderator access."""

import pytest
from app.api.v1 import admin_migration_board, migration_board
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import capabilities as capabilities_repository
from app.services import migration_board as migration_board_service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()
USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)
MODERATOR = CurrentUser(
    id="22222222-2222-2222-2222-222222222222",
    email="mod@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)

THREAD_ID = "33333333-3333-3333-3333-333333333333"


def _client(current_user: CurrentUser | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(migration_board.router, prefix="/api/v1")
    app.include_router(admin_migration_board.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app)


def _thread_response(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": THREAD_ID,
        "contact_request_id": "44444444-4444-4444-4444-444444444444",
        "post_id": "66666666-6666-6666-6666-666666666666",
        "post_title": "Moving to Uruguay",
        "counterpart_display_name": "Other Member",
        "status": "open",
        "closed_by_user_id": None,
        "closed_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    return row


def _message_response(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "77777777-7777-7777-7777-777777777777",
        "thread_id": THREAD_ID,
        "sender_user_id": USER.id,
        "sender_display_name": "User",
        "body": "Hello there",
        "created_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    return row


def test_list_my_threads_requires_auth() -> None:
    response = _client().get("/api/v1/me/threads")
    assert response.status_code == 401


def test_list_my_threads_returns_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "list_my_threads",
        lambda *_a, **_kw: {"items": [_thread_response()], "total": 1},
    )

    response = _client(USER).get("/api/v1/me/threads")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_list_thread_messages_passes_polling_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_list(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"items": [_message_response()], "total": 1}

    monkeypatch.setattr(
        migration_board_service, "list_thread_messages", fake_list
    )

    response = _client(USER).get(
        f"/api/v1/me/threads/{THREAD_ID}/messages",
        params={"after": "2026-01-01T00:00:00Z", "limit": 10},
    )

    assert response.status_code == 200
    assert captured["thread_id"] == THREAD_ID
    assert captured["limit"] == 10
    assert captured["after"] is not None


def test_list_thread_messages_missing_thread_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.errors import api_error

    def raise_not_found(*_a: Any, **_kw: Any) -> None:
        raise api_error(404, "thread_not_found", "Thread was not found.", {})

    monkeypatch.setattr(
        migration_board_service, "list_thread_messages", raise_not_found
    )

    response = _client(USER).get(f"/api/v1/me/threads/{THREAD_ID}/messages")

    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "thread_not_found"


def test_send_thread_message_rejects_when_thread_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.errors import api_error

    def raise_conflict(*_a: Any, **_kw: Any) -> None:
        raise api_error(
            409, "thread_not_open", "Thread is not open for new messages.", {}
        )

    monkeypatch.setattr(
        migration_board_service, "send_thread_message", raise_conflict
    )

    response = _client(USER).post(
        f"/api/v1/me/threads/{THREAD_ID}/messages", json={"body": "Hi"}
    )

    assert response.status_code == 409
    assert response.json()["detail"]["error"]["code"] == "thread_not_open"


def test_send_thread_message_success_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "send_thread_message",
        lambda *_a, **_kw: _message_response(),
    )

    response = _client(USER).post(
        f"/api/v1/me/threads/{THREAD_ID}/messages",
        json={"body": "Hello there"},
    )

    assert response.status_code == 201
    CONNECTION.commit.assert_called()


def test_close_thread_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "close_thread",
        lambda *_a, **_kw: _thread_response(status="closed"),
    )

    response = _client(USER).post(f"/api/v1/me/threads/{THREAD_ID}/close")

    assert response.status_code == 200
    assert response.json()["thread"]["status"] == "closed"


def test_moderator_thread_messages_requires_capability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: False
    )

    response = _client(USER).get(
        f"/api/v1/admin/migration-board/threads/{THREAD_ID}/messages",
        params={"report_id": "report-1"},
    )

    assert response.status_code == 403


def test_moderator_thread_messages_requires_report_id_query_param() -> None:
    response = _client(MODERATOR).get(
        f"/api/v1/admin/migration-board/threads/{THREAD_ID}/messages"
    )

    assert response.status_code == 422


def test_moderator_can_view_thread_messages_with_valid_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "get_thread_messages_for_moderation",
        lambda *_a, **_kw: {"items": [_message_response()], "total": 1},
    )

    response = _client(MODERATOR).get(
        f"/api/v1/admin/migration-board/threads/{THREAD_ID}/messages",
        params={"report_id": "report-1"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

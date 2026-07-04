"""Admin auth/authorization and status-transition behavior for the community Q&A moderation endpoints."""

import pytest
from app.api.v1.admin_community import router
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import community as repository
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()

MODERATOR_USER = CurrentUser(
    id="moderator-id",
    email="moderator@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)


def _client(*, with_admin: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if with_admin:
        app.dependency_overrides[get_current_active_user] = lambda: (
            MODERATOR_USER
        )
    return TestClient(app)


def _question_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "33333333-3333-3333-3333-333333333333",
        "country_slug": "uruguay",
        "route_id": None,
        "legal_signal_id": None,
        "topic": "residence",
        "title": "How does it work?",
        "body": "Body text",
        "status": status,
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "moderated_at": None,
        "moderated_by": None,
    }


def test_admin_list_questions_requires_admin_auth() -> None:
    response = _client(with_admin=False).get(
        "/api/v1/admin/community/questions"
    )

    assert response.status_code == 401


def test_admin_can_list_pending_questions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "list_questions_for_admin",
        lambda *_a, **_kw: [_question_row()],
    )

    response = _client().get("/api/v1/admin/community/questions?status=pending")

    assert response.status_code == 200
    assert response.json()[0]["status"] == "pending"


def test_admin_can_change_question_status_to_published(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    published = _question_row(status="published")
    monkeypatch.setattr(
        repository, "update_question_status", lambda *_a, **_kw: published
    )

    response = _client().patch(
        "/api/v1/admin/community/questions/q1/status",
        json={"status": "published", "moderated_by": "editor"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_admin_update_missing_question_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "update_question_status", lambda *_a, **_kw: None
    )

    response = _client().patch(
        "/api/v1/admin/community/questions/missing/status",
        json={"status": "published"},
    )

    assert response.status_code == 404

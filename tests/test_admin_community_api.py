"""Admin auth/authorization and status-transition behavior for the community Q&A moderation endpoints."""

import pytest
from app.api.v1.admin_community import router
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import (
    community as repository,
    data_error_reports as data_error_reports_repository,
    user_story_ratings as user_story_ratings_repository,
)
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
        json={"status": "published"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_admin_question_status_update_ignores_client_supplied_moderated_by(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    published = _question_row(status="published")
    captured: dict[str, Any] = {}

    def fake_update(*_a: Any, **_kw: Any) -> dict[str, Any]:
        captured["moderated_by"] = _kw["moderated_by"]
        return published

    monkeypatch.setattr(repository, "update_question_status", fake_update)

    response = _client().patch(
        "/api/v1/admin/community/questions/q1/status",
        json={"status": "published", "moderated_by": "spoofed-attacker-id"},
    )

    assert response.status_code == 200
    assert captured["moderated_by"] == MODERATOR_USER.id
    assert captured["moderated_by"] != "spoofed-attacker-id"


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


def _answer_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "44444444-4444-4444-4444-444444444444",
        "question_id": "33333333-3333-3333-3333-333333333333",
        "body": "Answer body",
        "status": status,
        "source_ids": [],
        "evidence_item_ids": [],
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "moderated_at": None,
        "moderated_by": None,
    }


def test_admin_answer_status_update_ignores_client_supplied_moderated_by(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    published = _answer_row(status="published")
    captured: dict[str, Any] = {}

    def fake_update(*_a: Any, **_kw: Any) -> dict[str, Any]:
        captured["moderated_by"] = _kw["moderated_by"]
        return published

    monkeypatch.setattr(repository, "update_answer_status", fake_update)

    response = _client().patch(
        "/api/v1/admin/community/answers/a1/status",
        json={"status": "published", "moderated_by": "spoofed-attacker-id"},
    )

    assert response.status_code == 200
    assert captured["moderated_by"] == MODERATOR_USER.id


def _report_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "55555555-5555-5555-5555-555555555555",
        "entity_type": "legal_signal",
        "entity_id": None,
        "country_slug": "uruguay",
        "route_id": None,
        "report_type": "outdated",
        "message": "This looks outdated.",
        "status": status,
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
        "resolution_note": None,
    }


def test_admin_data_error_report_status_update_ignores_client_supplied_reviewed_by(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved = _report_row(status="resolved")
    captured: dict[str, Any] = {}

    def fake_update(*_a: Any, **_kw: Any) -> dict[str, Any]:
        captured["reviewed_by"] = _kw["reviewed_by"]
        return resolved

    monkeypatch.setattr(
        data_error_reports_repository,
        "update_data_error_report_status",
        fake_update,
    )

    response = _client().patch(
        "/api/v1/admin/community/data-error-reports/r1/status",
        json={"status": "resolved", "reviewed_by": "spoofed-attacker-id"},
    )

    assert response.status_code == 200
    assert captured["reviewed_by"] == MODERATOR_USER.id


def _rating_row(status: str = "pending") -> dict[str, Any]:
    return {
        "id": "66666666-6666-6666-6666-666666666666",
        "user_story_id": None,
        "country_slug": "uruguay",
        "route_id": None,
        "official_expectation_score": 80,
        "real_experience_score": 40,
        "bureaucracy_score": 60,
        "cost_surprise_score": None,
        "banking_difficulty_score": None,
        "safety_feeling_score": None,
        "comment": "Harder than expected.",
        "status": status,
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }


def test_admin_user_story_rating_status_update_ignores_client_supplied_reviewed_by(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    published = _rating_row(status="published")
    captured: dict[str, Any] = {}

    def fake_update(*_a: Any, **_kw: Any) -> dict[str, Any]:
        captured["reviewed_by"] = _kw["reviewed_by"]
        return published

    monkeypatch.setattr(
        user_story_ratings_repository,
        "update_user_story_rating_status",
        fake_update,
    )

    response = _client().patch(
        "/api/v1/admin/community/user-story-ratings/rt1/status",
        json={"status": "published", "reviewed_by": "spoofed-attacker-id"},
    )

    assert response.status_code == 200
    assert captured["reviewed_by"] == MODERATOR_USER.id

"""Public community Q&A submission and listing endpoints."""

from app.api.v1.community import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import (
    community as repository,
    feature_flags as feature_repository,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(app_env="local")
    return TestClient(app)


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_repository,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        feature_repository,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )


def _published_question() -> dict[str, Any]:
    return {
        "id": "33333333-3333-3333-3333-333333333333",
        "country_slug": "uruguay",
        "route_id": None,
        "legal_signal_id": None,
        "topic": "residence",
        "title": "How does it work?",
        "body": "Body text",
        "status": "published",
        "created_by_identity_type": "anonymous_session",
        "created_by_identity_id": "session-1",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "moderated_at": None,
        "moderated_by": None,
    }


def test_public_post_question_creates_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        repository,
        "insert_question",
        lambda *_a, **_kw: {**_published_question(), "status": "pending"},
    )

    response = _client().post(
        "/api/v1/community/questions",
        json={
            "topic": "residence",
            "title": "How does it work?",
            "body": "Body text",
            "created_by_identity_type": "anonymous_session",
            "created_by_identity_id": "local-test",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_public_get_questions_only_shows_published(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_list(_conn: Any, **kwargs: Any) -> list[dict[str, Any]]:
        captured.update(kwargs)
        return [_published_question()]

    monkeypatch.setattr(repository, "list_published_questions", fake_list)

    response = _client().get("/api/v1/community/questions")

    assert response.status_code == 200
    assert all(item["status"] == "published" for item in response.json()["items"])


def test_public_get_pending_question_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_question", lambda *_a, **_kw: None)

    response = _client().get("/api/v1/community/questions/pending-question")

    assert response.status_code == 404


def test_public_post_answer_creates_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        repository, "get_question", lambda *_a, **_kw: _published_question()
    )
    monkeypatch.setattr(
        repository,
        "insert_answer",
        lambda *_a, **_kw: {
            "id": "44444444-4444-4444-4444-444444444444",
            "question_id": "33333333-3333-3333-3333-333333333333",
            "body": "answer",
            "status": "pending",
            "source_ids": [],
            "evidence_item_ids": [],
            "created_by_identity_type": "anonymous_session",
            "created_by_identity_id": "local-test",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "moderated_at": None,
            "moderated_by": None,
        },
    )

    response = _client().post(
        "/api/v1/community/questions/q1/answers",
        json={
            "body": "answer",
            "created_by_identity_type": "anonymous_session",
            "created_by_identity_id": "local-test",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

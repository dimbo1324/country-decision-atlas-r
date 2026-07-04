"""Admin API for generating and listing AI-authored content drafts."""

import pytest
from app.api.v1.admin_ai import router
from app.core.auth import CurrentUser, get_current_active_user
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import ai_drafts as repository
from app.services import ai_drafts as service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()

EDITOR_USER = CurrentUser(
    id="editor-id",
    email="editor@example.local",
    display_name="Editor",
    role="editor",
    status="active",
)


def _client(*, with_admin: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(app_env="local")
    if with_admin:
        app.dependency_overrides[get_current_active_user] = lambda: EDITOR_USER
    return TestClient(app)


def _draft_row() -> dict[str, Any]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "draft_type": "summary",
        "status": "needs_review",
        "country_slug": "uruguay",
        "route_id": None,
        "legal_signal_id": None,
        "source_id": None,
        "evidence_item_id": None,
        "title": "Summary draft: residence",
        "body": "excerpt",
        "summary": "summary",
        "detected_issue": None,
        "provider": "fake",
        "model_name": "fake-grounded-v1",
        "model_version": "v1",
        "input_context": {},
        "citations": [],
        "confidence": "medium",
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def test_generate_summary_draft_requires_admin_auth() -> None:
    client = _client(with_admin=False)

    response = client.post(
        "/api/v1/admin/ai/drafts/generate-summary",
        json={"topic": "residence", "locale": "ru"},
    )

    assert response.status_code == 401


def test_generate_summary_draft_returns_needs_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    monkeypatch.setattr(
        service, "generate_summary_draft", lambda *_a, **_kw: _draft_row()
    )

    response = client.post(
        "/api/v1/admin/ai/drafts/generate-summary",
        json={"topic": "residence", "locale": "ru"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "needs_review"


def test_list_ai_drafts(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    monkeypatch.setattr(
        repository, "list_ai_drafts", lambda *_a, **_kw: [_draft_row()]
    )
    monkeypatch.setattr(repository, "count_ai_drafts", lambda *_a, **_kw: 1)

    response = client.get("/api/v1/admin/ai/drafts")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "needs_review"


def test_get_ai_draft_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client()
    monkeypatch.setattr(repository, "get_ai_draft", lambda *_a, **_kw: None)

    response = client.get("/api/v1/admin/ai/drafts/missing")

    assert response.status_code == 404


def test_patch_ai_draft_status_to_approved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    approved = {**_draft_row(), "status": "approved", "reviewed_by": "editor"}
    monkeypatch.setattr(
        repository, "update_ai_draft_status", lambda *_a, **_kw: approved
    )

    response = client.patch(
        "/api/v1/admin/ai/drafts/draft-1/status",
        json={"status": "approved", "reviewed_by": "editor"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"

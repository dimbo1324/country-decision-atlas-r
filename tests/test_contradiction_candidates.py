"""Detection and status updates for AI contradiction candidates."""

import inspect
import pytest
from app.api.v1.admin_ai import router
from app.core.auth import CurrentUser, get_current_active_user
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import contradiction_candidates as repository
from app.schemas.ai import AICitation, AIContextItem
from app.services import contradiction_candidates as service
from app.services.ai_context import AIContextPackage
from fastapi import FastAPI, HTTPException
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


def _candidate_row() -> dict[str, Any]:
    return {
        "id": "22222222-2222-2222-2222-222222222222",
        "country_slug": "uruguay",
        "topic": "tax residency",
        "entity_type": None,
        "entity_id": None,
        "severity": "medium",
        "status": "needs_review",
        "summary": "possible contradiction",
        "claim_a": "claim a",
        "claim_b": "claim b",
        "source_ids": ["source-1"],
        "evidence_item_ids": [],
        "detected_by": "fake_ai",
        "provider": "fake",
        "model_name": "fake-grounded-v1",
        "model_version": "v1",
        "confidence": "low",
        "reviewed_at": None,
        "reviewed_by": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def _two_context_items() -> list[AIContextItem]:
    return [
        AIContextItem(
            entity_type="source",
            entity_id="source-1",
            country_slug="uruguay",
            title="Source A",
            excerpt="Claim from source A.",
            source_ids=["source-1"],
        ),
        AIContextItem(
            entity_type="source",
            entity_id="source-2",
            country_slug="uruguay",
            title="Source B",
            excerpt="Claim from source B.",
            source_ids=["source-2"],
        ),
    ]


def _package(items: list[AIContextItem]) -> AIContextPackage:
    citations = [
        AICitation(
            entity_type=item.entity_type,
            entity_id=item.entity_id,
            title=item.title,
            source_id=item.source_ids[0] if item.source_ids else None,
            country_slug=item.country_slug,
        )
        for item in items
    ]
    return AIContextPackage(
        system_rules=[],
        user_question="tax",
        grounded_context=items,
        citations=citations,
        citation_policy="cite",
        disclaimer_policy="disclaimer",
        locale="ru",
        refusal_reason=None if items else "insufficient",
    )


def test_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "BaseModel" not in source
    assert "INSERT INTO contradiction_candidates" in source


def test_detect_contradiction_candidate_requires_two_context_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service, "build_ask_context", lambda *_a, **_kw: _package([])
    )

    with pytest.raises(HTTPException) as exc_info:
        service.detect_contradiction_candidate(
            CONNECTION,
            Settings(app_env="local"),
            country_slug="uruguay",
            topic="tax",
            entity_type=None,
            entity_id=None,
            locale="ru",
        )
    assert exc_info.value.status_code == 422


def test_detect_contradiction_candidate_creates_needs_review_with_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "build_ask_context",
        lambda *_a, **_kw: _package(_two_context_items()),
    )
    events: dict[str, Any] = {}

    def fake_insert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            **_candidate_row(),
            **{k: v for k, v in kwargs.items() if k in _candidate_row()},
        }

    def fake_event(_conn: Any, **kwargs: Any) -> None:
        events.update(kwargs)

    monkeypatch.setattr(
        repository, "insert_contradiction_candidate", fake_insert
    )
    monkeypatch.setattr(service, "insert_domain_event", fake_event)

    row = service.detect_contradiction_candidate(
        CONNECTION,
        Settings(app_env="local", ai_model_version="test-v2"),
        country_slug="uruguay",
        topic="tax",
        entity_type=None,
        entity_id=None,
        locale="ru",
    )

    assert row["status"] == "needs_review"
    assert row["model_version"] == "test-v2"
    assert events["event_type"] == "contradiction_candidate.created"
    assert events["notifiable"] is False


def test_update_contradiction_candidate_status_requires_explicit_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    confirmed = {
        **_candidate_row(),
        "status": "confirmed",
        "reviewed_by": "editor",
    }
    monkeypatch.setattr(
        repository,
        "update_contradiction_candidate_status",
        lambda *_a, **_kw: confirmed,
    )

    row = service.update_contradiction_candidate_status(
        CONNECTION, "candidate-1", "confirmed", "editor"
    )
    assert row["status"] == "confirmed"


def test_admin_endpoints_require_admin_auth() -> None:
    client = _client(with_admin=False)

    response = client.post(
        "/api/v1/admin/ai/drafts/detect-contradiction",
        json={"topic": "tax"},
    )

    assert response.status_code == 401


def test_admin_list_contradiction_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    monkeypatch.setattr(
        repository,
        "list_contradiction_candidates",
        lambda *_a, **_kw: [_candidate_row()],
    )
    monkeypatch.setattr(
        repository, "count_contradiction_candidates", lambda *_a, **_kw: 1
    )

    response = client.get("/api/v1/admin/contradiction-candidates")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "needs_review"

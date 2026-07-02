from app.api.v1.ai import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import (
    ai_context as ai_context_repository,
    ai_interactions,
    feature_flags as ff_repo,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _client(monkeypatch: Any, settings: Settings | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: (
        settings or Settings(app_env="local")
    )
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )
    monkeypatch.setattr(
        ai_interactions, "insert_ai_interaction_log", lambda *_a, **_kw: {}
    )
    return TestClient(app)


def _context_row() -> dict[str, Any]:
    return {
        "entity_type": "country",
        "entity_id": "country-1",
        "country_slug": "uruguay",
        "title": "Uruguay",
        "excerpt": "Published context for Uruguay.",
        "url_path": "/countries/uruguay",
        "source_ids": [],
        "evidence_item_ids": [],
        "confidence": "medium",
        "freshness_status": "fresh",
        "last_verified_at": None,
    }


def test_ask_with_context_returns_answer_and_citations(monkeypatch: Any) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository,
        "search_ai_context_items",
        lambda *_a, **_kw: [_context_row()],
    )

    response = client.post(
        "/api/v1/ai/ask",
        json={"question": "What is known about Uruguay?", "locale": "ru"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["citations"]
    assert body["disclaimer"].startswith("Это не юридическая консультация")


def test_ask_without_context_returns_refusal(monkeypatch: Any) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository,
        "search_ai_context_items",
        lambda *_a, **_kw: [],
    )

    response = client.post(
        "/api/v1/ai/ask",
        json={"question": "Ответь без источников", "locale": "ru"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is True
    assert body["citations"] == []


def test_feature_disabled_returns_403(monkeypatch: Any) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "disabled",
            "access_tier": "public",
            "default_enabled": False,
        },
    )

    response = client.post(
        "/api/v1/ai/ask",
        json={"question": "What is known about Uruguay?", "locale": "ru"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["error"]["code"] == "feature_disabled"


def test_ai_mode_off_returns_403(monkeypatch: Any) -> None:
    client = _client(monkeypatch, Settings(app_env="local", ai_mode="off"))

    response = client.post(
        "/api/v1/ai/ask",
        json={"question": "What is known about Uruguay?", "locale": "ru"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["error"]["code"] == "ai_disabled"


def test_interaction_log_written_without_raw_question(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository,
        "search_ai_context_items",
        lambda *_a, **_kw: [_context_row()],
    )
    monkeypatch.setattr(
        ai_interactions,
        "insert_ai_interaction_log",
        lambda *_a, **kwargs: captured.update(kwargs) or {},
    )

    client.post(
        "/api/v1/ai/ask",
        json={
            "question": "Мой email test@example.com, что про Уругвай?",
            "locale": "ru",
        },
    )

    assert captured["query_hash"]
    assert "test@example.com" not in captured["sanitized_preview"]
    assert "question" not in captured

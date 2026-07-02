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


def _client(monkeypatch: Any) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(app_env="local")
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


def test_decision_intent_returns_hints_without_running_decision(
    monkeypatch: Any,
) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository,
        "get_decision_ai_context",
        lambda *_a, **_kw: [
            {
                "entity_type": "country",
                "entity_id": "country-1",
                "country_slug": "uruguay",
                "title": "Uruguay",
                "excerpt": "Published context.",
                "url_path": "/countries/uruguay",
                "source_ids": [],
                "evidence_item_ids": [],
                "confidence": "medium",
                "freshness_status": "fresh",
                "last_verified_at": None,
            }
        ],
    )

    response = client.post(
        "/api/v1/ai/decision-intent",
        json={
            "text": "I want to relocate with family, low budget, safety matters.",
            "locale": "ru",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["scenario_slug"]
    assert body["persona_slug"]
    assert body["candidate_country_slugs"]
    assert body["citations"]

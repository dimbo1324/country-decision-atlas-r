from app.api.v1.ai import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import (
    ai_context as ai_context_repository,
    ai_interactions,
    feature_flags as ff_repo,
)
from app.services import decision_engine
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


def test_explain_number_returns_citations(monkeypatch: Any) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository,
        "get_metric_ai_context",
        lambda *_a, **_kw: [
            {
                "entity_type": "trust_score",
                "entity_id": "trust-1",
                "country_slug": "uruguay",
                "title": "trust_score",
                "excerpt": "trust_score: value=75, label=high",
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
        "/api/v1/ai/explain-number",
        json={
            "number_type": "trust_score",
            "country_slug": "uruguay",
            "value": 75,
            "locale": "ru",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["citations"]
    assert body["what_it_means"]
    assert body["what_it_does_not_mean"]


def test_explain_number_does_not_run_decision(monkeypatch: Any) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        ai_context_repository, "get_metric_ai_context", lambda *_a, **_kw: []
    )
    monkeypatch.setattr(
        decision_engine,
        "run_decision",
        lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError("recomputed")),
        raising=False,
    )

    response = client.post(
        "/api/v1/ai/explain-number",
        json={
            "number_type": "decision_score",
            "country_slug": "uruguay",
            "value": 80,
            "locale": "ru",
        },
    )

    assert response.status_code == 200
    assert response.json()["refused"] is True

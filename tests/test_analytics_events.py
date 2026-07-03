"""Session-id hashing and metadata sanitization for analytics events."""

from app.api.v1.analytics import router
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.repositories import analytics as analytics_repository
from app.schemas.analytics import AnalyticsEventCreate
from app.services import analytics as analytics_service
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from psycopg import Connection
from pydantic import ValidationError
import pytest
from typing import Any, cast
from uuid import UUID, uuid4


CONNECTION = cast(Connection[Any], object())


def _payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "event_type": "page_view",
        "session_id": "local-session-123",
        "source": "web",
        "path": "/",
        "locale": "ru",
        "metadata": {"surface": "home"},
    }
    data.update(overrides)
    return data


def test_hash_session_id_is_deterministic() -> None:
    first = analytics_service.hash_session_id("session-123", "salt")
    second = analytics_service.hash_session_id("session-123", "salt")
    assert first == second
    assert len(first) == 64


def test_hash_session_id_differs_by_session() -> None:
    first = analytics_service.hash_session_id("session-123", "salt")
    second = analytics_service.hash_session_id("session-456", "salt")
    assert first != second


def test_sanitize_metadata_stores_safe_keys() -> None:
    result = analytics_service.sanitize_metadata({"surface": "home", "count": 2})
    assert result == {"surface": "home", "count": 2}


@pytest.mark.parametrize("key", ["email", "token", "ip", "user_agent", "admin_token"])
def test_metadata_forbidden_keys_rejected(key: str) -> None:
    with pytest.raises(HTTPException) as exc_info:
        analytics_service.sanitize_metadata({key: "secret"})
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert exc_info.value.status_code == 422
    assert detail["error"]["code"] == "analytics_pii_not_allowed"


def test_metadata_too_large_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        analytics_service.sanitize_metadata({"large": "x" * 257})
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert exc_info.value.status_code == 422
    assert detail["error"]["code"] == "analytics_payload_invalid"


def test_metadata_too_many_keys_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        analytics_service.sanitize_metadata({f"k{i}": i for i in range(21)})
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert exc_info.value.status_code == 422
    assert detail["error"]["code"] == "analytics_payload_invalid"


def test_event_type_not_snake_case_rejected() -> None:
    with pytest.raises(ValidationError):
        AnalyticsEventCreate.model_validate(_payload(event_type="PageView"))


def test_invalid_source_rejected() -> None:
    with pytest.raises(ValidationError):
        AnalyticsEventCreate.model_validate(_payload(source="browser"))


def test_record_event_disabled_does_not_store(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"insert": False}

    def fake_insert(*_args: Any, **_kwargs: Any) -> UUID:
        called["insert"] = True
        return uuid4()

    monkeypatch.setattr(analytics_repository, "insert_analytics_event", fake_insert)
    response = analytics_service.record_analytics_event(
        CONNECTION,
        AnalyticsEventCreate.model_validate(_payload()),
        Settings(analytics_enabled=False),
    )
    assert response.accepted is True
    assert response.stored is False
    assert response.reason == "analytics_disabled"
    assert called["insert"] is False


def test_record_event_stores_hashed_session(monkeypatch: pytest.MonkeyPatch) -> None:
    inserted: dict[str, Any] = {}
    event_id = uuid4()

    def fake_insert(_conn: Connection[Any], **kwargs: Any) -> UUID:
        inserted.update(kwargs)
        return event_id

    monkeypatch.setattr(analytics_repository, "insert_analytics_event", fake_insert)
    response = analytics_service.record_analytics_event(
        CONNECTION,
        AnalyticsEventCreate.model_validate(_payload()),
        Settings(analytics_salt="test-salt"),
    )
    assert response.accepted is True
    assert response.stored is True
    assert response.event_id == event_id
    assert inserted["session_hash"] != "local-session-123"
    assert len(inserted["session_hash"]) == 64
    assert inserted["metadata"] == {"surface": "home"}


def test_repository_insert_analytics_event(monkeypatch: pytest.MonkeyPatch) -> None:
    event_id = uuid4()
    captured: dict[str, Any] = {}

    def fake_fetch_one(
        _conn: Connection[Any],
        query: str,
        params: tuple[Any, ...],
    ) -> dict[str, Any]:
        captured["query"] = query
        captured["params"] = params
        return {"id": event_id}

    monkeypatch.setattr(analytics_repository, "fetch_one", fake_fetch_one)
    result = analytics_repository.insert_analytics_event(
        CONNECTION,
        session_hash="a" * 64,
        event_type="page_view",
        source="web",
        path="/",
        locale="ru",
        country_slug="russia",
        scenario_slug=None,
        persona_slug=None,
        route_id=None,
        entity_type=None,
        entity_id=None,
        metadata={"surface": "home"},
    )
    assert result == event_id
    assert "session_id" not in captured["query"]
    assert "local-session-123" not in captured["params"]


def test_api_endpoint_stores_event(monkeypatch: pytest.MonkeyPatch) -> None:
    event_id = uuid4()

    def fake_insert(_conn: Connection[Any], **_kwargs: Any) -> UUID:
        return event_id

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings()
    monkeypatch.setattr(analytics_repository, "insert_analytics_event", fake_insert)
    response = TestClient(app).post("/api/v1/analytics/events", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["stored"] is True
    assert body["event_id"] == str(event_id)
    assert "session_id" not in body
    assert "session_hash" not in body


def test_api_endpoint_disabled_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"insert": False}

    def fake_insert(_conn: Connection[Any], **_kwargs: Any) -> UUID:
        called["insert"] = True
        return uuid4()

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings(analytics_enabled=False)
    monkeypatch.setattr(analytics_repository, "insert_analytics_event", fake_insert)
    response = TestClient(app).post("/api/v1/analytics/events", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["stored"] is False
    assert body["reason"] == "analytics_disabled"
    assert body["event_id"] is None
    assert called["insert"] is False


def test_api_endpoint_rejects_pii() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_settings] = lambda: Settings()
    response = TestClient(app).post(
        "/api/v1/analytics/events",
        json=_payload(metadata={"email": "test@example.test"}),
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "analytics_pii_not_allowed"

"""Admin endpoints for recomputing country drift, including auth/role enforcement."""

import pytest
from app.api.v1 import country_drift as country_drift_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.schemas.country_drift import CountryDriftRecomputeRequest
from app.services.country_drift import CountryDriftStoredResult
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import MagicMock


ADMIN_USER = CurrentUser(
    id="admin-id",
    email="admin@example.local",
    display_name="Admin",
    role="admin",
    status="active",
)
REGULAR_USER = CurrentUser(
    id="user-id",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def test_admin_recompute_all_enqueues_request_instead_of_computing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        country_drift_api,
        "enqueue_recompute_request",
        lambda *_a, **_kw: "event-123",
    )
    conn = MagicMock()
    result = country_drift_api.admin_recompute_all_country_drift(
        CountryDriftRecomputeRequest(dry_run=False), conn, ADMIN_USER
    )
    assert result.queued is True
    assert result.resource == "country_drift"
    assert result.dry_run is False
    assert result.event_id == "event-123"
    conn.commit.assert_called_once()


def test_admin_recompute_all_forwards_dry_run_and_emit_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_enqueue(_conn: Any, **kwargs: Any) -> str:
        captured.update(kwargs)
        return "event-456"

    monkeypatch.setattr(
        country_drift_api, "enqueue_recompute_request", fake_enqueue
    )
    conn = MagicMock()
    country_drift_api.admin_recompute_all_country_drift(
        CountryDriftRecomputeRequest(dry_run=True, emit_events=False),
        conn,
        ADMIN_USER,
    )
    assert captured["resource"] == "country_drift"
    assert captured["dry_run"] is True
    assert captured["extra_payload"] == {"emit_events": False}


def test_admin_recompute_country_returns_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = CountryDriftStoredResult(
        country_slug="argentina",
        country_not_found=False,
        dry_run=False,
        computed=True,
        stored=True,
        label="mildly_positive",
        previous_label="stable",
        confidence="medium",
        net_score=None,
        event_count=6,
        event_emitted=True,
        error=None,
    )
    monkeypatch.setattr(
        country_drift_api,
        "compute_and_store_country_drift",
        lambda *_a, **_kw: stored,
    )
    conn = MagicMock()
    result = country_drift_api.admin_recompute_country_drift(
        "argentina",
        CountryDriftRecomputeRequest(dry_run=False),
        conn,
        ADMIN_USER,
    )
    assert result.computed is True
    assert result.stored is True
    assert result.label == "mildly_positive"
    assert result.event_emitted is True


def _admin_client(
    monkeypatch: Any, current_user: CurrentUser | None = None
) -> TestClient:
    from app.api.v1.country_drift import admin_router

    app = FastAPI()
    app.include_router(admin_router, prefix="/api/v1")
    conn = MagicMock()
    app.dependency_overrides[get_connection] = lambda: conn
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    monkeypatch.setattr(
        country_drift_api,
        "enqueue_recompute_request",
        lambda *_a, **_kw: "event-789",
    )
    return TestClient(app, raise_server_exceptions=False)


def test_admin_recompute_without_token_returns_401(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch)
    response = client.post(
        "/api/v1/admin/country-drift/recompute", json={"dry_run": False}
    )
    assert response.status_code == 401


def test_admin_recompute_with_user_role_returns_403(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, current_user=REGULAR_USER)
    response = client.post(
        "/api/v1/admin/country-drift/recompute",
        json={"dry_run": False},
        headers={"Authorization": "Bearer user-session-token"},
    )
    assert response.status_code == 403


def test_admin_recompute_with_admin_role_returns_202(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, current_user=ADMIN_USER)
    response = client.post(
        "/api/v1/admin/country-drift/recompute",
        json={"dry_run": False},
        headers={"Authorization": "Bearer admin-session-token"},
    )
    assert response.status_code == 202


def test_dry_run_request_is_still_recorded_and_committed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Unlike the old synchronous recompute, dry_run no longer skips work:
    # the endpoint only ever records that a recompute was *requested* (P2-3,
    # Аудит-эпизод 5) - it never runs the actual per-country computation
    # inline, so there is nothing for dry_run to skip except that audit
    # record itself, and recording it is cheap and useful either way.
    monkeypatch.setattr(
        country_drift_api,
        "enqueue_recompute_request",
        lambda *_a, **_kw: "event-999",
    )
    conn = MagicMock()
    country_drift_api.admin_recompute_all_country_drift(
        CountryDriftRecomputeRequest(dry_run=True), conn, ADMIN_USER
    )
    conn.commit.assert_called_once()


def test_emit_events_false_still_writes_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored = CountryDriftStoredResult(
        country_slug="argentina",
        country_not_found=False,
        dry_run=False,
        computed=True,
        stored=True,
        label="stable",
        previous_label="negative",
        confidence="medium",
        net_score=None,
        event_count=5,
        event_emitted=False,
        error=None,
    )
    monkeypatch.setattr(
        country_drift_api,
        "compute_and_store_country_drift",
        lambda *_a, **_kw: stored,
    )
    conn = MagicMock()
    result = country_drift_api.admin_recompute_country_drift(
        "argentina",
        CountryDriftRecomputeRequest(dry_run=False, emit_events=False),
        conn,
        ADMIN_USER,
    )
    assert result.stored is True
    assert result.event_emitted is False

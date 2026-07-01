from app.api.v1 import country_drift as country_drift_api
from app.core import admin_auth as admin_auth_module
from app.core.config import Settings
from app.core.database import get_connection
from app.schemas.country_drift import CountryDriftRecomputeRequest
from app.services.country_drift import (
    CountryDriftBatchResult,
    CountryDriftStoredResult,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from typing import Any
from unittest.mock import MagicMock


def test_admin_recompute_all_returns_batch_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batch = CountryDriftBatchResult(
        countries_processed=3,
        snapshots_written=3,
        events_emitted=1,
        insufficient_data_count=0,
        errors=[],
    )
    monkeypatch.setattr(
        country_drift_api,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    conn = MagicMock()
    result = country_drift_api.admin_recompute_all_country_drift(
        CountryDriftRecomputeRequest(dry_run=False), conn, "admin-token"
    )
    assert result.countries_processed == 3
    assert result.snapshots_written == 3
    assert result.events_emitted == 1
    assert result.insufficient_data_count == 0


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
        "argentina", CountryDriftRecomputeRequest(dry_run=False), conn, "admin-token"
    )
    assert result.computed is True
    assert result.stored is True
    assert result.label == "mildly_positive"
    assert result.event_emitted is True


def _admin_client(monkeypatch: Any, token: str = "secret-token") -> TestClient:
    from app.api.v1.country_drift import admin_router

    app = FastAPI()
    app.include_router(admin_router, prefix="/api/v1")
    conn = MagicMock()
    app.dependency_overrides[get_connection] = lambda: conn
    monkeypatch.setattr(
        admin_auth_module,
        "get_settings",
        lambda: Settings(app_env="local", admin_token=token),
    )
    batch = CountryDriftBatchResult(
        countries_processed=0,
        snapshots_written=0,
        events_emitted=0,
        insufficient_data_count=0,
        errors=[],
    )
    monkeypatch.setattr(
        country_drift_api,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    return TestClient(app, raise_server_exceptions=False)


def test_admin_recompute_without_token_returns_401(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch)
    response = client.post(
        "/api/v1/admin/country-drift/recompute", json={"dry_run": False}
    )
    assert response.status_code == 401


def test_admin_recompute_with_wrong_token_returns_401(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, token="secret-token")
    response = client.post(
        "/api/v1/admin/country-drift/recompute",
        json={"dry_run": False},
        headers={"X-Admin-Token": "wrong-token"},
    )
    assert response.status_code == 401


def test_admin_recompute_with_correct_token_returns_200(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, token="secret-token")
    response = client.post(
        "/api/v1/admin/country-drift/recompute",
        json={"dry_run": False},
        headers={"X-Admin-Token": "secret-token"},
    )
    assert response.status_code == 200


def test_dry_run_does_not_commit_call(monkeypatch: pytest.MonkeyPatch) -> None:
    batch = CountryDriftBatchResult(
        countries_processed=1,
        snapshots_written=0,
        events_emitted=0,
        insufficient_data_count=1,
        errors=[],
    )
    monkeypatch.setattr(
        country_drift_api,
        "compute_and_store_all_country_drifts",
        lambda *_a, **_kw: batch,
    )
    conn = MagicMock()
    country_drift_api.admin_recompute_all_country_drift(
        CountryDriftRecomputeRequest(dry_run=True), conn, "admin-token"
    )
    conn.commit.assert_not_called()


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
        "admin-token",
    )
    assert result.stored is True
    assert result.event_emitted is False

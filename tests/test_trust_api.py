"""Country trust API: response shape, not-found handling, and admin batch recompute."""

from app.api.v1 import trust as trust_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import trust as trust_repo
from app.schemas.trust import TrustRecomputeRequest
from datetime import UTC, datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], object())

_NOW = datetime(2025, 6, 1, tzinfo=UTC)

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

_TRUST_ROW = {
    "country_slug": "russia",
    "trust_score": 72.5,
    "trust_label": "high",
    "confidence": "high",
    "freshness_status": "fresh",
    "source_count": 15,
    "evidence_count": 20,
    "legal_signal_count": 8,
    "route_count": 5,
    "platform_metric_count": 3,
    "contradiction_score": 10.0,
    "freshness_score": 100.0,
    "evidence_depth_score": 100.0,
    "source_quality_score": 100.0,
    "review_coverage_score": 100.0,
    "last_verified_at": datetime(2025, 3, 1, tzinfo=UTC),
    "computed_at": _NOW,
    "expires_at": None,
    "methodology_version": "v1.0",
    "input_summary": {
        "components": {
            "source_quality_score": 100.0,
            "evidence_depth_score": 100.0,
            "freshness_score": 100.0,
            "review_coverage_score": 100.0,
            "contradiction_component": 90.0,
        }
    },
}


def test_get_country_trust_returns_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(trust_repo, "get_country_trust_score", lambda *_: _TRUST_ROW)
    result = trust_api.get_country_trust("russia", CONNECTION)
    assert result.country_slug == "russia"
    assert result.trust_label == "high"
    assert result.trust_score is not None
    assert result.trust_score == pytest.approx(72.5)


def test_get_country_trust_returns_404_when_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(trust_repo, "get_country_trust_score", lambda *_: None)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        trust_api.get_country_trust("nonexistent", CONNECTION)
    assert exc.value.status_code == 404


def test_get_country_trust_components_populated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(trust_repo, "get_country_trust_score", lambda *_: _TRUST_ROW)
    result = trust_api.get_country_trust("russia", CONNECTION)
    assert result.components is not None
    assert result.components.source_quality_score == pytest.approx(100.0)
    assert result.components.freshness_score == pytest.approx(100.0)


def test_admin_recompute_all_returns_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    summary = {
        "feature_enabled": True,
        "dry_run": False,
        "countries_processed": 3,
        "countries_computed": 3,
        "countries_stored": 3,
        "countries_failed": 0,
        "errors": [],
    }
    monkeypatch.setattr(
        trust_api,
        "compute_and_store_trust_for_all_countries",
        lambda *_a, **_kw: summary,
    )
    conn = MagicMock()
    result = trust_api.admin_recompute_all_trust(
        TrustRecomputeRequest(dry_run=False), conn, ADMIN_USER
    )
    assert result.countries_processed == 3
    assert result.feature_enabled is True


def test_admin_recompute_country_returns_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    country_result = {
        "country_slug": "russia",
        "feature_enabled": True,
        "country_not_found": False,
        "dry_run": False,
        "computed": True,
        "stored": True,
        "error": None,
        "trust_label": "high",
        "trust_score": 72.5,
        "confidence": "high",
        "freshness_status": "fresh",
    }
    monkeypatch.setattr(
        trust_api,
        "compute_and_store_trust_for_country",
        lambda *_a, **_kw: country_result,
    )
    conn = MagicMock()
    result = trust_api.admin_recompute_country_trust(
        "russia", TrustRecomputeRequest(dry_run=False), conn, ADMIN_USER
    )
    assert result.computed is True
    assert result.stored is True
    assert result.trust_label == "high"


def test_get_country_trust_disclaimer_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(trust_repo, "get_country_trust_score", lambda *_: _TRUST_ROW)
    result = trust_api.get_country_trust("russia", CONNECTION)
    assert (
        "data quality" in result.disclaimer.lower()
        or "not" in result.disclaimer.lower()
    )


def _admin_client(
    monkeypatch: Any, current_user: CurrentUser | None = None
) -> TestClient:
    from app.api.v1.trust import admin_router

    app = FastAPI()
    app.include_router(admin_router, prefix="/api/v1")
    conn = MagicMock()
    app.dependency_overrides[get_connection] = lambda: conn
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    summary = {
        "feature_enabled": True,
        "dry_run": False,
        "countries_processed": 0,
        "countries_computed": 0,
        "countries_stored": 0,
        "countries_failed": 0,
        "errors": [],
    }
    monkeypatch.setattr(
        trust_api,
        "compute_and_store_trust_for_all_countries",
        lambda *_a, **_kw: summary,
    )
    return TestClient(app, raise_server_exceptions=False)


def test_admin_recompute_without_token_returns_401(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch)
    response = client.post("/api/v1/admin/trust/recompute", json={"dry_run": False})
    assert response.status_code == 401


def test_admin_recompute_with_user_role_returns_403(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, current_user=REGULAR_USER)
    response = client.post(
        "/api/v1/admin/trust/recompute",
        json={"dry_run": False},
        headers={"Authorization": "Bearer user-session-token"},
    )
    assert response.status_code == 403


def test_admin_recompute_with_admin_role_returns_200(monkeypatch: Any) -> None:
    client = _admin_client(monkeypatch, current_user=ADMIN_USER)
    response = client.post(
        "/api/v1/admin/trust/recompute",
        json={"dry_run": False},
        headers={"Authorization": "Bearer admin-session-token"},
    )
    assert response.status_code == 200

"""Author metrics public/authenticated API: RBAC gates, deny-by-default, and overlay isolation from core surfaces."""

import pytest
from app.api.v1 import admin_author_metrics, author_metrics
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import capabilities as capabilities_repository
from app.services import author_metrics as author_metrics_service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import MagicMock


CONNECTION = MagicMock()
USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)
MODERATOR = CurrentUser(
    id="22222222-2222-2222-2222-222222222222",
    email="mod@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)


def _client(current_user: CurrentUser | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(author_metrics.router, prefix="/api/v1")
    app.include_router(admin_author_metrics.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app)


def test_public_country_overlay_endpoint_requires_no_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        author_metrics_service,
        "get_author_metrics_for_country",
        lambda *_a, **_kw: {"country_slug": "uruguay", "items": [], "total": 0},
    )

    response = _client().get("/api/v1/countries/uruguay/author-metrics")

    assert response.status_code == 200
    assert response.json()["country_slug"] == "uruguay"


def test_public_author_metrics_listing_requires_no_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        author_metrics_service,
        "list_public_definitions_for_author",
        lambda *_a, **_kw: {"items": [], "total": 0},
    )

    response = _client().get(f"/api/v1/authors/{USER.id}/metrics")

    assert response.status_code == 200


def test_me_author_metrics_endpoint_requires_auth() -> None:
    response = _client().get("/api/v1/me/author-metrics")
    assert response.status_code == 401


def test_me_author_metrics_denies_user_without_capability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: False
    )

    response = _client(USER).get("/api/v1/me/author-metrics")

    assert response.status_code == 403


def test_me_author_metrics_allows_user_with_capability_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: True
    )
    monkeypatch.setattr(
        author_metrics_service,
        "list_my_definitions",
        lambda *_a, **_kw: {"items": [], "total": 0},
    )

    response = _client(USER).get("/api/v1/me/author-metrics")

    assert response.status_code == 200


def test_create_my_author_metric_commits_and_returns_definition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: True
    )
    captured: dict[str, Any] = {}

    def fake_create(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {
            "id": "metric-1",
            "slug": "cost-of-living",
            "name_en": "Cost of Living",
            "name_ru": "Стоимость жизни",
            "methodology_en": "",
            "methodology_ru": "",
            "polarity": "lower_is_better",
            "scale_min": 0,
            "scale_max": 100,
            "license": "platform",
            "author": {"user_id": USER.id, "display_name": "User"},
            "forked_from_id": None,
            "version": 1,
            "published_at": None,
            "status": "draft",
            "visibility": "private",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "submitted_at": None,
            "archived_at": None,
            "rejected_at": None,
            "moderation_reason": None,
        }

    monkeypatch.setattr(
        author_metrics_service, "create_my_definition", fake_create
    )

    response = _client(USER).post(
        "/api/v1/me/author-metrics",
        json={
            "slug": "cost-of-living",
            "name_en": "Cost of Living",
            "name_ru": "Стоимость жизни",
        },
    )

    assert response.status_code == 201
    assert captured["current_user"].id == USER.id
    CONNECTION.commit.assert_called()


def test_regular_user_cannot_approve_author_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: False
    )

    response = _client(USER).post(
        "/api/v1/admin/author-metrics/metric-1/approve"
    )

    assert response.status_code == 403


def test_moderator_can_approve_author_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        author_metrics_service,
        "approve_definition",
        lambda *_a, **_kw: {
            "id": "metric-1",
            "slug": "cost-of-living",
            "name_en": "Cost of Living",
            "name_ru": "Стоимость жизни",
            "methodology_en": "x" * 130,
            "methodology_ru": "y" * 130,
            "polarity": "lower_is_better",
            "scale_min": 0,
            "scale_max": 100,
            "license": "platform",
            "author": {"user_id": USER.id, "display_name": "User"},
            "forked_from_id": None,
            "version": 1,
            "published_at": "2026-01-03T00:00:00Z",
            "status": "published",
            "visibility": "public",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-03T00:00:00Z",
            "submitted_at": "2026-01-02T00:00:00Z",
            "archived_at": None,
            "rejected_at": None,
            "moderation_reason": None,
            "author_user_id": USER.id,
            "moderated_by": MODERATOR.id,
            "moderated_at": "2026-01-03T00:00:00Z",
        },
    )

    response = _client(MODERATOR).post(
        "/api/v1/admin/author-metrics/metric-1/approve"
    )

    assert response.status_code == 200
    assert response.json()["definition"]["status"] == "published"


def test_admin_author_metrics_queue_requires_auth() -> None:
    response = _client().get("/api/v1/admin/author-metrics")
    assert response.status_code == 401


def test_subscriptions_feed_requires_auth() -> None:
    response = _client().get("/api/v1/me/subscriptions/feed")
    assert response.status_code == 401


def test_country_page_overlay_isolated_from_core_error_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.errors import api_error

    def _raise(*_a: Any, **_kw: Any) -> Any:
        raise api_error(404, "country_not_found", "Country was not found.", {})

    monkeypatch.setattr(
        author_metrics_service, "get_author_metrics_for_country", _raise
    )

    response = _client().get("/api/v1/countries/nowhere/author-metrics")

    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "country_not_found"

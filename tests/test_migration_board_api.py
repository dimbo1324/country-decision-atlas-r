"""Migration Board public/authenticated API: listing, post creation, and role-gated moderation actions."""

from app.api.v1 import admin_migration_board, migration_board
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.services import migration_board as migration_board_service
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
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
    app.include_router(migration_board.router, prefix="/api/v1")
    app.include_router(admin_migration_board.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app)


def test_public_listing_endpoint_returns_privacy_safe_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "list_public_posts",
        lambda *_a, **_kw: {
            "items": [
                {
                    "id": "post-1",
                    "title": "Moving to Uruguay",
                    "summary": "Preparing documents and housing research.",
                    "author": {"display_name": "Member"},
                    "destination_country": {
                        "id": "country-1",
                        "slug": "uruguay",
                        "name": "Uruguay",
                    },
                    "origin_country": None,
                    "route": None,
                    "scenario": None,
                    "persona": None,
                    "target_city": None,
                    "target_month": None,
                    "timeline_window": "6_12_months",
                    "budget_range": "undisclosed",
                    "household_type": "solo",
                    "migration_stage": "researching",
                    "companion_goal": "info_exchange",
                    "preferred_language": "en",
                    "visibility": "public",
                    "contact_requests_enabled": True,
                    "tags": [],
                    "published_at": None,
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        },
    )

    response = _client().get("/api/v1/migration-board/posts")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["author"] == {"display_name": "Member"}
    assert "email" not in str(body)
    assert "telegram_user_id" not in str(body)


def test_me_endpoint_requires_auth() -> None:
    response = _client().get("/api/v1/me/migration-board/posts")
    assert response.status_code == 401


def test_authenticated_user_can_create_post(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_create(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {
            "id": "post-1",
            "title": "Moving to Uruguay",
            "summary": "Preparing documents and housing research.",
            "destination_country": {
                "id": "country-1",
                "slug": "uruguay",
                "name": "Uruguay",
            },
            "origin_country": None,
            "route": None,
            "scenario": None,
            "persona": None,
            "target_city": None,
            "target_month": None,
            "timeline_window": "unknown",
            "budget_range": "undisclosed",
            "household_type": "solo",
            "migration_stage": "researching",
            "companion_goal": "info_exchange",
            "preferred_language": "en",
            "visibility": "members_only",
            "contact_requests_enabled": True,
            "tags": [],
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "status": "draft",
            "moderation_status": "pending",
            "risk_acknowledged": True,
            "legal_disclaimer_acknowledged": True,
        }

    monkeypatch.setattr(migration_board_service, "create_user_post", fake_create)

    response = _client(USER).post(
        "/api/v1/me/migration-board/posts",
        json={
            "destination_country_slug": "uruguay",
            "title": "Moving to Uruguay",
            "summary": "Preparing documents and housing research.",
            "risk_acknowledged": True,
            "legal_disclaimer_acknowledged": True,
        },
    )

    assert response.status_code == 201
    assert captured["current_user"].id == USER.id
    CONNECTION.commit.assert_called()


def test_regular_user_cannot_approve_post() -> None:
    response = _client(USER).post("/api/v1/admin/migration-board/posts/post-1/approve")
    assert response.status_code == 403


def test_moderator_can_approve_post(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        migration_board_service,
        "approve_post",
        lambda *_a, **_kw: {
            "id": "post-1",
            "user_id": "user-1",
            "author_display_name": "User",
            "title": "Moving to Uruguay",
            "summary": "Preparing documents and housing research.",
            "destination_country": {
                "id": "country-1",
                "slug": "uruguay",
                "name": "Uruguay",
            },
            "origin_country": None,
            "route": None,
            "scenario": None,
            "persona": None,
            "target_city": None,
            "target_month": None,
            "timeline_window": "unknown",
            "budget_range": "undisclosed",
            "household_type": "solo",
            "migration_stage": "researching",
            "companion_goal": "info_exchange",
            "preferred_language": "en",
            "visibility": "public",
            "contact_requests_enabled": True,
            "tags": [],
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "status": "published",
            "moderation_status": "approved",
            "risk_acknowledged": True,
            "legal_disclaimer_acknowledged": True,
        },
    )

    response = _client(MODERATOR).post(
        "/api/v1/admin/migration-board/posts/post-1/approve"
    )

    assert response.status_code == 200
    assert response.json()["post"]["status"] == "published"

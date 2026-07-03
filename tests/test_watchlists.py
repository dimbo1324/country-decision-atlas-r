"""Personal watchlist: feature gating, listing, and adding countries."""

from app.api.v1 import watchlists as watchlists_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import countries as countries_repository, watchlists as repository
from app.services import feature_flags as feature_flags_service, watchlists as service
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()

CURRENT_USER = CurrentUser(
    id="user-1",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)

_COUNTRY = {"id": "country-1", "slug": "uruguay", "name": "Uruguay"}


def _watchlist_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "watchlist-1",
        "user_id": "user-1",
        "country_slug": "uruguay",
        "country_name": "Uruguay",
        "status": "active",
        "notify_legal_signals": True,
        "notify_drift_changes": True,
        "notify_route_updates": False,
        "notes": None,
        "created_source": "web",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
        "archived_at": None,
    }
    row.update(overrides)
    return row


def _enable_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_a, **_kw: True
    )


def _disable_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_a, **_kw: False
    )


def test_list_user_watchlist_disabled_feature_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_feature(monkeypatch)
    with pytest.raises(HTTPException) as exc_info:
        service.list_user_watchlist(CONNECTION, "user-1")
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "feature_disabled"


def test_list_user_watchlist_returns_items(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        repository, "list_user_watchlist", lambda *_a: [_watchlist_row()]
    )
    items = service.list_user_watchlist(CONNECTION, "user-1")
    assert len(items) == 1
    assert items[0]["country_slug"] == "uruguay"


def test_add_country_to_watchlist_country_not_found_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: None
    )
    with pytest.raises(HTTPException) as exc_info:
        service.add_country_to_watchlist(
            CONNECTION, user_id="user-1", country_slug="nowhere"
        )
    assert exc_info.value.status_code == 404
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "country_not_found"


def test_add_country_to_watchlist_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    captured: dict[str, Any] = {}

    def fake_add(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"id": "watchlist-1"}

    monkeypatch.setattr(repository, "add_country_to_watchlist", fake_add)
    monkeypatch.setattr(
        repository,
        "get_user_watchlist_item_by_country_slug",
        lambda *_a: _watchlist_row(),
    )
    item = service.add_country_to_watchlist(
        CONNECTION, user_id="user-1", country_slug="uruguay"
    )
    assert item["country_slug"] == "uruguay"
    assert captured["user_id"] == "user-1"
    assert captured["country_id"] == "country-1"
    assert captured["created_source"] == "web"


def test_remove_country_from_watchlist_calls_archive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    captured: dict[str, Any] = {}

    def fake_archive(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"id": "watchlist-1"}

    monkeypatch.setattr(repository, "archive_country_from_watchlist", fake_archive)
    service.remove_country_from_watchlist(
        CONNECTION, user_id="user-1", country_slug="uruguay"
    )
    assert captured == {"user_id": "user-1", "country_id": "country-1"}


def test_update_watchlist_preferences_rejects_too_long_notes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    with pytest.raises(HTTPException) as exc_info:
        service.update_watchlist_preferences(
            CONNECTION,
            user_id="user-1",
            country_slug="uruguay",
            notify_legal_signals=None,
            notify_drift_changes=None,
            notify_route_updates=None,
            notes="x" * 2001,
            notes_provided=True,
        )
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "notes_too_long"


def test_update_watchlist_preferences_item_not_found_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository, "update_watchlist_preferences", lambda *_a, **_kw: None
    )
    with pytest.raises(HTTPException) as exc_info:
        service.update_watchlist_preferences(
            CONNECTION,
            user_id="user-1",
            country_slug="uruguay",
            notify_legal_signals=True,
            notify_drift_changes=None,
            notify_route_updates=None,
            notes=None,
            notes_provided=False,
        )
    assert exc_info.value.status_code == 404
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "watchlist_item_not_found"


def test_update_watchlist_preferences_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository,
        "update_watchlist_preferences",
        lambda *_a, **_kw: {"id": "watchlist-1"},
    )
    monkeypatch.setattr(
        repository,
        "get_user_watchlist_item_by_country_slug",
        lambda *_a: _watchlist_row(notes="updated notes"),
    )
    item = service.update_watchlist_preferences(
        CONNECTION,
        user_id="user-1",
        country_slug="uruguay",
        notify_legal_signals=False,
        notify_drift_changes=None,
        notify_route_updates=None,
        notes="updated notes",
        notes_provided=True,
    )
    assert item["notes"] == "updated notes"


def test_get_watchlist_status_returns_saved_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository, "get_watchlist_status_for_country", lambda *_a: True
    )
    saved = service.get_watchlist_status(
        CONNECTION, user_id="user-1", country_slug="uruguay"
    )
    assert saved is True


def _client(*, authenticated: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(watchlists_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if authenticated:
        app.dependency_overrides[get_current_active_user] = lambda: CURRENT_USER
    return TestClient(app, raise_server_exceptions=False)


def test_get_my_watchlist_without_auth_returns_401() -> None:
    client = _client(authenticated=False)
    response = client.get("/api/v1/me/watchlist")
    assert response.status_code == 401


def test_get_my_watchlist_returns_items(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        repository, "list_user_watchlist", lambda *_a: [_watchlist_row()]
    )
    client = _client()
    response = client.get(
        "/api/v1/me/watchlist", headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["country_slug"] == "uruguay"


def test_add_country_to_watchlist_endpoint_returns_201(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository, "add_country_to_watchlist", lambda *_a, **_kw: {"id": "watchlist-1"}
    )
    monkeypatch.setattr(
        repository,
        "get_user_watchlist_item_by_country_slug",
        lambda *_a: _watchlist_row(),
    )
    client = _client()
    response = client.post(
        "/api/v1/me/watchlist/countries/uruguay",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 201
    assert response.json()["country_slug"] == "uruguay"


def test_remove_country_from_watchlist_endpoint_returns_204(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository,
        "archive_country_from_watchlist",
        lambda *_a, **_kw: {"id": "watchlist-1"},
    )
    client = _client()
    response = client.delete(
        "/api/v1/me/watchlist/countries/uruguay",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 204


def test_get_country_watchlist_status_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_feature(monkeypatch)
    monkeypatch.setattr(
        countries_repository, "get_active_country_by_slug", lambda *_a: _COUNTRY
    )
    monkeypatch.setattr(
        repository, "get_watchlist_status_for_country", lambda *_a: False
    )
    client = _client()
    response = client.get(
        "/api/v1/countries/uruguay/watchlist-status",
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["country_slug"] == "uruguay"
    assert body["saved"] is False

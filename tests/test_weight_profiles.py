"""Saved user weight profiles: validation, ownership-safe CRUD, and API wiring."""

import pytest
from app.api.v1 import weight_profiles as weight_profiles_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import weight_profiles as repository
from app.services import weight_profiles as service
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from psycopg import Connection, errors as psycopg_errors
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION_MOCK = MagicMock()
CONNECTION = cast(Connection[Any], CONNECTION_MOCK)
NOW = datetime(2026, 7, 4, tzinfo=UTC)
USER_ID = "11111111-1111-1111-1111-111111111111"
PROFILE_ID = "22222222-2222-2222-2222-222222222222"
USER = CurrentUser(
    id=USER_ID,
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)
WEIGHTS = {
    "legalization_score": 20,
    "long_term_status_score": 20,
    "cost_of_living_score": 20,
    "safety_score": 20,
    "business_score": 10,
    "legal_stability_score": 5,
    "source_quality_score": 5,
}


def _row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": PROFILE_ID,
        "user_id": USER_ID,
        "name": "Balanced",
        "scenario_slug": None,
        "weights": WEIGHTS,
        "is_default": False,
        "created_at": NOW,
        "updated_at": NOW,
    }
    row.update(overrides)
    return row


def test_create_profile_validates_and_persists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(repository, "scenario_exists", lambda *_: True)
    monkeypatch.setattr(
        repository, "get_profile_by_name_for_user", lambda *_: None
    )
    monkeypatch.setattr(
        repository, "clear_default_profiles", lambda *_a, **_kw: None
    )

    def fake_create(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return _row(**kwargs)

    monkeypatch.setattr(repository, "create_profile", fake_create)

    result = service.create_user_weight_profile(
        CONNECTION,
        user_id=USER_ID,
        name="  Balanced  ",
        scenario_slug="relocation_residence",
        weights=cast(Any, WEIGHTS),
        is_default=True,
    )

    assert result["name"] == "Balanced"
    assert captured["name"] == "Balanced"
    assert captured["is_default"] is True
    assert set(result["weights"]) == set(WEIGHTS)


def test_create_profile_reuses_custom_weight_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "scenario_exists", lambda *_: True)
    bad_weights = dict(WEIGHTS)
    del bad_weights["safety_score"]

    with pytest.raises(HTTPException) as exc:
        service.create_user_weight_profile(
            CONNECTION,
            user_id=USER_ID,
            name="Incomplete",
            scenario_slug=None,
            weights=cast(Any, bad_weights),
            is_default=False,
        )

    assert "custom_weights_incomplete" in str(exc.value.detail)


def test_duplicate_profile_name_returns_409(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "scenario_exists", lambda *_: True)
    monkeypatch.setattr(
        repository, "get_profile_by_name_for_user", lambda *_: _row()
    )

    with pytest.raises(HTTPException) as exc:
        service.create_user_weight_profile(
            CONNECTION,
            user_id=USER_ID,
            name="Balanced",
            scenario_slug=None,
            weights=cast(Any, WEIGHTS),
            is_default=False,
        )

    assert exc.value.status_code == 409


def test_create_profile_race_on_unique_name_returns_409(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "scenario_exists", lambda *_: True)
    monkeypatch.setattr(
        repository, "get_profile_by_name_for_user", lambda *_: None
    )

    def fake_create(_connection: Any, **_kwargs: Any) -> dict[str, Any]:
        raise psycopg_errors.UniqueViolation("duplicate key value")

    monkeypatch.setattr(repository, "create_profile", fake_create)

    with pytest.raises(HTTPException) as exc:
        service.create_user_weight_profile(
            CONNECTION,
            user_id=USER_ID,
            name="Balanced",
            scenario_slug=None,
            weights=cast(Any, WEIGHTS),
            is_default=False,
        )

    assert exc.value.status_code == 409
    assert "weight_profile_name_exists" in str(exc.value.detail)


def test_update_profile_race_on_unique_name_returns_409(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_profile_for_user", lambda *_: _row())
    monkeypatch.setattr(repository, "scenario_exists", lambda *_: True)
    monkeypatch.setattr(
        repository, "get_profile_by_name_for_user", lambda *_: None
    )

    def fake_update(_connection: Any, **_kwargs: Any) -> dict[str, Any]:
        raise psycopg_errors.UniqueViolation("duplicate key value")

    monkeypatch.setattr(repository, "update_profile", fake_update)

    with pytest.raises(HTTPException) as exc:
        service.update_user_weight_profile(
            CONNECTION,
            user_id=USER_ID,
            profile_id="profile-1",
            fields={"name"},
            name="Taken",
            scenario_slug=None,
            weights=None,
            is_default=None,
        )

    assert exc.value.status_code == 409
    assert "weight_profile_name_exists" in str(exc.value.detail)


def test_resolve_profile_rejects_scenario_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "get_profile_for_user",
        lambda *_: _row(scenario_slug="business_self_employment"),
    )

    with pytest.raises(HTTPException) as exc:
        service.resolve_profile_for_decision(
            CONNECTION,
            profile_id="profile-1",
            user_id=USER_ID,
            scenario_slug="relocation_residence",
        )

    assert exc.value.status_code == 422


def test_delete_missing_profile_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "delete_profile", lambda *_: False)

    with pytest.raises(HTTPException) as exc:
        service.delete_user_weight_profile(CONNECTION, "missing", USER_ID)

    assert exc.value.status_code == 404


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(weight_profiles_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_current_active_user] = lambda: USER
    return TestClient(app)


def test_list_weight_profiles_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        service, "list_user_weight_profiles", lambda *_: [_row()]
    )

    response = _client().get("/api/v1/me/weight-profiles")

    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == PROFILE_ID


def test_get_weight_profile_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        service, "get_user_weight_profile", lambda *_a, **_kw: _row()
    )

    response = _client().get(f"/api/v1/me/weight-profiles/{PROFILE_ID}")

    assert response.status_code == 200
    assert response.json()["item"]["id"] == PROFILE_ID


def test_get_weight_profile_api_returns_404_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_profile_for_user", lambda *_: None)

    response = _client().get(f"/api/v1/me/weight-profiles/{PROFILE_ID}")

    assert response.status_code == 404


def test_create_weight_profile_api_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service, "create_user_weight_profile", lambda *_a, **_kw: _row()
    )

    response = _client().post(
        "/api/v1/me/weight-profiles",
        json={
            "name": "Balanced",
            "weights": WEIGHTS,
            "is_default": False,
        },
    )

    assert response.status_code == 201
    CONNECTION_MOCK.commit.assert_called()


def test_patch_weight_profile_api_passes_field_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_update(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return _row(name=kwargs["name"])

    monkeypatch.setattr(service, "update_user_weight_profile", fake_update)

    response = _client().patch(
        f"/api/v1/me/weight-profiles/{PROFILE_ID}",
        json={"name": "Safety first"},
    )

    assert response.status_code == 200
    assert captured["fields"] == {"name"}
    assert response.json()["item"]["name"] == "Safety first"

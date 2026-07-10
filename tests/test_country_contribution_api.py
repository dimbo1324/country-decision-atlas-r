"""Country contribution API: deny-by-default RBAC gates for contributor and curator surfaces."""

import pytest
from app.api.v1 import admin_country_contribution, country_contribution
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import capabilities as capabilities_repository
from app.services import country_contribution as service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.cache_test_helpers import FakeCacheBackend
from unittest.mock import MagicMock


CONNECTION = MagicMock()
USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)
EDITOR = CurrentUser(
    id="22222222-2222-2222-2222-222222222222",
    email="editor@example.local",
    display_name="Editor",
    role="editor",
    status="active",
)


def _client(current_user: CurrentUser | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(country_contribution.router, prefix="/api/v1")
    app.include_router(admin_country_contribution.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app)


def test_me_country_proposals_requires_auth() -> None:
    response = _client().get("/api/v1/me/country-proposals")
    assert response.status_code == 401


def test_me_country_proposals_denies_user_without_capability_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: False
    )

    response = _client(USER).get("/api/v1/me/country-proposals")

    assert response.status_code == 403
    assert (
        response.json()["detail"]["error"]["code"] == "insufficient_capability"
    )


def test_me_country_proposals_allows_user_with_capability_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: True
    )
    monkeypatch.setattr(
        service,
        "list_my_proposals",
        lambda *_a, **_kw: {"items": [], "total": 0},
    )

    response = _client(USER).get("/api/v1/me/country-proposals")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_create_proposal_denies_plain_user_role_regardless_of_editor_powers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: False
    )

    response = _client(EDITOR).post(
        "/api/v1/me/country-proposals",
        json={
            "slug": "wakanda",
            "name_en": "Wakanda",
            "name_ru": "Ваканда",
            "iso2": "WK",
            "iso3": "WKD",
            "justification": "x" * 30,
        },
    )

    assert response.status_code == 403


def test_admin_country_proposals_requires_editor_role() -> None:
    response = _client(USER).get("/api/v1/admin/country-proposals")
    assert response.status_code == 403
    assert response.json()["detail"]["error"]["code"] == "insufficient_role"


def test_admin_country_proposals_allows_editor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "list_proposals_for_curation",
        lambda *_a, **_kw: {"items": [], "total": 0},
    )

    response = _client(EDITOR).get("/api/v1/admin/country-proposals")

    assert response.status_code == 200


def test_admin_publish_requires_auth() -> None:
    response = _client().post("/api/v1/admin/country-proposals/some-id/publish")
    assert response.status_code == 401


def _create_payload() -> dict[str, object]:
    return {
        "slug": "wakanda",
        "name_en": "Wakanda",
        "name_ru": "Ваканда",
        "iso2": "WK",
        "iso3": "WKD",
        "justification": "x" * 30,
    }


def _fake_proposal(suffix: str) -> dict[str, object]:
    return {
        "id": f"11111111-1111-1111-1111-11111111111{suffix}",
        "proposer_user_id": USER.id,
        "country_id": f"22222222-2222-2222-2222-22222222222{suffix}",
        "slug": "wakanda",
        "name_en": "Wakanda",
        "name_ru": "Ваканда",
        "iso2": "WK",
        "iso3": "WKD",
        "justification": "x" * 30,
        "status": "draft",
        "curator_user_id": None,
        "readiness_snapshot": None,
        "moderated_by": None,
        "moderated_at": None,
        "moderation_reason": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "published_at": None,
        "country_is_active": False,
        "country_is_demo": False,
    }


def test_create_proposal_repeated_idempotency_key_does_not_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: True
    )
    shared_cache = FakeCacheBackend()
    monkeypatch.setattr(
        country_contribution, "get_cache_backend", lambda: shared_cache
    )
    calls: list[int] = []

    def fake_create_proposal(*_a: object, **_kw: object) -> dict[str, object]:
        calls.append(1)
        return _fake_proposal(str(len(calls)))

    monkeypatch.setattr(service, "create_proposal", fake_create_proposal)

    client = _client(USER)
    first = client.post(
        "/api/v1/me/country-proposals",
        json=_create_payload(),
        headers={"Idempotency-Key": "retry-1"},
    )
    second = client.post(
        "/api/v1/me/country-proposals",
        json=_create_payload(),
        headers={"Idempotency-Key": "retry-1"},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert len(calls) == 1


def test_create_proposal_without_idempotency_key_creates_each_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_repository, "has_active_grant", lambda *_a, **_kw: True
    )
    shared_cache = FakeCacheBackend()
    monkeypatch.setattr(
        country_contribution, "get_cache_backend", lambda: shared_cache
    )
    calls: list[int] = []

    def fake_create_proposal(*_a: object, **_kw: object) -> dict[str, object]:
        calls.append(1)
        return _fake_proposal(str(len(calls)))

    monkeypatch.setattr(service, "create_proposal", fake_create_proposal)

    client = _client(USER)
    client.post("/api/v1/me/country-proposals", json=_create_payload())
    client.post("/api/v1/me/country-proposals", json=_create_payload())

    assert len(calls) == 2


def test_admin_country_proposals_returns_422_for_invalid_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service,
        "list_proposals_for_curation",
        lambda *_a, **_kw: {"items": [], "total": 0},
    )

    response = _client(EDITOR).get(
        "/api/v1/admin/country-proposals?status=not_a_real_status"
    )

    assert response.status_code == 422


def test_admin_country_proposals_accepts_valid_status_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_list(*_a: object, **kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {"items": [], "total": 0}

    monkeypatch.setattr(service, "list_proposals_for_curation", fake_list)

    response = _client(EDITOR).get(
        "/api/v1/admin/country-proposals?status=review"
    )

    assert response.status_code == 200
    assert captured["status"] == "review"
    assert isinstance(captured["status"], str)

"""Country contribution API: deny-by-default RBAC gates for contributor and curator surfaces."""

import pytest
from app.api.v1 import admin_country_contribution, country_contribution
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import capabilities as capabilities_repository
from app.services import country_contribution as service
from fastapi import FastAPI
from fastapi.testclient import TestClient
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

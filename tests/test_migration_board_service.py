from app.core.auth import CurrentUser
from app.repositories import migration_board as migration_board_repository
from app.services import migration_board as service
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def _post(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "22222222-2222-2222-2222-222222222222",
        "user_id": "33333333-3333-3333-3333-333333333333",
        "author_display_name": "Author",
        "origin_country_id": None,
        "origin_country_slug": None,
        "origin_country_name": None,
        "destination_country_id": "44444444-4444-4444-4444-444444444444",
        "destination_country_slug": "uruguay",
        "destination_country_name": "Uruguay",
        "route_id": None,
        "route_slug": None,
        "route_title": None,
        "scenario_slug": None,
        "scenario_label": None,
        "persona_slug": None,
        "persona_label": None,
        "title": "Moving to Uruguay",
        "summary": "Looking for people preparing documents and housing research.",
        "target_city": None,
        "target_month": None,
        "timeline_window": "6_12_months",
        "budget_range": "undisclosed",
        "household_type": "solo",
        "migration_stage": "researching",
        "companion_goal": "info_exchange",
        "preferred_language": "en",
        "visibility": "public",
        "status": "published",
        "moderation_status": "approved",
        "risk_acknowledged": True,
        "legal_disclaimer_acknowledged": True,
        "contact_requests_enabled": True,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "submitted_at": None,
        "published_at": "2026-01-02T00:00:00Z",
        "archived_at": None,
        "rejected_at": None,
        "moderated_by": None,
        "moderated_at": None,
        "moderation_reason": None,
        "tags": ["housing"],
    }
    row.update(overrides)
    return row


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service, "is_feature_enabled_by_key", lambda *_: True)


def test_public_post_response_does_not_expose_private_identity() -> None:
    result = service._public_post(_post())
    assert "user_id" not in result
    assert "email" not in result
    assert "telegram_user_id" not in result
    assert result["author"] == {"display_name": "Author"}


def test_submit_rejects_pii_in_public_text() -> None:
    with pytest.raises(HTTPException) as exc_info:
        service._reject_public_pii(
            "Moving to Uruguay",
            "Contact me at person@example.com while preparing relocation.",
        )
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "pii_not_allowed"


def test_contact_request_rejects_self_contact(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        migration_board_repository,
        "get_post_by_id",
        lambda *_: _post(user_id=USER.id),
    )

    with pytest.raises(HTTPException) as exc_info:
        service.create_contact_request(
            CONNECTION,
            current_user=USER,
            post_id="22222222-2222-2222-2222-222222222222",
            message="I would like to compare document preparation timelines.",
        )

    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "self_contact_not_allowed"


def test_contact_request_rejects_blocked_relation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    monkeypatch.setattr(
        migration_board_repository, "get_post_by_id", lambda *_: _post()
    )
    monkeypatch.setattr(
        migration_board_repository, "is_user_blocked", lambda *_a, **_kw: True
    )

    with pytest.raises(HTTPException) as exc_info:
        service.create_contact_request(
            CONNECTION,
            current_user=USER,
            post_id="22222222-2222-2222-2222-222222222222",
            message="I would like to compare document preparation timelines.",
        )

    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "contact_blocked"


def test_matching_returns_reasons_without_numeric_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    source = _post(
        id="55555555-5555-5555-5555-555555555555",
        user_id=USER.id,
        route_id="66666666-6666-6666-6666-666666666666",
        scenario_slug="residence",
    )
    candidate = _post(
        route_id="66666666-6666-6666-6666-666666666666",
        scenario_slug="residence",
    )
    monkeypatch.setattr(
        migration_board_repository, "get_post_for_owner", lambda *_: source
    )
    monkeypatch.setattr(
        migration_board_repository,
        "list_potential_companion_posts",
        lambda *_a, **_kw: [candidate],
    )
    monkeypatch.setattr(service, "_track_event", lambda *_a, **_kw: None)

    result = service.list_companion_matches(
        CONNECTION,
        current_user=USER,
        post_id="55555555-5555-5555-5555-555555555555",
        limit=10,
    )

    match = result["items"][0]
    assert "same_destination" in match["match_reasons"]
    assert "same_route" in match["match_reasons"]
    assert "score" not in match

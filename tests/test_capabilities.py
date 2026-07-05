"""Capability grants: has_capability role/grant logic, grant/revoke lifecycle, conflict checks, moderation feed, and admin API wiring."""

import pytest
from app.api.v1 import (
    admin_capabilities as admin_capabilities_api,
    admin_moderation as admin_moderation_api,
)
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import auth as auth_repository, capabilities as repository
from app.services import capabilities as service, moderation_feed
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION_MOCK = MagicMock()
CONNECTION = cast(Connection[Any], CONNECTION_MOCK)
NOW = datetime(2026, 7, 5, tzinfo=UTC)
OWNER = CurrentUser(
    id="owner-id",
    email="owner@example.local",
    display_name="Owner",
    role="owner",
    status="active",
)
ADMIN = CurrentUser(
    id="admin-id",
    email="admin@example.local",
    display_name="Admin",
    role="admin",
    status="active",
)
MODERATOR = CurrentUser(
    id="mod-id",
    email="mod@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)
USER = CurrentUser(
    id="user-id",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


GRANT_ID = "11111111-1111-1111-1111-111111111111"


def _grant_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": GRANT_ID,
        "user_id": "target-id",
        "capability": "moderator.board",
        "granted_by": OWNER.id,
        "granted_at": NOW,
        "revoked_at": None,
        "note": None,
    }
    row.update(overrides)
    return row


class TestHasCapability:
    def test_owner_always_true(self) -> None:
        assert (
            service.has_capability(CONNECTION, OWNER, "author.metrics") is True
        )

    def test_admin_always_true(self) -> None:
        assert (
            service.has_capability(CONNECTION, ADMIN, "author.metrics") is True
        )

    def test_moderator_true_for_moderator_capabilities(self) -> None:
        assert (
            service.has_capability(CONNECTION, MODERATOR, "moderator.board")
            is True
        )
        assert (
            service.has_capability(CONNECTION, MODERATOR, "moderator.metrics")
            is True
        )
        assert (
            service.has_capability(CONNECTION, MODERATOR, "moderator.community")
            is True
        )

    def test_moderator_false_for_non_moderator_capability_without_grant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            repository, "has_active_grant", lambda *_a, **_kw: False
        )
        assert (
            service.has_capability(CONNECTION, MODERATOR, "author.metrics")
            is False
        )

    def test_regular_user_false_without_grant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            repository, "has_active_grant", lambda *_a, **_kw: False
        )
        assert (
            service.has_capability(CONNECTION, USER, "author.metrics") is False
        )

    def test_regular_user_true_with_active_grant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            repository, "has_active_grant", lambda *_a, **_kw: True
        )
        assert (
            service.has_capability(CONNECTION, USER, "author.metrics") is True
        )


class TestGrantCapability:
    def test_rejects_unknown_capability(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service.grant_capability(
                CONNECTION,
                current_user=OWNER,
                user_id="target-id",
                capability="not.a.capability",
                note=None,
            )
        assert exc_info.value.status_code == 422

    def test_raises_404_when_target_user_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(auth_repository, "get_user_by_id", lambda *_a: None)
        with pytest.raises(HTTPException) as exc_info:
            service.grant_capability(
                CONNECTION,
                current_user=OWNER,
                user_id="missing",
                capability="author.metrics",
                note=None,
            )
        assert exc_info.value.status_code == 404

    def test_grants_and_audits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            auth_repository,
            "get_user_by_id",
            lambda *_a: {"id": "target-id"},
        )
        monkeypatch.setattr(
            repository, "grant_capability", lambda *_a, **_kw: _grant_row()
        )
        captured: dict[str, Any] = {}
        monkeypatch.setattr(
            service, "insert_audit_event", lambda _c, **kw: captured.update(kw)
        )

        row = service.grant_capability(
            CONNECTION,
            current_user=OWNER,
            user_id="target-id",
            capability="moderator.board",
            note="trusted contributor",
        )

        assert row["capability"] == "moderator.board"
        assert captured["action"] == "granted"
        assert captured["changed_by"] == OWNER.id
        assert captured["entity_type"] == "user_capability"


class TestRevokeCapability:
    def test_raises_404_when_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            repository, "revoke_capability_by_id", lambda *_a: None
        )
        with pytest.raises(HTTPException) as exc_info:
            service.revoke_capability(
                CONNECTION, current_user=OWNER, capability_id="missing"
            )
        assert exc_info.value.status_code == 404

    def test_revokes_and_audits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            repository,
            "revoke_capability_by_id",
            lambda *_a: _grant_row(revoked_at=NOW),
        )
        captured: dict[str, Any] = {}
        monkeypatch.setattr(
            service, "insert_audit_event", lambda _c, **kw: captured.update(kw)
        )

        row = service.revoke_capability(
            CONNECTION, current_user=OWNER, capability_id="grant-1"
        )

        assert row["revoked_at"] == NOW
        assert captured["action"] == "revoked"
        assert captured["changed_by"] == OWNER.id


class TestListCapabilities:
    def test_returns_items_and_total(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            dict(_grant_row(), total_count=2),
            dict(_grant_row(id="grant-2"), total_count=2),
        ]
        monkeypatch.setattr(
            repository, "list_capabilities", lambda *_a, **_kw: rows
        )

        result = service.list_capabilities(
            CONNECTION,
            user_id=None,
            capability=None,
            active_only=True,
            limit=50,
            offset=0,
        )

        assert result["total"] == 2
        assert len(result["items"]) == 2

    def test_empty_list_has_zero_total(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            repository, "list_capabilities", lambda *_a, **_kw: []
        )

        result = service.list_capabilities(
            CONNECTION,
            user_id=None,
            capability=None,
            active_only=True,
            limit=50,
            offset=0,
        )

        assert result["total"] == 0
        assert result["items"] == []


class TestConflictOfInterest:
    def test_raises_when_current_user_is_involved(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            service.assert_no_moderation_conflict(USER, [USER.id, "other-id"])
        assert exc_info.value.status_code == 403
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "moderation_conflict_of_interest"

    def test_allows_when_not_involved(self) -> None:
        service.assert_no_moderation_conflict(USER, ["other-id", None])

    def test_ignores_none_entries(self) -> None:
        service.assert_no_moderation_conflict(USER, [None, None])


def _client(current_user: CurrentUser | None) -> TestClient:
    app = FastAPI()
    app.include_router(admin_capabilities_api.router, prefix="/api/v1")
    app.include_router(admin_moderation_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    if current_user is not None:
        app.dependency_overrides[get_current_active_user] = lambda: current_user
    return TestClient(app, raise_server_exceptions=False)


class TestAdminCapabilitiesApi:
    def test_list_without_auth_returns_401(self) -> None:
        response = _client(None).get("/api/v1/admin/capabilities")
        assert response.status_code == 401

    def test_list_with_regular_user_returns_403(self) -> None:
        response = _client(USER).get(
            "/api/v1/admin/capabilities",
            headers={"Authorization": "Bearer user-token"},
        )
        assert response.status_code == 403

    def test_list_with_moderator_returns_403(self) -> None:
        response = _client(MODERATOR).get(
            "/api/v1/admin/capabilities",
            headers={"Authorization": "Bearer mod-token"},
        )
        assert response.status_code == 403

    def test_list_with_owner_returns_200(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            service,
            "list_capabilities",
            lambda *_a, **_kw: {"items": [_grant_row()], "total": 1},
        )
        response = _client(OWNER).get(
            "/api/v1/admin/capabilities",
            headers={"Authorization": "Bearer owner-token"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_grant_endpoint_commits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            service, "grant_capability", lambda *_a, **_kw: _grant_row()
        )
        response = _client(OWNER).post(
            "/api/v1/admin/capabilities",
            json={"user_id": "target-id", "capability": "moderator.board"},
            headers={"Authorization": "Bearer owner-token"},
        )
        assert response.status_code == 201
        CONNECTION_MOCK.commit.assert_called()

    def test_revoke_endpoint_returns_204(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            service,
            "revoke_capability",
            lambda *_a, **_kw: _grant_row(revoked_at=NOW),
        )
        response = _client(OWNER).delete(
            "/api/v1/admin/capabilities/grant-1",
            headers={"Authorization": "Bearer owner-token"},
        )
        assert response.status_code == 204


class TestAdminModerationApi:
    def test_list_without_auth_returns_401(self) -> None:
        response = _client(None).get("/api/v1/admin/moderation/actions")
        assert response.status_code == 401

    def test_list_with_regular_user_returns_403(self) -> None:
        response = _client(USER).get(
            "/api/v1/admin/moderation/actions",
            headers={"Authorization": "Bearer user-token"},
        )
        assert response.status_code == 403

    def test_list_with_moderator_returns_403(self) -> None:
        response = _client(MODERATOR).get(
            "/api/v1/admin/moderation/actions",
            headers={"Authorization": "Bearer mod-token"},
        )
        assert response.status_code == 403

    def test_list_with_owner_returns_200(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            moderation_feed,
            "list_moderation_actions",
            lambda *_a, **_kw: {"items": [], "total": 0, "anomalies": []},
        )
        response = _client(OWNER).get(
            "/api/v1/admin/moderation/actions",
            headers={"Authorization": "Bearer owner-token"},
        )
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0, "anomalies": []}


class TestModerationFeedAnomalies:
    def _row(self, index: int, action: str) -> dict[str, Any]:
        return {
            "id": f"event-{index}",
            "entity_type": "migration_board",
            "entity_id": "post-1",
            "action": action,
            "changed_by": "mod-1",
            "changed_at": NOW,
            "changes": {},
        }

    def test_flags_moderator_with_high_reject_rate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            self._row(i, "rejected" if i < 4 else "published") for i in range(6)
        ]
        monkeypatch.setattr(
            moderation_feed, "list_audit_events", lambda *_a, **_kw: rows
        )

        result = moderation_feed.list_moderation_actions(
            CONNECTION,
            entity_type=None,
            action=None,
            changed_by=None,
            limit=50,
            offset=0,
        )

        assert result["total"] == 6
        assert len(result["anomalies"]) == 1
        assert result["anomalies"][0]["changed_by"] == "mod-1"
        assert result["anomalies"][0]["reject_rate"] == pytest.approx(
            4 / 6, rel=1e-2
        )

    def test_does_not_flag_moderator_below_minimum_actions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [self._row(i, "rejected") for i in range(3)]
        monkeypatch.setattr(
            moderation_feed, "list_audit_events", lambda *_a, **_kw: rows
        )

        result = moderation_feed.list_moderation_actions(
            CONNECTION,
            entity_type=None,
            action=None,
            changed_by=None,
            limit=50,
            offset=0,
        )

        assert result["anomalies"] == []

    def test_does_not_flag_moderator_with_low_reject_rate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            self._row(i, "published" if i < 4 else "rejected") for i in range(6)
        ]
        monkeypatch.setattr(
            moderation_feed, "list_audit_events", lambda *_a, **_kw: rows
        )

        result = moderation_feed.list_moderation_actions(
            CONNECTION,
            entity_type=None,
            action=None,
            changed_by=None,
            limit=50,
            offset=0,
        )

        assert result["anomalies"] == []

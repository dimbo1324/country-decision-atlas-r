"""Community threads service: ownership gating, lifecycle rules, rate limits, and moderator report-gated access."""

import pytest
from app.core.auth import CurrentUser
from app.repositories import migration_board as repository
from app.services import (
    feature_flags as feature_flags_service,
    migration_board as service,
)
from app.services.migration_board import helpers as migration_board_helpers
from fastapi import HTTPException
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
FROM_USER_ID = "11111111-1111-1111-1111-111111111111"
TO_USER_ID = "22222222-2222-2222-2222-222222222222"
STRANGER_ID = "99999999-9999-9999-9999-999999999999"
THREAD_ID = "33333333-3333-3333-3333-333333333333"
CONTACT_REQUEST_ID = "44444444-4444-4444-4444-444444444444"

FROM_USER = CurrentUser(
    id=FROM_USER_ID,
    email="requester@example.local",
    display_name="Requester",
    role="user",
    status="active",
)
TO_USER = CurrentUser(
    id=TO_USER_ID,
    email="recipient@example.local",
    display_name="Recipient",
    role="user",
    status="active",
)
STRANGER = CurrentUser(
    id=STRANGER_ID,
    email="stranger@example.local",
    display_name="Stranger",
    role="user",
    status="active",
)
MODERATOR = CurrentUser(
    id="55555555-5555-5555-5555-555555555555",
    email="mod@example.local",
    display_name="Moderator",
    role="moderator",
    status="active",
)


def _thread_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": THREAD_ID,
        "contact_request_id": CONTACT_REQUEST_ID,
        "status": "open",
        "closed_by_user_id": None,
        "closed_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "post_id": "66666666-6666-6666-6666-666666666666",
        "post_title": "Moving to Uruguay",
        "from_user_id": FROM_USER_ID,
        "from_user_display_name": "Requester",
        "to_user_id": TO_USER_ID,
        "to_user_display_name": "Recipient",
    }
    row.update(overrides)
    return row


def _message_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "77777777-7777-7777-7777-777777777777",
        "thread_id": THREAD_ID,
        "sender_user_id": FROM_USER_ID,
        "sender_display_name": "Requester",
        "body": "Hello there",
        "created_at": "2026-01-01T00:00:00Z",
    }
    row.update(overrides)
    return row


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_: True
    )


def _assert_error(exc: pytest.ExceptionInfo[HTTPException], code: str) -> None:
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == code


class TestListMyThreads:
    def test_wraps_rows_with_counterpart_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "list_my_threads", lambda *_a, **_kw: [_thread_row()]
        )

        result = service.list_my_threads(CONNECTION, FROM_USER)

        assert result["total"] == 1
        assert result["items"][0]["counterpart_display_name"] == "Recipient"

    def test_counterpart_name_flips_for_recipient(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "list_my_threads", lambda *_a, **_kw: [_thread_row()]
        )

        result = service.list_my_threads(CONNECTION, TO_USER)

        assert result["items"][0]["counterpart_display_name"] == "Requester"


class TestListThreadMessages:
    def test_rejects_when_current_user_not_a_party(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.list_thread_messages(
                CONNECTION,
                current_user=STRANGER,
                thread_id=THREAD_ID,
                after=None,
                limit=50,
            )
        assert exc_info.value.status_code == 404
        _assert_error(exc_info, "thread_not_found")

    def test_rejects_when_thread_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.list_thread_messages(
                CONNECTION,
                current_user=FROM_USER,
                thread_id=THREAD_ID,
                after=None,
                limit=50,
            )
        assert exc_info.value.status_code == 404

    def test_returns_messages_for_owning_party(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        captured: dict[str, Any] = {}

        def fake_list_messages(
            _conn: Any, **kwargs: Any
        ) -> list[dict[str, Any]]:
            captured.update(kwargs)
            return [_message_row()]

        monkeypatch.setattr(repository, "list_messages", fake_list_messages)

        result = service.list_thread_messages(
            CONNECTION,
            current_user=TO_USER,
            thread_id=THREAD_ID,
            after=None,
            limit=25,
        )

        assert result["total"] == 1
        assert captured["thread_id"] == THREAD_ID
        assert captured["limit"] == 25


class TestSendThreadMessage:
    def test_rejects_when_thread_not_open(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_thread_by_id",
            lambda *_a, **_kw: _thread_row(status="closed"),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.send_thread_message(
                CONNECTION,
                current_user=FROM_USER,
                thread_id=THREAD_ID,
                body="Are you still there?",
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "thread_not_open")

    def test_rejects_empty_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.send_thread_message(
                CONNECTION,
                current_user=FROM_USER,
                thread_id=THREAD_ID,
                body="   ",
            )
        assert exc_info.value.status_code == 422
        _assert_error(exc_info, "empty_message_body")

    def test_rejects_when_daily_limit_reached(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            migration_board_helpers,
            "max_thread_messages_per_day",
            lambda *_: 50,
        )
        monkeypatch.setattr(
            repository, "count_messages_created_since", lambda *_a, **_kw: 50
        )

        with pytest.raises(HTTPException) as exc_info:
            service.send_thread_message(
                CONNECTION,
                current_user=FROM_USER,
                thread_id=THREAD_ID,
                body="One more message",
            )
        assert exc_info.value.status_code == 429
        _assert_error(exc_info, "thread_message_limit_exceeded")

    def test_sends_message_and_audits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            migration_board_helpers,
            "max_thread_messages_per_day",
            lambda *_: 50,
        )
        monkeypatch.setattr(
            repository, "count_messages_created_since", lambda *_a, **_kw: 0
        )
        monkeypatch.setattr(
            repository,
            "create_message",
            lambda *_a, **kwargs: _message_row(**kwargs),
        )
        audit_calls: list[tuple[Any, ...]] = []
        monkeypatch.setattr(
            migration_board_helpers,
            "_audit",
            lambda *args: audit_calls.append(args),
        )

        result = service.send_thread_message(
            CONNECTION,
            current_user=FROM_USER,
            thread_id=THREAD_ID,
            body="Hello there",
        )

        assert result["body"] == "Hello there"
        assert len(audit_calls) == 1
        assert audit_calls[0][2] == "thread_message_sent"


class TestCloseThread:
    def test_rejects_when_current_user_not_a_party(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )

        with pytest.raises(HTTPException) as exc_info:
            service.close_thread(
                CONNECTION, current_user=STRANGER, thread_id=THREAD_ID
            )
        assert exc_info.value.status_code == 404

    def test_rejects_when_already_closed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(repository, "close_thread", lambda *_a, **_kw: None)

        with pytest.raises(HTTPException) as exc_info:
            service.close_thread(
                CONNECTION, current_user=FROM_USER, thread_id=THREAD_ID
            )
        assert exc_info.value.status_code == 409
        _assert_error(exc_info, "thread_not_open")

    def test_closes_thread_and_audits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            repository,
            "close_thread",
            lambda *_a, **_kw: _thread_row(
                status="closed",
                closed_by_user_id=TO_USER_ID,
                closed_at="2026-01-02T00:00:00Z",
            ),
        )
        audit_calls: list[tuple[Any, ...]] = []
        monkeypatch.setattr(
            migration_board_helpers,
            "_audit",
            lambda *args: audit_calls.append(args),
        )

        result = service.close_thread(
            CONNECTION, current_user=TO_USER, thread_id=THREAD_ID
        )

        assert result["status"] == "closed"
        assert len(audit_calls) == 1
        assert audit_calls[0][2] == "thread_closed"


class TestModeratorAccess:
    def test_rejects_when_thread_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_thread_messages_for_moderation(
                CONNECTION,
                current_user=MODERATOR,
                thread_id=THREAD_ID,
                report_id="report-1",
            )
        assert exc_info.value.status_code == 404
        _assert_error(exc_info, "thread_not_found")

    def test_rejects_when_no_matching_report(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            repository,
            "get_report_by_id",
            lambda *_a, **_kw: {
                "id": "report-1",
                "contact_request_id": "other-contact-request",
            },
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_thread_messages_for_moderation(
                CONNECTION,
                current_user=MODERATOR,
                thread_id=THREAD_ID,
                report_id="report-1",
            )
        assert exc_info.value.status_code == 403
        _assert_error(exc_info, "report_required_for_thread_access")

    def test_rejects_when_report_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            repository, "get_report_by_id", lambda *_a, **_kw: None
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_thread_messages_for_moderation(
                CONNECTION,
                current_user=MODERATOR,
                thread_id=THREAD_ID,
                report_id="missing-report",
            )
        _assert_error(exc_info, "report_required_for_thread_access")

    def test_rejects_moderator_who_is_a_party(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            repository,
            "get_report_by_id",
            lambda *_a, **_kw: {
                "id": "report-1",
                "contact_request_id": CONTACT_REQUEST_ID,
            },
        )
        involved_moderator = CurrentUser(
            id=FROM_USER_ID,
            email="dual@example.local",
            display_name="Dual",
            role="moderator",
            status="active",
        )

        with pytest.raises(HTTPException) as exc_info:
            service.get_thread_messages_for_moderation(
                CONNECTION,
                current_user=involved_moderator,
                thread_id=THREAD_ID,
                report_id="report-1",
            )
        assert exc_info.value.status_code == 403
        _assert_error(exc_info, "moderation_conflict_of_interest")

    def test_grants_access_and_audits_every_call(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository, "get_thread_by_id", lambda *_a, **_kw: _thread_row()
        )
        monkeypatch.setattr(
            repository,
            "get_report_by_id",
            lambda *_a, **_kw: {
                "id": "report-1",
                "contact_request_id": CONTACT_REQUEST_ID,
            },
        )
        monkeypatch.setattr(
            repository, "list_messages", lambda *_a, **_kw: [_message_row()]
        )
        audit_calls: list[tuple[Any, ...]] = []
        monkeypatch.setattr(
            migration_board_helpers,
            "_audit",
            lambda *args: audit_calls.append(args),
        )

        service.get_thread_messages_for_moderation(
            CONNECTION,
            current_user=MODERATOR,
            thread_id=THREAD_ID,
            report_id="report-1",
        )
        service.get_thread_messages_for_moderation(
            CONNECTION,
            current_user=MODERATOR,
            thread_id=THREAD_ID,
            report_id="report-1",
        )

        assert len(audit_calls) == 2
        assert all(
            call[2] == "thread_viewed_by_moderator" for call in audit_calls
        )


class TestContactAndBlockHooks:
    def test_accept_contact_request_creates_thread(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(
            repository,
            "get_contact_request_by_id",
            lambda *_a, **_kw: {
                "id": "req-1",
                "from_user_id": STRANGER_ID,
                "to_user_id": FROM_USER_ID,
            },
        )
        monkeypatch.setattr(
            repository,
            "update_contact_request_status",
            lambda *_a, **_kw: {
                "id": "req-1",
                "post_id": "66666666-6666-6666-6666-666666666666",
                "post_title": "Moving to Uruguay",
                "from_user_display_name": "Stranger",
                "to_user_display_name": "Requester",
                "message": "hi",
                "status": "accepted",
                "created_at": "2026-01-01T00:00:00Z",
                "responded_at": "2026-01-02T00:00:00Z",
                "cancelled_at": None,
                "response_note": None,
            },
        )
        monkeypatch.setattr(
            migration_board_helpers, "_audit", lambda *_a, **_kw: None
        )
        created_for: list[str] = []

        def fake_create_thread(_conn: Any, request_id: str) -> dict[str, Any]:
            created_for.append(request_id)
            return _thread_row()

        monkeypatch.setattr(
            repository, "create_thread_for_contact_request", fake_create_thread
        )

        service.accept_contact_request(
            CONNECTION,
            current_user=FROM_USER,
            request_id="req-1",
            response_note=None,
        )

        assert created_for == ["req-1"]

    def test_block_user_freezes_open_threads(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _enable_features(monkeypatch)
        monkeypatch.setattr(repository, "user_exists", lambda *_a, **_kw: True)
        monkeypatch.setattr(
            repository,
            "block_user",
            lambda *_a, **_kw: {
                "id": "block-1",
                "blocked_user_id": STRANGER_ID,
                "blocked_user_display_name": "Stranger",
                "created_at": "2026-01-01T00:00:00Z",
                "reason": None,
            },
        )
        monkeypatch.setattr(
            migration_board_helpers, "_audit", lambda *_a, **_kw: None
        )
        freeze_calls: list[dict[str, Any]] = []

        def fake_freeze(_conn: Any, **kwargs: Any) -> int:
            freeze_calls.append(kwargs)
            return 1

        monkeypatch.setattr(
            repository, "freeze_threads_between_users", fake_freeze
        )

        service.block_user(
            CONNECTION,
            current_user=FROM_USER,
            blocked_user_id=STRANGER_ID,
            reason=None,
        )

        assert freeze_calls == [
            {"user_a_id": FROM_USER_ID, "user_b_id": STRANGER_ID}
        ]

"""Advisory-lock wiring for migration board daily-limit count-then-insert races (P1-2, AE-4).

pg_advisory_xact_lock closes the TOCTOU window between counting today's rows
and inserting a new one. These tests can't prove the lock actually serializes
concurrent Postgres transactions (this suite mocks the repository layer
entirely, per the pre-existing gap tracked as AE-8/P2-7); they verify instead
that the lock is acquired, with the correct per-user+scope key, before the
count-then-insert sequence in every call site the audit finding named.
"""

import pytest
from app.core.auth import CurrentUser
from app.repositories import migration_board as repository
from app.schemas.migration_board import CreateMigrationBoardPostRequest
from app.services import (
    feature_flags as feature_flags_service,
    migration_board as service,
)
from app.services.migration_board import helpers, threads as threads_service
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


USER = CurrentUser(
    id="11111111-1111-1111-1111-111111111111",
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def _enable_features(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service, "is_feature_enabled_by_key", lambda *_: True
    )


def _tracking_connection(calls: list[str]) -> Any:
    conn = MagicMock()
    conn.transaction.return_value.__enter__ = lambda s: s
    conn.transaction.return_value.__exit__ = MagicMock(return_value=False)

    def _execute(sql: str, *_a: Any, **_kw: Any) -> Any:
        if "pg_advisory_xact_lock" in sql:
            calls.append("lock")
        return MagicMock()

    conn.execute.side_effect = _execute
    return cast(Connection[Any], conn)


def test_with_daily_limit_lock_issues_advisory_lock_on_scoped_key() -> None:
    conn = MagicMock()
    helpers.with_daily_limit_lock(conn, "user-1", "thread_message")
    sql, params = conn.execute.call_args[0]
    assert "pg_advisory_xact_lock" in sql
    assert params == ("thread_message:user-1",)


def test_send_thread_message_acquires_lock_before_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    calls: list[str] = []
    conn = _tracking_connection(calls)
    monkeypatch.setattr(
        threads_service,
        "_get_owned_thread_or_404",
        lambda *_a, **_kw: {"status": "open"},
    )
    monkeypatch.setattr(helpers, "max_thread_messages_per_day", lambda *_a: 5)

    def _count(*_a: Any, **_kw: Any) -> int:
        calls.append("count")
        return 0

    def _create(*_a: Any, **_kw: Any) -> dict[str, Any]:
        calls.append("create")
        return {
            "id": "m-1",
            "thread_id": "t-1",
            "sender_user_id": USER.id,
            "body": "hi",
            "created_at": "2026-01-01T00:00:00Z",
        }

    monkeypatch.setattr(repository, "count_messages_created_since", _count)
    monkeypatch.setattr(repository, "create_message", _create)
    monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)

    service.send_thread_message(
        conn, current_user=USER, thread_id="t-1", body="hi"
    )
    assert calls == ["lock", "count", "create"]


def test_create_user_post_acquires_lock_before_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    calls: list[str] = []
    conn = _tracking_connection(calls)
    monkeypatch.setattr(helpers, "max_active_posts", lambda *_a: 5)

    def _count(*_a: Any, **_kw: Any) -> int:
        calls.append("count")
        return 0

    def _create(*_a: Any, **_kw: Any) -> dict[str, Any]:
        calls.append("create")
        return {"id": "p-1"}

    monkeypatch.setattr(repository, "count_user_active_posts", _count)
    monkeypatch.setattr(
        repository,
        "get_country_by_slug",
        lambda *_a, **_kw: {"id": "44444444-4444-4444-4444-444444444444"},
    )
    monkeypatch.setattr(repository, "create_post", _create)
    monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_track_event", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_my_post", lambda row: row)

    payload = CreateMigrationBoardPostRequest(
        destination_country_slug="uruguay",
        title="Moving",
        summary="Looking for people preparing documents.",
        timeline_window="6_12_months",
        budget_range="undisclosed",
        household_type="solo",
        migration_stage="researching",
        companion_goal="info_exchange",
        preferred_language="en",
        visibility="public",
        risk_acknowledged=True,
        legal_disclaimer_acknowledged=True,
        contact_requests_enabled=True,
        tags=[],
    )
    service.create_user_post(conn, current_user=USER, payload=payload)
    assert calls == ["lock", "count", "create"]


def test_create_contact_request_acquires_lock_before_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    calls: list[str] = []
    conn = _tracking_connection(calls)
    monkeypatch.setattr(
        repository,
        "get_post_by_id",
        lambda *_a: {
            "id": "post-1",
            "user_id": "other-user",
            "status": "published",
            "moderation_status": "approved",
            "visibility": "public",
            "contact_requests_enabled": True,
        },
    )
    monkeypatch.setattr(repository, "is_user_blocked", lambda *_a, **_kw: False)
    monkeypatch.setattr(
        repository, "pending_contact_request_exists", lambda *_a, **_kw: False
    )
    monkeypatch.setattr(helpers, "max_contact_requests_per_day", lambda *_a: 5)

    def _count(*_a: Any, **_kw: Any) -> int:
        calls.append("count")
        return 0

    def _create(*_a: Any, **_kw: Any) -> dict[str, Any]:
        calls.append("create")
        return {"id": "r-1"}

    monkeypatch.setattr(
        repository, "count_contact_requests_created_since", _count
    )
    monkeypatch.setattr(repository, "create_contact_request", _create)
    monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_track_event", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_contact_request", lambda row: row)

    service.create_contact_request(
        conn, current_user=USER, post_id="post-1", message="hi"
    )
    assert calls == ["lock", "count", "create"]


def test_report_post_acquires_lock_before_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_features(monkeypatch)
    calls: list[str] = []
    conn = _tracking_connection(calls)
    monkeypatch.setattr(
        repository, "get_post_by_id", lambda *_a: {"id": "post-1"}
    )
    monkeypatch.setattr(
        repository, "existing_pending_report_exists", lambda *_a, **_kw: False
    )
    monkeypatch.setattr(helpers, "max_reports_per_day", lambda *_a: 5)

    def _count(*_a: Any, **_kw: Any) -> int:
        calls.append("count")
        return 0

    def _create(*_a: Any, **_kw: Any) -> dict[str, Any]:
        calls.append("create")
        return {"id": "rep-1"}

    monkeypatch.setattr(repository, "count_reports_created_today", _count)
    monkeypatch.setattr(repository, "create_report", _create)
    monkeypatch.setattr(helpers, "_audit", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_track_event", lambda *_a, **_kw: None)
    monkeypatch.setattr(helpers, "_report", lambda row: row)

    service.report_post(
        conn,
        current_user=USER,
        post_id="post-1",
        reason="spam",
        details=None,
    )
    assert calls == ["lock", "count", "create"]

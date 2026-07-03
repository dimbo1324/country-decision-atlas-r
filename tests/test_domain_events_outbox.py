"""Domain events outbox: row creation, JSON-compatible payloads, and duplicate-key idempotency."""

from app.repositories import domain_events as repo
from psycopg import Connection
from typing import Any, cast
from uuid import uuid4


CONNECTION = cast(Connection[Any], object())

AGGREGATE_ID = uuid4()
COUNTRY = "uruguay"
EVENT_KEY = "legal_signal:test-id:published"
EVENT_TYPE = "legal_signal.published"
AGGREGATE_TYPE = "legal_signal"
PAYLOAD: dict[str, Any] = {"signal_id": str(AGGREGATE_ID), "country_slug": COUNTRY}

FULL_ROW: dict[str, Any] = {
    "id": uuid4(),
    "event_key": EVENT_KEY,
    "event_type": EVENT_TYPE,
    "aggregate_type": AGGREGATE_TYPE,
    "aggregate_id": AGGREGATE_ID,
    "country_slug": COUNTRY,
    "payload": PAYLOAD,
    "status": "pending",
    "notifiable": True,
    "created_at": "2026-01-01T00:00:00+00:00",
    "relayed_at": None,
    "attempts": 0,
    "last_error": None,
}


def test_insert_domain_event_creates_row(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: FULL_ROW)
    result = repo.insert_domain_event(
        CONNECTION,
        event_key=EVENT_KEY,
        event_type=EVENT_TYPE,
        aggregate_type=AGGREGATE_TYPE,
        aggregate_id=AGGREGATE_ID,
        country_slug=COUNTRY,
        payload=PAYLOAD,
    )
    assert result is not None
    assert result["event_key"] == EVENT_KEY
    assert result["status"] == "pending"


def test_insert_domain_event_returns_json_compatible_payload(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: FULL_ROW)
    result = repo.insert_domain_event(
        CONNECTION,
        event_key=EVENT_KEY,
        event_type=EVENT_TYPE,
        aggregate_type=AGGREGATE_TYPE,
        aggregate_id=AGGREGATE_ID,
        country_slug=COUNTRY,
        payload=PAYLOAD,
    )
    assert result is not None
    assert isinstance(result["payload"], dict)


def test_insert_domain_event_duplicate_returns_none(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: None)
    result = repo.insert_domain_event(
        CONNECTION,
        event_key=EVENT_KEY,
        event_type=EVENT_TYPE,
        aggregate_type=AGGREGATE_TYPE,
        aggregate_id=AGGREGATE_ID,
        country_slug=COUNTRY,
        payload=PAYLOAD,
    )
    assert result is None


def test_duplicate_event_key_does_not_increase_count(monkeypatch: Any) -> None:
    call_count = {"n": 0}

    def fake_fetch_one(*_args: Any) -> dict[str, Any] | None:
        call_count["n"] += 1
        return None

    monkeypatch.setattr(repo, "fetch_one", fake_fetch_one)
    repo.insert_domain_event(
        CONNECTION,
        event_key=EVENT_KEY,
        event_type=EVENT_TYPE,
        aggregate_type=AGGREGATE_TYPE,
        aggregate_id=AGGREGATE_ID,
        country_slug=COUNTRY,
        payload=PAYLOAD,
    )
    assert call_count["n"] == 1


def test_count_domain_events(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: {"cnt": 5})
    assert repo.count_domain_events(CONNECTION) == 5


def test_count_domain_events_none_row(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: None)
    assert repo.count_domain_events(CONNECTION) == 0


def test_count_pending_notifiable_events(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: {"cnt": 3})
    assert repo.count_pending_notifiable_events(CONNECTION) == 3


def test_count_pending_notifiable_events_none_row(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: None)
    assert repo.count_pending_notifiable_events(CONNECTION) == 0


def test_list_pending_domain_events_returns_only_pending_notifiable(
    monkeypatch: Any,
) -> None:
    rows = [FULL_ROW]
    monkeypatch.setattr(repo, "fetch_all", lambda *_: rows)
    result = repo.list_pending_domain_events(CONNECTION, limit=10)
    assert len(result) == 1
    assert result[0]["status"] == "pending"
    assert result[0]["notifiable"] is True


def test_list_pending_domain_events_empty(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [])
    result = repo.list_pending_domain_events(CONNECTION, limit=10)
    assert result == []


def test_list_pending_domain_events_ordered_by_created_at(monkeypatch: Any) -> None:
    earlier = {**FULL_ROW, "id": uuid4(), "created_at": "2026-01-01T00:00:00+00:00"}
    later = {**FULL_ROW, "id": uuid4(), "created_at": "2026-06-01T00:00:00+00:00"}
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [earlier, later])
    result = repo.list_pending_domain_events(CONNECTION, limit=10)
    assert result[0]["created_at"] < result[1]["created_at"]


def test_mark_domain_event_relayed_changes_status(monkeypatch: Any) -> None:
    relayed_row = {
        **FULL_ROW,
        "status": "relayed",
        "relayed_at": "2026-06-24T12:00:00+00:00",
    }
    monkeypatch.setattr(repo, "fetch_one", lambda *_: relayed_row)
    event_id = uuid4()
    result = repo.mark_domain_event_relayed(CONNECTION, event_id)
    assert result is not None
    assert result["status"] == "relayed"


def test_mark_domain_event_relayed_sets_relayed_at(monkeypatch: Any) -> None:
    relayed_row = {
        **FULL_ROW,
        "status": "relayed",
        "relayed_at": "2026-06-24T12:00:00+00:00",
    }
    monkeypatch.setattr(repo, "fetch_one", lambda *_: relayed_row)
    result = repo.mark_domain_event_relayed(CONNECTION, uuid4())
    assert result is not None
    assert result["relayed_at"] is not None


def test_mark_domain_event_failed_changes_status(monkeypatch: Any) -> None:
    failed_row = {
        **FULL_ROW,
        "status": "failed",
        "attempts": 1,
        "last_error": "timeout",
    }
    monkeypatch.setattr(repo, "fetch_one", lambda *_: failed_row)
    result = repo.mark_domain_event_failed(CONNECTION, uuid4(), "timeout")
    assert result is not None
    assert result["status"] == "failed"


def test_mark_domain_event_failed_increments_attempts(monkeypatch: Any) -> None:
    failed_row = {**FULL_ROW, "status": "failed", "attempts": 2, "last_error": "err"}
    monkeypatch.setattr(repo, "fetch_one", lambda *_: failed_row)
    result = repo.mark_domain_event_failed(CONNECTION, uuid4(), "err")
    assert result is not None
    assert result["attempts"] == 2


def test_mark_domain_event_failed_writes_last_error(monkeypatch: Any) -> None:
    failed_row = {
        **FULL_ROW,
        "status": "failed",
        "attempts": 1,
        "last_error": "connection refused",
    }
    monkeypatch.setattr(repo, "fetch_one", lambda *_: failed_row)
    result = repo.mark_domain_event_failed(CONNECTION, uuid4(), "connection refused")
    assert result is not None
    assert result["last_error"] == "connection refused"


def test_mark_domain_event_skipped_changes_status(monkeypatch: Any) -> None:
    skipped_row = {**FULL_ROW, "status": "skipped"}
    monkeypatch.setattr(repo, "fetch_one", lambda *_: skipped_row)
    result = repo.mark_domain_event_skipped(CONNECTION, uuid4())
    assert result is not None
    assert result["status"] == "skipped"


def test_notifiable_false_not_counted_by_pending(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: {"cnt": 0})
    assert repo.count_pending_notifiable_events(CONNECTION) == 0


def test_notifiable_false_not_returned_by_list_pending(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [])
    result = repo.list_pending_domain_events(CONNECTION, limit=10)
    assert all(r["notifiable"] for r in result)

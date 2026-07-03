"""Audit-event repository: row creation, change tracking, and action/entity preservation."""

from app.repositories import audit as audit_repo
from psycopg import Connection
from typing import Any, cast
from uuid import uuid4


CONNECTION = cast(Connection[Any], object())

ENTITY_ID = uuid4()
ENTITY_TYPE = "legal_signal"
ACTION = "published"
CHANGED_BY = "admin"
CHANGES: dict[str, Any] = {"status": {"old": "review", "new": "published"}}

AUDIT_ROW: dict[str, Any] = {
    "id": uuid4(),
    "entity_type": ENTITY_TYPE,
    "entity_id": ENTITY_ID,
    "action": ACTION,
    "changed_by": CHANGED_BY,
    "changed_at": "2026-06-24T12:00:00+00:00",
    "changes": CHANGES,
}


def test_insert_audit_event_creates_row(monkeypatch: Any) -> None:
    monkeypatch.setattr(audit_repo, "execute_one", lambda *_: AUDIT_ROW)
    result = audit_repo.insert_audit_event(
        CONNECTION,
        entity_type=ENTITY_TYPE,
        entity_id=ENTITY_ID,
        action=ACTION,
        changed_by=CHANGED_BY,
        changes=CHANGES,
    )
    assert result is not None
    assert result["entity_type"] == ENTITY_TYPE


def test_insert_audit_event_changes_stored_as_dict(monkeypatch: Any) -> None:
    monkeypatch.setattr(audit_repo, "execute_one", lambda *_: AUDIT_ROW)
    result = audit_repo.insert_audit_event(
        CONNECTION,
        entity_type=ENTITY_TYPE,
        entity_id=ENTITY_ID,
        action=ACTION,
        changed_by=CHANGED_BY,
        changes=CHANGES,
    )
    assert isinstance(result["changes"], dict)


def test_insert_audit_event_action_preserved(monkeypatch: Any) -> None:
    monkeypatch.setattr(audit_repo, "execute_one", lambda *_: AUDIT_ROW)
    result = audit_repo.insert_audit_event(
        CONNECTION,
        entity_type=ENTITY_TYPE,
        entity_id=ENTITY_ID,
        action=ACTION,
        changed_by=CHANGED_BY,
        changes=CHANGES,
    )
    assert result["action"] == ACTION


def test_insert_audit_event_entity_type_and_id_preserved(monkeypatch: Any) -> None:
    monkeypatch.setattr(audit_repo, "execute_one", lambda *_: AUDIT_ROW)
    result = audit_repo.insert_audit_event(
        CONNECTION,
        entity_type=ENTITY_TYPE,
        entity_id=ENTITY_ID,
        action=ACTION,
        changed_by=CHANGED_BY,
        changes=CHANGES,
    )
    assert result["entity_type"] == ENTITY_TYPE
    assert result["entity_id"] == ENTITY_ID


def test_insert_audit_event_changed_by_preserved(monkeypatch: Any) -> None:
    monkeypatch.setattr(audit_repo, "execute_one", lambda *_: AUDIT_ROW)
    result = audit_repo.insert_audit_event(
        CONNECTION,
        entity_type=ENTITY_TYPE,
        entity_id=ENTITY_ID,
        action=ACTION,
        changed_by=CHANGED_BY,
        changes=CHANGES,
    )
    assert result["changed_by"] == CHANGED_BY

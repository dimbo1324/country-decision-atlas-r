"""Data-quality checks for the 'what changed' feed: unknown or non-published references."""

from app.repositories import data_quality as dq_repository
from app.schemas.what_changed import WhatChangedItem
from app.services.data_quality.what_changed_checks import (
    _append_what_changed_checks,
)
from datetime import UTC, datetime
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _install_clean(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_domain_events_with_unknown_country", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository,
        "list_domain_events_referencing_non_published_content",
        lambda *_: [],
    )


def test_clean_state_produces_no_issues(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)

    issues: list[Any] = []
    checks: list[Any] = []
    _append_what_changed_checks(CONNECTION, issues, checks)

    assert issues == []
    assert all(check.status == "passed" for check in checks)


def test_detects_unknown_country_reference(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_domain_events_with_unknown_country",
        lambda *_: [{"id": "event-1", "country_slug": "atlantis"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_what_changed_checks(CONNECTION, issues, checks)

    assert any(i.code == "what_changed_event_unknown_country" for i in issues)
    check = next(
        c
        for c in checks
        if c.code == "what_changed_events_reference_known_country"
    )
    assert check.status == "failed"


def test_detects_non_published_reference(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_domain_events_referencing_non_published_content",
        lambda *_: [{"id": "event-1", "event_type": "route.published"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_what_changed_checks(CONNECTION, issues, checks)

    codes = [i.code for i in issues]
    assert "what_changed_event_references_non_published_content" in codes
    critical = [i for i in issues if i.severity == "critical"]
    assert len(critical) == 1


def test_what_changed_item_requires_path_and_occurred_at() -> None:
    item = WhatChangedItem(
        id="item-1",
        event_type="route_published",
        entity_type="route",
        entity_id="route-1",
        country_slug="argentina",
        title="Route updated",
        summary="Summary",
        path="/routes/route-1",
        occurred_at=datetime.now(UTC),
        importance="medium",
        source="routes",
    )
    assert item.path
    assert item.occurred_at is not None
    assert item.event_type == "route_published"

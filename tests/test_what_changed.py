"""'What changed' feed: default/override time windows and unknown-country handling."""

import pytest
from app.repositories import (
    countries as countries_repository,
    what_changed as repository,
)
from app.services import what_changed as service
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from psycopg import Connection
from tests.test_openapi_contract import load_contract
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
NOW = datetime.now(UTC)


def install_country_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        countries_repository, "get_country", lambda *_: {"slug": "argentina"}
    )


def install_empty_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repository, "list_country_domain_events_since", lambda *_: []
    )
    monkeypatch.setattr(
        repository, "list_country_data_journal_since", lambda *_: []
    )
    monkeypatch.setattr(
        repository, "list_country_drift_changes_since", lambda *_: []
    )
    monkeypatch.setattr(
        repository, "list_country_route_changes_since", lambda *_: []
    )
    monkeypatch.setattr(
        repository, "list_country_legal_signal_changes_since", lambda *_: []
    )


def test_default_30_day_window(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    delta = datetime.now(UTC) - response.since
    assert 29 <= delta.days <= 30


def test_since_overrides_days(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    explicit_since = NOW - timedelta(days=5)

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", explicit_since, 30, 20
    )

    assert response.since == explicit_since


def test_unknown_country_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(countries_repository, "get_country", lambda *_: None)

    with pytest.raises(HTTPException) as exc_info:
        service.build_what_changed(CONNECTION, "unknown", "en", None, 30, 20)

    assert exc_info.value.status_code == 404
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "country_not_found"
    )


def test_route_change_appears(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_country_route_changes_since",
        lambda *_: [
            {
                "id": "route-1",
                "country_slug": "argentina",
                "title": "Temporary residence",
                "route_type": "temporary_residence",
                "route_slug": "temp",
                "occurred_at": NOW,
            }
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert any(item.event_type == "route_published" for item in response.items)
    assert response.summary.routes == 1


def test_legal_signal_publish_appears(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_country_legal_signal_changes_since",
        lambda *_: [
            {
                "id": "signal-1",
                "country_slug": "argentina",
                "title": "New visa rule",
                "signal_type": "visa",
                "impact_level": "high",
                "occurred_at": NOW,
            }
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert any(
        item.event_type == "legal_signal_published" for item in response.items
    )
    assert response.summary.legal_signals == 1
    assert response.items[0].importance == "high"


def test_drift_change_appears(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_country_drift_changes_since",
        lambda *_: [
            {
                "id": "snap-1",
                "country_slug": "argentina",
                "label": "negative",
                "previous_label": "stable",
                "confidence": "medium",
                "occurred_at": NOW,
            }
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert any(item.event_type == "drift_changed" for item in response.items)
    assert response.summary.drift == 1
    assert response.items[0].importance == "high"


def test_empty_state_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert response.items == []
    assert response.summary.total == 0


def test_items_sorted_newest_first(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    older = NOW - timedelta(days=10)
    newer = NOW - timedelta(days=1)
    monkeypatch.setattr(
        repository,
        "list_country_route_changes_since",
        lambda *_: [
            {
                "id": "route-old",
                "country_slug": "argentina",
                "title": "Old route",
                "route_type": "temporary_residence",
                "route_slug": "old",
                "occurred_at": older,
            }
        ],
    )
    monkeypatch.setattr(
        repository,
        "list_country_legal_signal_changes_since",
        lambda *_: [
            {
                "id": "signal-new",
                "country_slug": "argentina",
                "title": "New signal",
                "signal_type": "visa",
                "impact_level": "medium",
                "occurred_at": newer,
            }
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert response.items[0].occurred_at >= response.items[1].occurred_at


def test_limit_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_country_route_changes_since",
        lambda *_: [
            {
                "id": f"route-{i}",
                "country_slug": "argentina",
                "title": f"Route {i}",
                "route_type": "temporary_residence",
                "route_slug": f"route-{i}",
                "occurred_at": NOW - timedelta(hours=i),
            }
            for i in range(10)
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 3
    )

    assert len(response.items) == 3


def test_draft_content_hidden_by_repository_filters() -> None:
    import inspect

    for func in (
        repository.list_country_route_changes_since,
        repository.list_country_legal_signal_changes_since,
    ):
        source = inspect.getsource(func)
        assert "status = 'published'" in source


def test_dedup_collapses_overlapping_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_country_exists(monkeypatch)
    install_empty_sources(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_country_domain_events_since",
        lambda *_: [
            {
                "id": "de-1",
                "event_type": "route.published",
                "entity_type": "route",
                "entity_id": "route-1",
                "country_slug": "argentina",
                "payload": {"title": "Route"},
                "occurred_at": NOW,
            }
        ],
    )
    monkeypatch.setattr(
        repository,
        "list_country_route_changes_since",
        lambda *_: [
            {
                "id": "route-1",
                "country_slug": "argentina",
                "title": "Route",
                "route_type": "temporary_residence",
                "route_slug": "route",
                "occurred_at": NOW,
            }
        ],
    )

    response = service.build_what_changed(
        CONNECTION, "argentina", "en", None, 30, 20
    )

    assert response.summary.total == 1


def test_openapi_contains_what_changed_endpoint() -> None:
    contract = load_contract()

    assert "/api/v1/countries/{country_slug}/what-changed" in contract["paths"]
    for schema_name in [
        "WhatChangedItem",
        "WhatChangedSummary",
        "WhatChangedResponse",
    ]:
        assert schema_name in contract["components"]["schemas"]

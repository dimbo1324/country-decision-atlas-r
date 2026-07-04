"""Trip planner v1: schema, warnings, sharing, exports, reminders, and API wiring."""

import pytest
from app.api.v1 import trip_planner as trip_api
from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.repositories import (
    country_pairs,
    domain_events,
    trip_planner as repository,
)
from app.schemas.trip_planner import TripCreateRequest
from app.services import trip_planner as service
from app.services.trip_planner import helpers, reminders, sharing, warnings
from datetime import UTC, date, datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path
from psycopg import Connection
from tests.methodology_test_helpers import methodology_config
from tests.test_openapi_contract import load_contract
from typing import Any, cast
from unittest.mock import MagicMock
from uuid import UUID


CONNECTION = cast(Connection[Any], MagicMock())
USER_ID = "11111111-1111-1111-1111-111111111111"
TRIP_ID = "22222222-2222-2222-2222-222222222222"
WAYPOINT_ID = "33333333-3333-3333-3333-333333333333"
ITEM_ID = "44444444-4444-4444-4444-444444444444"
REMINDER_ID = "55555555-5555-5555-5555-555555555555"
NOW = datetime(2026, 7, 4, 12, 0, tzinfo=UTC)
MIGRATION_SQL = Path("database/migrations/047_trip_planner_v1.sql").read_text(
    encoding="utf-8"
)

USER = CurrentUser(
    id=USER_ID,
    email="user@example.local",
    display_name="User",
    role="user",
    status="active",
)


def _trip(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": TRIP_ID,
        "user_id": USER_ID,
        "title": "Uruguay relocation",
        "scenario_slug": "relocation_residence",
        "origin_country_id": "origin-country-id",
        "origin_country_slug": "russia",
        "origin_country_name": "Russia",
        "status": "draft",
        "confidence_tier": "declared",
        "visibility": "private",
        "share_token_prefix": None,
        "created_at": NOW,
        "updated_at": NOW,
        "completed_at": None,
    }
    row.update(overrides)
    return row


def _waypoint(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": WAYPOINT_ID,
        "trip_id": TRIP_ID,
        "position": 1,
        "country_id": "destination-country-id",
        "country_slug": "uruguay",
        "country_name": "Uruguay",
        "country_iso2": "UY",
        "city": "Montevideo",
        "kind": "destination",
        "planned_from": date(2026, 9, 1),
        "planned_to": None,
        "notes": "private note with user context",
        "created_at": NOW,
        "updated_at": NOW,
    }
    row.update(overrides)
    return row


def _checklist(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": ITEM_ID,
        "trip_id": TRIP_ID,
        "waypoint_id": WAYPOINT_ID,
        "title": "Check residence filing package",
        "description": "Private checklist details",
        "due_date": date(2026, 8, 20),
        "status": "todo",
        "origin_kind": "manual",
        "origin_ref": None,
        "position": 1,
        "created_at": NOW,
        "updated_at": NOW,
    }
    row.update(overrides)
    return row


def _disable_feature_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        helpers, "require_trip_planner_enabled", lambda *_: None
    )


def test_trip_planner_migration_creates_required_tables_and_feature_flag() -> (
    None
):
    for table in [
        "trips",
        "trip_waypoints",
        "trip_checklist_items",
        "trip_reminders",
        "trip_annotations",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in MIGRATION_SQL
    assert "'trip_planner_enabled'" in MIGRATION_SQL
    assert "'trip_reminder_due'" in MIGRATION_SQL
    assert "'trip.warning.high_impact_min_rank'" in MIGRATION_SQL


def test_openapi_contains_trip_planner_contract() -> None:
    contract = load_contract()
    paths = contract["paths"]
    schemas = contract["components"]["schemas"]

    for path in [
        "/api/v1/me/trips",
        "/api/v1/me/trips/from-passport",
        "/api/v1/me/trips/{trip_id}",
        "/api/v1/me/trips/{trip_id}/waypoints",
        "/api/v1/me/trips/{trip_id}/checklist",
        "/api/v1/me/trips/{trip_id}/warnings",
        "/api/v1/me/trips/{trip_id}/reminders",
        "/api/v1/me/trips/{trip_id}/share",
        "/api/v1/me/trips/{trip_id}/export",
        "/api/v1/me/trips/{trip_id}/annotations",
        "/api/v1/me/trips/{trip_id}/what-changed",
        "/api/v1/trips/shared/{token}",
    ]:
        assert path in paths
    for schema in [
        "TripDetailResponse",
        "TripWaypoint",
        "TripChecklistItem",
        "TripReminder",
        "TripWarning",
        "TripShareResponse",
        "SharedTripResponse",
    ]:
        assert schema in schemas


def test_warning_engine_combines_pair_and_high_impact_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_feature_gate(monkeypatch)
    monkeypatch.setattr(
        warnings,
        "get_active_methodology_config",
        lambda *_: methodology_config(),
    )
    monkeypatch.setattr(
        repository,
        "get_trip_for_user",
        lambda *_: _trip(),
    )
    monkeypatch.setattr(
        repository,
        "list_waypoints",
        lambda *_: [
            _waypoint(),
            _waypoint(
                id="waypoint-2",
                position=2,
                country_slug="argentina",
                country_name="Argentina",
            ),
        ],
    )

    def fake_pair(
        _conn: Any, origin: str, destination: str
    ) -> dict[str, Any] | None:
        if origin == "russia" and destination == "uruguay":
            return {
                "id": "pair-1",
                "compatibility_label": "restrictive",
                "practical_summary": "Banking route is restrictive.",
            }
        return None

    monkeypatch.setattr(
        country_pairs, "get_country_pair_compatibility", fake_pair
    )
    monkeypatch.setattr(
        country_pairs,
        "list_pair_sources",
        lambda *_: [{"id": "source-pair-1"}],
    )
    monkeypatch.setattr(
        repository,
        "list_published_legal_signals_for_country_slugs",
        lambda *_: [
            {
                "id": "signal-1",
                "country_slug": "uruguay",
                "title": "Tax rule changed",
                "summary": "High-impact tax rule changed.",
                "impact_level": "high",
                "source_id": "source-signal-1",
            }
        ],
    )

    result = warnings.build_trip_warnings(
        CONNECTION, user_id=USER_ID, trip_id=TRIP_ID
    )

    assert result.methodology_version == "v1.0"
    assert {item.code for item in result.items} == {
        "country_pair_restrictive",
        "country_pair_missing_context",
        "legal_signal_high_impact",
    }
    assert all(item.severity in {"medium", "high"} for item in result.items)


def test_shared_trip_projection_omits_private_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_feature_gate(monkeypatch)
    monkeypatch.setattr(
        repository,
        "get_trip_by_share_token_hash",
        lambda *_: _trip(visibility="link", share_token_prefix="abc12345"),
    )
    monkeypatch.setattr(repository, "list_waypoints", lambda *_: [_waypoint()])
    monkeypatch.setattr(
        repository, "list_checklist_items", lambda *_: [_checklist()]
    )

    result = sharing.get_shared_trip(CONNECTION, token="public-token")
    body = result.model_dump_json()

    assert "user_id" not in body
    assert "share_token" not in body
    assert "private note" not in body
    assert "Private checklist details" not in body
    assert "reminders" not in body
    assert "annotations" not in body


def test_ics_export_contains_due_checklist_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_feature_gate(monkeypatch)
    monkeypatch.setattr(repository, "get_trip_for_user", lambda *_: _trip())
    monkeypatch.setattr(repository, "list_waypoints", lambda *_: [_waypoint()])
    monkeypatch.setattr(
        repository, "list_checklist_items", lambda *_: [_checklist()]
    )
    monkeypatch.setattr(repository, "list_reminders", lambda *_: [])
    monkeypatch.setattr(repository, "list_annotations", lambda *_: [])

    content, media_type, filename = service.export_trip(
        CONNECTION, user_id=USER_ID, trip_id=TRIP_ID, export_format="ics"
    )

    assert media_type.startswith("text/calendar")
    assert filename.endswith(".ics")
    assert "BEGIN:VCALENDAR" in content
    assert "DTSTART;VALUE=DATE:20260820" in content
    assert "SUMMARY:Check residence filing package" in content


def test_dispatch_due_reminders_writes_idempotent_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "list_due_reminders",
        lambda *_a, **_kw: [
            {
                "id": REMINDER_ID,
                "trip_id": TRIP_ID,
                "checklist_item_id": ITEM_ID,
                "remind_at": NOW,
                "channel": "telegram",
                "user_id": USER_ID,
                "trip_title": "Uruguay relocation",
                "checklist_item_title": "File documents",
                "country_slug": "uruguay",
            }
        ],
    )
    monkeypatch.setattr(
        repository, "mark_reminder_sent", lambda *_: {"id": REMINDER_ID}
    )

    def fake_insert(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {"id": "event-1"}

    monkeypatch.setattr(domain_events, "insert_domain_event", fake_insert)

    summary = reminders.dispatch_due_reminders(CONNECTION, now=NOW, limit=100)

    assert summary == {"due_reminders": 1, "events_inserted": 1}
    assert captured["event_key"] == f"trip_reminder:{REMINDER_ID}"
    assert captured["event_type"] == "trip_reminder_due"
    assert captured["aggregate_id"] == UUID(REMINDER_ID)
    assert captured["payload"]["user_id"] == USER_ID


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(trip_api.router, prefix="/api/v1")
    app.include_router(trip_api.shared_router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    app.dependency_overrides[get_current_active_user] = lambda: USER
    return TestClient(app)


def test_create_trip_endpoint_commits(monkeypatch: pytest.MonkeyPatch) -> None:
    detail = helpers.trip_detail(_trip(), [], [], [], [])
    monkeypatch.setattr(service, "create_user_trip", lambda *_a, **_kw: detail)

    response = _client().post(
        "/api/v1/me/trips",
        json=TripCreateRequest(title="Uruguay relocation").model_dump(),
    )

    assert response.status_code == 201
    assert response.json()["item"]["id"] == TRIP_ID
    cast(Any, CONNECTION).commit.assert_called()

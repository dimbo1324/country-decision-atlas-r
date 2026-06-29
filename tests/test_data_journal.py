from app.api.v1.data_journal import router
from app.core.database import get_connection
from app.repositories import (
    countries as countries_repository,
    data_journal as repository,
)
from app.services import data_journal as service
from datetime import UTC, datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
NOW = datetime(2026, 6, 29, tzinfo=UTC)


def _row(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": "event-1",
        "event_type": "route.published",
        "country_slug": "russia",
        "entity_type": "route",
        "entity_id": "route-1",
        "payload": {"title": "Temporary residence", "route_type": "residence"},
        "event_date": NOW,
        "source": "domain_events",
        "is_source_backed": True,
        "last_verified_at": NOW,
    }
    data.update(overrides)
    return data


def _client(monkeypatch: Any, rows: list[dict[str, Any]]) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    monkeypatch.setattr(
        countries_repository,
        "get_country",
        lambda _conn, slug, _locale: {"slug": slug} if slug != "missing" else None,
    )
    monkeypatch.setattr(
        repository, "list_country_data_journal_entries", lambda *_: rows
    )
    monkeypatch.setattr(
        repository, "count_country_data_journal_entries", lambda *_: len(rows)
    )
    monkeypatch.setattr(
        repository,
        "get_country_last_verified_at",
        lambda *_: {"last_verified_at": NOW} if rows else {"last_verified_at": None},
    )
    return TestClient(app)


def test_endpoint_returns_200_for_countries(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_row()])
    for slug in ["russia", "uruguay", "argentina"]:
        response = client.get(f"/api/v1/countries/{slug}/data-journal?locale=ru")
        assert response.status_code == 200
        assert response.json()["country_slug"] == slug


def test_unknown_country_returns_404(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [])
    response = client.get("/api/v1/countries/missing/data-journal?locale=ru")
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "country_not_found"


def test_limit_is_bounded(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [])
    assert (
        client.get("/api/v1/countries/russia/data-journal?limit=0").status_code == 422
    )
    assert (
        client.get("/api/v1/countries/russia/data-journal?limit=51").status_code == 422
    )


def test_offset_works(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}
    client = _client(monkeypatch, [_row()])

    def fake_list(
        _conn: Connection[Any], _slug: str, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        captured["limit"] = limit
        captured["offset"] = offset
        return [_row()]

    monkeypatch.setattr(repository, "list_country_data_journal_entries", fake_list)
    response = client.get("/api/v1/countries/russia/data-journal?limit=5&offset=2")
    assert response.status_code == 200
    assert captured == {"limit": 5, "offset": 2}


def test_response_contains_no_internal_fields(monkeypatch: Any) -> None:
    client = _client(
        monkeypatch,
        [
            _row(
                payload={
                    "title": "Safe",
                    "changed_by": "admin",
                    "raw_diff": {"secret": True},
                    "last_error": "boom",
                }
            )
        ],
    )
    body = client.get("/api/v1/countries/russia/data-journal?locale=en").json()
    text = str(body)
    for forbidden in ["changed_by", "raw_diff", "admin", "last_error", "attempts"]:
        assert forbidden not in text


def test_empty_journal_returns_items_empty(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [])
    body = client.get("/api/v1/countries/russia/data-journal?locale=ru").json()
    assert body["items"] == []
    assert body["total"] == 0


def test_journal_supports_ru_and_en(monkeypatch: Any) -> None:
    client = _client(monkeypatch, [_row()])
    assert (
        client.get("/api/v1/countries/russia/data-journal?locale=ru").status_code == 200
    )
    assert (
        client.get("/api/v1/countries/russia/data-journal?locale=en").status_code == 200
    )
    assert (
        client.get("/api/v1/countries/russia/data-journal?locale=es").status_code == 422
    )


def test_public_text_falls_back_to_generic_title() -> None:
    result = service.public_title_for_event("unknown", {}, "ru")
    assert result == "Данные обновлены"

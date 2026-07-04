"""Search API: input validation and filtering by entity type."""

import pytest
from app.repositories import search as repository
from app.services import search as service
from fastapi import HTTPException
from psycopg import Connection
from tests.test_openapi_contract import load_contract
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def install_empty_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "search_documents", lambda *_: [])
    monkeypatch.setattr(
        repository, "count_search_documents_matching", lambda *_: 0
    )


def test_empty_query_returns_422() -> None:
    with pytest.raises(HTTPException) as exc_info:
        service.run_search(CONNECTION, "   ", "en", None, None, 20, 0)

    assert exc_info.value.status_code == 422
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "search_query_empty"
    )


def test_invalid_entity_type_returns_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_empty_results(monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        service.run_search(CONNECTION, "visa", "en", "not_a_type", None, 20, 0)

    assert exc_info.value.status_code == 422
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "invalid_search_entity_type"
    )


def test_search_returns_route_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repository,
        "search_documents",
        lambda *_: [
            {
                "id": "doc-1",
                "entity_type": "route",
                "entity_id": "route-1",
                "country_slug": "argentina",
                "title": "Temporary residence",
                "snippet": "A route about temporary residence",
                "path": "/routes/route-1",
                "rank": 0.5,
            }
        ],
    )
    monkeypatch.setattr(
        repository, "count_search_documents_matching", lambda *_: 1
    )

    response = service.run_search(
        CONNECTION, "residence", "en", None, None, 20, 0
    )

    assert response.total == 1
    assert response.items[0].entity_type == "route"
    assert response.items[0].country_slug == "argentina"


def test_search_filters_by_types(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search_documents(*args: Any) -> list[dict[str, Any]]:
        captured["entity_types"] = args[3]
        return []

    monkeypatch.setattr(repository, "search_documents", fake_search_documents)
    monkeypatch.setattr(
        repository, "count_search_documents_matching", lambda *_: 0
    )

    service.run_search(
        CONNECTION, "visa", "en", "route,legal_signal", None, 20, 0
    )

    assert captured["entity_types"] == ["route", "legal_signal"]


def test_search_filters_by_country_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_search_documents(*args: Any) -> list[dict[str, Any]]:
        captured["country_slug"] = args[4]
        return []

    monkeypatch.setattr(repository, "search_documents", fake_search_documents)
    monkeypatch.setattr(
        repository, "count_search_documents_matching", lambda *_: 0
    )

    service.run_search(CONNECTION, "visa", "en", None, "argentina", 20, 0)

    assert captured["country_slug"] == "argentina"


def test_search_preserves_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    install_empty_results(monkeypatch)

    response = service.run_search(CONNECTION, "visa", "ru", None, None, 20, 0)

    assert response.locale == "ru"


def test_search_query_is_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    install_empty_results(monkeypatch)

    response = service.run_search(
        CONNECTION, "  visa  ", "en", None, None, 20, 0
    )

    assert response.query == "visa"


def test_empty_result_state_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_empty_results(monkeypatch)

    response = service.run_search(
        CONNECTION, "no-matches-here", "en", None, None, 20, 0
    )

    assert response.items == []
    assert response.total == 0


def test_search_only_selects_published_status_in_sql() -> None:
    import inspect

    for func in (
        repository.search_documents,
        repository.count_search_documents_matching,
    ):
        source = inspect.getsource(func)
        assert "sd.status = 'published'" in source


def test_search_uses_parameterized_query() -> None:
    import inspect

    source = inspect.getsource(repository.search_documents)
    assert "websearch_to_tsquery" in source
    assert "ts_rank" in source


def test_openapi_contains_search_endpoint() -> None:
    contract = load_contract()

    assert "/api/v1/search" in contract["paths"]
    for schema_name in ["SearchResponse", "SearchResultItem"]:
        assert schema_name in contract["components"]["schemas"]

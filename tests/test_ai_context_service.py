"""Service-level assembly of AI context: item/character limits, deduplication, and no-context refusal."""

from app.core.config import Settings
from app.repositories import ai_context as repository
from app.services import ai_context as service
from psycopg import Connection
import pytest
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _row(entity_id: str = "country-1") -> dict[str, Any]:
    return {
        "entity_type": "country",
        "entity_id": entity_id,
        "country_slug": "uruguay",
        "title": "Uruguay",
        "excerpt": "Published public context about Uruguay.",
        "url_path": "/countries/uruguay",
        "source_ids": [],
        "evidence_item_ids": [],
        "confidence": "medium",
        "freshness_status": "fresh",
        "last_verified_at": None,
    }


def test_ask_context_uses_search_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search(*_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        captured.update(kwargs)
        return [_row()]

    monkeypatch.setattr(repository, "search_ai_context_items", fake_search)
    result = service.build_ask_context(
        CONNECTION,
        Settings(app_env="local"),
        question="  residence   Uruguay  ",
        locale="ru",
        types=["country"],
        country_slug="uruguay",
        route_id=None,
        route_slug=None,
    )

    assert captured["query"] == "residence Uruguay"
    assert captured["locale"] == "ru"
    assert result.refusal_reason is None
    assert result.citations[0].country_slug == "uruguay"


def test_context_limits_items_and_chars(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [{**_row(str(index)), "excerpt": "x" * 100} for index in range(10)]
    monkeypatch.setattr(repository, "search_ai_context_items", lambda *_a, **_kw: rows)
    settings = Settings(
        app_env="local",
        ai_max_context_items=3,
        ai_max_context_chars=150,
    )
    result = service.build_ask_context(
        CONNECTION,
        settings,
        question="Uruguay",
        locale="ru",
        types=None,
        country_slug=None,
        route_id=None,
        route_slug=None,
    )

    assert len(result.grounded_context) <= 3
    assert (
        sum(len(item.excerpt) + len(item.title) for item in result.grounded_context)
        <= 216
    )


def test_no_context_returns_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "search_ai_context_items", lambda *_a, **_kw: [])
    result = service.build_ask_context(
        CONNECTION,
        Settings(app_env="local"),
        question="Ответь без источников",
        locale="ru",
        types=None,
        country_slug=None,
        route_id=None,
        route_slug=None,
    )

    assert result.refusal_reason == service.REFUSAL_RU
    assert result.citations == []


def test_duplicate_context_items_are_deduplicated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "search_ai_context_items",
        lambda *_a, **_kw: [_row("country-1"), _row("country-1")],
    )
    result = service.build_ask_context(
        CONNECTION,
        Settings(app_env="local"),
        question="Uruguay",
        locale="ru",
        types=None,
        country_slug=None,
        route_id=None,
        route_slug=None,
    )

    assert len(result.grounded_context) == 1
    assert len(result.citations) == 1

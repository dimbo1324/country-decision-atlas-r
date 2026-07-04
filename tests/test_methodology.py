"""Methodology section listing: locale handling, empty results, and lookup by slug."""

from app.repositories import methodology as methodology_repo
from typing import Any
from unittest.mock import MagicMock


_SECTION_EN = {
    "slug": "what_is_trust_score",
    "title": "What is Trust Score?",
    "summary": "A data quality indicator.",
    "body": "The trust score measures...",
    "section_type": "trust",
    "display_order": 8,
    "updated_at": None,
}

_SECTION_RU = {
    "slug": "what_is_trust_score",
    "title": "Что такое Trust Score?",
    "summary": "Индикатор качества данных.",
    "body": "Trust score измеряет...",
    "section_type": "trust",
    "display_order": 8,
    "updated_at": None,
}


def _conn_returning_list(rows: list[dict[str, Any]], monkeypatch: Any) -> Any:
    conn = MagicMock()
    monkeypatch.setattr(
        "app.repositories.methodology.fetch_all",
        lambda *_a, **_kw: rows,
    )
    return conn


def _conn_returning_one(row: dict[str, Any] | None, monkeypatch: Any) -> Any:
    conn = MagicMock()
    monkeypatch.setattr(
        "app.repositories.methodology.fetch_one",
        lambda *_a, **_kw: row,
    )
    return conn


def test_list_methodology_sections_returns_items(monkeypatch: Any) -> None:
    conn = _conn_returning_list([_SECTION_EN], monkeypatch)
    result = methodology_repo.list_methodology_sections(conn, "en")
    assert len(result) == 1
    assert result[0]["slug"] == "what_is_trust_score"


def test_list_methodology_sections_ru_locale(monkeypatch: Any) -> None:
    conn = _conn_returning_list([_SECTION_RU], monkeypatch)
    result = methodology_repo.list_methodology_sections(conn, "ru")
    assert result[0]["title"] == "Что такое Trust Score?"


def test_list_methodology_sections_empty(monkeypatch: Any) -> None:
    conn = _conn_returning_list([], monkeypatch)
    result = methodology_repo.list_methodology_sections(conn)
    assert result == []


def test_get_methodology_section_found(monkeypatch: Any) -> None:
    conn = _conn_returning_one(_SECTION_EN, monkeypatch)
    result = methodology_repo.get_methodology_section(
        conn, "what_is_trust_score", "en"
    )
    assert result is not None
    assert result["slug"] == "what_is_trust_score"
    assert result["section_type"] == "trust"


def test_get_methodology_section_not_found(monkeypatch: Any) -> None:
    conn = _conn_returning_one(None, monkeypatch)
    result = methodology_repo.get_methodology_section(conn, "nonexistent", "en")
    assert result is None


def test_get_methodology_section_ru_locale(monkeypatch: Any) -> None:
    conn = _conn_returning_one(_SECTION_RU, monkeypatch)
    result = methodology_repo.get_methodology_section(
        conn, "what_is_trust_score", "ru"
    )
    assert result is not None
    assert "Что" in result["title"]

"""Glossary term listing: locale handling, empty results, and category filtering."""

from app.repositories import glossary as glossary_repo
from typing import Any
from unittest.mock import MagicMock


_TERM_EN = {
    "slug": "trust_score",
    "term": "Trust Score",
    "definition": "A composite data quality indicator.",
    "category": "trust",
    "related_terms": ["confidence", "freshness"],
    "display_order": 11,
    "updated_at": None,
}

_TERM_RU = {
    "slug": "trust_score",
    "term": "Показатель доверия",
    "definition": "Составной индикатор качества данных.",
    "category": "trust",
    "related_terms": ["confidence", "freshness"],
    "display_order": 11,
    "updated_at": None,
}


def _conn_list(rows: list[dict[str, Any]], monkeypatch: Any) -> Any:
    monkeypatch.setattr("app.repositories.glossary.fetch_all", lambda *_a, **_kw: rows)
    return MagicMock()


def _conn_one(row: dict[str, Any] | None, monkeypatch: Any) -> Any:
    monkeypatch.setattr("app.repositories.glossary.fetch_one", lambda *_a, **_kw: row)
    return MagicMock()


def test_list_glossary_terms_returns_items(monkeypatch: Any) -> None:
    conn = _conn_list([_TERM_EN], monkeypatch)
    result = glossary_repo.list_glossary_terms(conn, "en")
    assert len(result) == 1
    assert result[0]["slug"] == "trust_score"


def test_list_glossary_terms_ru_locale(monkeypatch: Any) -> None:
    conn = _conn_list([_TERM_RU], monkeypatch)
    result = glossary_repo.list_glossary_terms(conn, "ru")
    assert result[0]["term"] == "Показатель доверия"


def test_list_glossary_terms_empty(monkeypatch: Any) -> None:
    conn = _conn_list([], monkeypatch)
    result = glossary_repo.list_glossary_terms(conn)
    assert result == []


def test_list_glossary_terms_with_category_filter(monkeypatch: Any) -> None:
    conn = _conn_list([_TERM_EN], monkeypatch)
    result = glossary_repo.list_glossary_terms(conn, "en", category="trust")
    assert len(result) == 1


def test_list_glossary_terms_with_query_filter(monkeypatch: Any) -> None:
    conn = _conn_list([_TERM_EN], monkeypatch)
    result = glossary_repo.list_glossary_terms(conn, "en", query="trust")
    assert len(result) == 1


def test_get_glossary_term_found(monkeypatch: Any) -> None:
    conn = _conn_one(_TERM_EN, monkeypatch)
    result = glossary_repo.get_glossary_term(conn, "trust_score", "en")
    assert result is not None
    assert result["term"] == "Trust Score"
    assert result["category"] == "trust"


def test_get_glossary_term_not_found(monkeypatch: Any) -> None:
    conn = _conn_one(None, monkeypatch)
    result = glossary_repo.get_glossary_term(conn, "nonexistent", "en")
    assert result is None


def test_get_glossary_term_ru_locale(monkeypatch: Any) -> None:
    conn = _conn_one(_TERM_RU, monkeypatch)
    result = glossary_repo.get_glossary_term(conn, "trust_score", "ru")
    assert result is not None
    assert "доверия" in result["term"]

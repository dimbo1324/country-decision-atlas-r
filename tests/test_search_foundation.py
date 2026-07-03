from app.repositories import search_index as repository
from app.services.data_quality.search_foundation_checks import (
    _append_search_foundation_checks,
)
from pathlib import Path
from psycopg import Connection
from typing import Any, cast


MIGRATION = Path("database/migrations/040_search_foundation.sql")
CONNECTION = cast(Connection[Any], object())

VALID_ENTITY_TYPES = {
    "country",
    "route",
    "route_checklist_item",
    "legal_signal",
    "source",
    "evidence_item",
    "country_pair_compatibility",
    "methodology",
    "glossary_term",
}


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


class FakeSearchDocumentStore:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, str], dict[str, Any]] = {}

    def insert(
        self, entity_type: str, entity_id: str, locale: str, **fields: Any
    ) -> dict[str, Any]:
        if entity_type not in VALID_ENTITY_TYPES:
            raise ValueError("search_documents_entity_type_check")
        if locale not in {"ru", "en"}:
            raise ValueError("search_documents_locale_check")
        status = fields.get("status", "published")
        if status not in {"published", "archived"}:
            raise ValueError("search_documents_status_check")
        key = (entity_type, entity_id, locale)
        row = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "locale": locale,
            **fields,
        }
        self.rows[key] = row
        return row


def test_migration_creates_search_documents_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS search_documents" in _sql()


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("CREATE TABLE IF NOT EXISTS search_documents") == 1
    assert sql.count("CREATE OR REPLACE FUNCTION build_search_vector") == 1


def test_migration_creates_gin_index() -> None:
    assert "USING GIN (search_vector)" in _sql()


def test_migration_creates_build_search_vector_function() -> None:
    assert "CREATE OR REPLACE FUNCTION build_search_vector" in _sql()
    assert "RETURNS TSVECTOR" in _sql()


def test_migration_does_not_bulk_index_content() -> None:
    sql = _sql()
    assert "INSERT INTO search_documents" not in sql


def test_migration_does_not_touch_scoring_tables() -> None:
    sql = _sql()
    for forbidden in (
        "country_cii_scores",
        "country_scores",
        "country_score_breakdowns",
        "scenario_metric_weights",
        "country_trust_scores",
        "country_drift_snapshots",
        "decision_passports",
    ):
        assert forbidden not in sql


def test_invalid_entity_type_rejected() -> None:
    store = FakeSearchDocumentStore()
    try:
        store.insert("decision_passport", "id-1", "en")
    except ValueError as error:
        assert "entity_type_check" in str(error)
    else:
        raise AssertionError("Invalid entity_type was accepted")


def test_invalid_locale_rejected() -> None:
    store = FakeSearchDocumentStore()
    try:
        store.insert("route", "id-1", "fr")
    except ValueError as error:
        assert "locale_check" in str(error)
    else:
        raise AssertionError("Invalid locale was accepted")


def test_invalid_status_rejected() -> None:
    store = FakeSearchDocumentStore()
    try:
        store.insert("route", "id-1", "en", status="draft")
    except ValueError as error:
        assert "status_check" in str(error)
    else:
        raise AssertionError("Invalid status was accepted")


def test_unique_entity_type_entity_id_locale_enforced() -> None:
    store = FakeSearchDocumentStore()
    store.insert("route", "id-1", "en")
    store.insert("route", "id-1", "en")
    assert len(store.rows) == 1


def test_ru_and_en_documents_can_coexist() -> None:
    store = FakeSearchDocumentStore()
    store.insert("route", "id-1", "ru")
    store.insert("route", "id-1", "en")
    assert len(store.rows) == 2


def test_upsert_search_document_source_is_sql_only() -> None:
    import inspect

    source = inspect.getsource(repository.upsert_search_document)
    assert "build_search_vector" in source
    assert "ON CONFLICT (entity_type, entity_id, locale)" in source


def _install_clean_coverage_fakes(monkeypatch: Any) -> Any:
    from app.repositories import data_quality as dq_repository

    monkeypatch.setattr(
        dq_repository,
        "list_search_documents_referencing_non_published_content",
        lambda *_: [],
    )
    for name in [
        "list_active_countries_missing_from_index",
        "list_published_routes_missing_from_index",
        "list_published_legal_signals_missing_from_index",
        "list_published_sources_missing_from_index",
        "list_published_evidence_missing_from_index",
        "list_search_documents_with_incomplete_locale_coverage",
    ]:
        monkeypatch.setattr(dq_repository, name, lambda *_: [])
    return dq_repository


def test_dq_ignores_empty_index_as_non_critical(monkeypatch: Any) -> None:
    monkeypatch.setattr(repository, "list_broken_search_documents", lambda *_: [])
    monkeypatch.setattr(repository, "count_search_documents", lambda *_: 0)
    _install_clean_coverage_fakes(monkeypatch)

    issues: list[Any] = []
    checks: list[Any] = []
    _append_search_foundation_checks(CONNECTION, issues, checks)

    assert all(issue.severity != "critical" for issue in issues)
    assert any(issue.code == "search_index_empty" for issue in issues)


def test_dq_detects_broken_document(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        repository,
        "list_broken_search_documents",
        lambda *_: [{"id": "doc-1", "path": ""}],
    )
    monkeypatch.setattr(repository, "count_search_documents", lambda *_: 1)
    _install_clean_coverage_fakes(monkeypatch)

    issues: list[Any] = []
    checks: list[Any] = []
    _append_search_foundation_checks(CONNECTION, issues, checks)

    critical = [i for i in issues if i.severity == "critical"]
    assert any(i.code == "search_document_invalid" for i in critical)


def test_dq_detects_coverage_gap_when_index_populated(monkeypatch: Any) -> None:
    monkeypatch.setattr(repository, "list_broken_search_documents", lambda *_: [])
    monkeypatch.setattr(repository, "count_search_documents", lambda *_: 1)
    dq_repository = _install_clean_coverage_fakes(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_published_routes_missing_from_index",
        lambda *_: [{"id": "route-1", "slug": "route-slug", "country_slug": "russia"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_search_foundation_checks(CONNECTION, issues, checks)

    critical = [i for i in issues if i.severity == "critical"]
    assert any(i.code == "search_coverage_gap_route" for i in critical)


def test_dq_flags_incomplete_locale_coverage_as_warning(monkeypatch: Any) -> None:
    monkeypatch.setattr(repository, "list_broken_search_documents", lambda *_: [])
    monkeypatch.setattr(repository, "count_search_documents", lambda *_: 1)
    dq_repository = _install_clean_coverage_fakes(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_search_documents_with_incomplete_locale_coverage",
        lambda *_: [
            {"entity_type": "route", "entity_id": "route-1", "locale_count": 1}
        ],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_search_foundation_checks(CONNECTION, issues, checks)

    warnings = [i for i in issues if i.severity == "warning"]
    assert any(i.code == "search_document_incomplete_locale_coverage" for i in warnings)
    assert all(i.severity != "critical" for i in issues)

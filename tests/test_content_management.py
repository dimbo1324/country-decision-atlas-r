"""Schema assertions for the content management migration and related OpenAPI/publish-validation behavior."""

from app.repositories import sources as source_repository
from app.repositories.sorting import resolve_sort_clause
from app.schemas.admin_content import EvidenceItemCreate, SourceCreate
from app.schemas.common import PublicationStatus
from app.services import admin_content
from fastapi import HTTPException
from pathlib import Path
import pytest
from tests.test_openapi_contract import load_contract
from typing import Any, cast


MIGRATION_SQL = Path("database/migrations/007_content_management.sql").read_text(
    encoding="utf-8"
)


def test_content_management_migration_adds_lifecycle_and_audit() -> None:
    for status in ["draft", "review", "published", "archived", "rejected"]:
        assert status in MIGRATION_SQL

    assert "CREATE TABLE IF NOT EXISTS audit_events" in MIGRATION_SQL
    assert "idx_audit_events_entity" in MIGRATION_SQL
    assert "idx_audit_events_changed_at" in MIGRATION_SQL


def test_openapi_has_admin_security_and_content_schemas() -> None:
    contract = load_contract()
    paths = contract["paths"]
    schemas = contract["components"]["schemas"]

    for path in [
        "/api/v1/admin/sources",
        "/api/v1/admin/sources/{source_id}",
        "/api/v1/admin/evidence-items",
        "/api/v1/admin/evidence-items/{evidence_item_id}",
        "/api/v1/admin/legal-signals",
        "/api/v1/admin/legal-signals/{signal_id}",
        "/api/v1/admin/countries/{country_slug}/profile",
        "/api/v1/admin/user-stories",
        "/api/v1/admin/user-stories/{story_id}",
        "/api/v1/admin/data-quality/report",
    ]:
        assert path in paths

    assert contract["components"]["securitySchemes"]["BearerAuth"] == {
        "type": "http",
        "scheme": "bearer",
    }
    for schema in [
        "PublicationStatus",
        "AuditEvent",
        "SourceCreate",
        "SourcePatch",
        "LegalSignalCreate",
        "LegalSignalPatch",
        "EvidenceItemCreate",
        "EvidenceItemPatch",
        "CountryProfilePatch",
        "UserStoryAdminCreate",
        "UserStoryPatch",
        "DataQualityIssue",
        "DataQualityReport",
        "ErrorResponse",
    ]:
        assert schema in schemas


def test_public_read_openapi_exposes_filters_pagination_and_sort() -> None:
    contract = load_contract()
    checks = {
        "/api/v1/legal-signals": {
            "country_slug",
            "signal_type",
            "impact_direction",
            "impact_level",
            "status",
            "locale",
            "limit",
            "offset",
            "sort",
            "order",
        },
        "/api/v1/sources": {
            "country_slug",
            "source_type",
            "language",
            "confidence",
            "status",
            "limit",
            "offset",
            "sort",
            "order",
        },
        "/api/v1/evidence-items": {
            "country_slug",
            "source_id",
            "legal_signal_id",
            "confidence",
            "status",
            "limit",
            "offset",
            "sort",
            "order",
        },
        "/api/v1/user-stories": {
            "origin_country_slug",
            "destination_country_slug",
            "scenario",
            "verification_status",
            "is_synthetic",
            "status",
            "limit",
            "offset",
            "sort",
            "order",
        },
    }

    for path, expected_params in checks.items():
        params = {
            param["name"] for param in contract["paths"][path]["get"]["parameters"]
        }
        assert expected_params.issubset(params)


def test_publish_source_validation_blocks_missing_required_fields() -> None:
    payload = SourceCreate(
        title="Draft source",
        source_type="official",
        publisher="Example",
        confidence="high",
        status=PublicationStatus.published,
    )

    with pytest.raises(HTTPException) as error:
        admin_content.create_source(cast(Any, object()), payload, "admin")

    assert error.value.status_code == 422
    detail = cast(dict[str, Any], error.value.detail)
    assert detail["error"]["code"] == "data_quality_validation_failed"
    fields = {
        issue["details"]["field"] for issue in detail["error"]["details"]["issues"]
    }
    assert "url" in fields


def test_publish_evidence_validation_blocks_missing_required_fields() -> None:
    payload = EvidenceItemCreate(status=PublicationStatus.published)

    with pytest.raises(HTTPException) as error:
        admin_content.create_evidence_item(cast(Any, object()), payload, "admin")

    assert error.value.status_code == 422
    detail = cast(dict[str, Any], error.value.detail)
    fields = {
        issue["details"]["field"] for issue in detail["error"]["details"]["issues"]
    }
    assert {"source_id", "country_id", "claim"}.issubset(fields)


def test_source_sorting_uses_whitelist(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return []

    monkeypatch.setattr(source_repository, "fetch_all", fake_fetch_all)

    source_repository.list_sources(
        cast(Any, object()),
        20,
        0,
        None,
        None,
        None,
        None,
        "published",
        "unsafe_column",
        "desc",
    )

    assert "ORDER BY s.last_checked_at DESC" in captured["query"]
    assert "unsafe_column" not in captured["query"]


def test_sort_clause_resolver_uses_whitelisted_columns() -> None:
    columns = {"created_at": "items.created_at", "title": "items.title"}

    assert resolve_sort_clause("title", "asc", columns, "created_at") == (
        "items.title",
        "ASC",
    )
    assert resolve_sort_clause("unsafe", "drop table", columns, "created_at") == (
        "items.created_at",
        "DESC",
    )

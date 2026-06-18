from app.api.v1 import admin as admin_route
from app.repositories import data_quality as data_quality_repository
from app.schemas.data_quality import DataQualityReport
from app.services import data_quality
import asyncio
from fastapi import HTTPException
from pathlib import Path
from psycopg import Connection
from tests.test_openapi_contract import load_contract
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
MIGRATION_SQL = Path(
    "database/migrations/008_data_quality_validation_v1.sql"
).read_text(encoding="utf-8")


def install_clean_report_fakes(monkeypatch: Any) -> None:
    for name in [
        "list_missing_mvp_countries",
        "list_published_countries_without_cards",
        "list_published_countries_without_sources",
        "list_missing_country_scores_for_required_scenarios",
        "list_scores_without_breakdowns",
        "list_scores_with_incomplete_breakdowns",
        "list_scores_with_invalid_weight_sum",
        "list_published_legal_signals_without_source",
        "list_published_legal_signals_without_evidence",
        "list_evidence_without_source",
        "list_evidence_without_country",
        "list_published_sources_with_missing_required_fields",
        "list_invalid_synthetic_user_stories",
        "list_country_cards_with_empty_major_sections",
    ]:
        monkeypatch.setattr(data_quality_repository, name, lambda *_: [])


def test_data_quality_migration_adds_required_constraints() -> None:
    for constraint in [
        "country_scores_score_range_check",
        "country_score_breakdowns_score_range_check",
        "country_score_breakdowns_weight_range_check",
        "sources_published_quality_check",
        "legal_signals_published_quality_check",
        "evidence_items_published_quality_check",
        "user_stories_synthetic_quality_check",
    ]:
        assert constraint in MIGRATION_SQL
    assert "status = 'review'" in MIGRATION_SQL


def test_clean_data_quality_report_is_valid(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is True
    assert report.issues == []


def test_data_quality_report_aggregates_critical_and_warning_issues(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_without_source",
        lambda *_: [{"id": "signal-id", "title": "Signal", "country_id": "country-id"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_without_evidence",
        lambda *_: [{"id": "signal-id", "title": "Signal", "country_id": "country-id"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {issue.code for issue in report.issues} == {
        "published_legal_signal_source_missing",
        "published_legal_signal_evidence_missing",
    }
    assert any(issue.severity == "critical" for issue in report.issues)
    assert any(issue.severity == "warning" for issue in report.issues)


def test_source_publish_validation_requires_required_metadata() -> None:
    issues = data_quality.validate_source_for_publish(
        {
            "id": "source-id",
            "title": "Source",
            "source_type": "official",
            "confidence": "high",
        }
    )

    assert {issue.details["field"] for issue in issues} == {"url", "publisher"}


def test_legal_signal_publish_validation_requires_source() -> None:
    issues = data_quality.validate_legal_signal_for_publish(
        {
            "id": "signal-id",
            "country_id": "country-id",
            "title_en": "Signal",
            "summary_en": "Summary",
            "signal_type": "residence",
            "impact_direction": "mixed",
            "impact_level": "medium",
            "confidence": "medium",
        }
    )

    assert any(issue.details["field"] == "source_id" for issue in issues)


def test_evidence_publish_validation_requires_traceability() -> None:
    issues = data_quality.validate_evidence_item_for_publish(
        {
            "id": "evidence-id",
            "claim": "Claim",
            "confidence": "medium",
        }
    )

    assert {"source_id", "country_id", "excerpt"}.issubset(
        {str(issue.details["field"]) for issue in issues}
    )


def test_synthetic_user_story_publish_validation_requires_marking() -> None:
    issues = data_quality.validate_user_story_for_publish(
        {
            "id": "story-id",
            "origin_country_id": "russia-id",
            "destination_country_id": "uruguay-id",
            "scenario": "relocation_residence",
            "year": 2026,
            "verification_status": "verified",
            "is_synthetic": True,
            "notes": "Real user story",
        }
    )

    assert "synthetic_user_story_invalid" in {issue.code for issue in issues}
    assert "user_story_verified_without_verification" in {
        issue.code for issue in issues
    }


def test_raise_if_critical_issues_uses_data_quality_error_shape() -> None:
    issues = data_quality.validate_source_for_publish({"id": "source-id"})

    try:
        data_quality.raise_if_critical_issues(issues)
    except HTTPException as error:
        detail = cast(dict[str, Any], error.detail)
        assert error.status_code == 422
        assert detail["error"]["code"] == "data_quality_validation_failed"
        assert detail["error"]["details"]["issues"]
    else:
        raise AssertionError("Critical data-quality issues were accepted")


def test_admin_data_quality_report_route(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        admin_route,
        "build_data_quality_report",
        lambda *_: DataQualityReport(valid=True),
    )

    result = asyncio.run(
        admin_route.admin_read_data_quality_report(CONNECTION, "admin")
    )

    assert result.valid is True
    assert result.issues == []


def test_openapi_has_admin_data_quality_report() -> None:
    contract = load_contract()

    assert "/api/v1/admin/data-quality/report" in contract["paths"]
    assert "DataQualityIssue" in contract["components"]["schemas"]
    assert "DataQualityReport" in contract["components"]["schemas"]

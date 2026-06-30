from app.api.v1 import admin as admin_route
from app.repositories import data_quality as data_quality_repository
from app.schemas.data_quality import DataQualityReport
from app.services import data_quality
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
    monkeypatch.setattr(
        data_quality,
        "build_translation_quality_results",
        lambda *_: ([], []),
    )
    monkeypatch.setattr(
        data_quality,
        "build_country_onboarding_dq_results",
        lambda *_: ([], []),
    )
    for name in [
        "list_missing_mvp_countries",
        "list_published_countries_without_cards",
        "list_published_countries_without_sources",
        "list_mvp_countries_with_too_few_published_sources",
        "list_mvp_countries_with_too_few_published_evidence",
        "list_mvp_countries_with_too_few_published_legal_signals",
        "list_missing_country_scores_for_required_scenarios",
        "list_scores_without_breakdowns",
        "list_scores_with_incomplete_breakdowns",
        "list_scores_with_invalid_weight_sum",
        "list_published_score_breakdowns_without_source_ids",
        "list_published_legal_signals_without_source",
        "list_published_legal_signals_without_evidence",
        "list_published_legal_signals_without_timeline_event",
        "list_published_legal_signals_with_missing_legal_status",
        "list_published_legal_signals_with_unknown_legal_status",
        "list_review_sources_with_missing_required_fields",
        "list_review_evidence_items_with_missing_required_fields",
        "list_review_legal_signals_with_missing_required_fields",
        "list_published_evidence_items_with_missing_required_fields",
        "list_published_legal_signals_with_missing_required_fields",
        "list_invalid_domain_events_for_dq",
        "list_timeline_events_with_invalid_date",
        "list_timeline_events_with_invalid_impact_direction",
        "list_timeline_events_with_invalid_impact_level",
        "list_timeline_events_with_country_mismatch",
        "list_timeline_events_without_traceability",
        "list_unplanned_future_timeline_events",
        "list_evidence_without_source",
        "list_evidence_without_country",
        "list_published_sources_with_missing_required_fields",
        "list_published_sources_with_example_invalid_url",
        "list_invalid_synthetic_user_stories",
        "list_country_cards_with_empty_major_sections",
        "list_country_cards_with_demo_source_summary",
        "list_mvp_countries_missing_cii",
        "list_cii_scores_missing_formula_metadata",
        "list_cii_metric_weights_with_invalid_sum",
        "list_mvp_metrics_missing_values",
        "list_cii_scores_out_of_range",
        "list_mvp_scenarios_missing_cii_weights",
        "list_cii_scenario_weights_with_negative_values",
        "list_cii_scenario_weights_exceeding_one",
        "list_mvp_scenarios_missing_cii_scores",
        "list_cii_scenario_scores_missing_formula_metadata",
        "list_inactive_mvp_scenarios",
        "list_cii_scores_with_non_geometric_aggregation",
        "list_cii_metric_definitions_without_polarity",
        "list_mvp_countries_without_legal_events",
        "list_published_routes_without_sources",
        "list_published_routes_missing_required_text",
        "list_published_routes_with_all_eligibility_unknown",
        "list_published_routes_without_documents",
        "list_route_source_country_mismatches",
        "list_route_evidence_country_mismatches",
        "list_published_routes_missing_legal_status",
        "list_published_routes_with_unknown_legal_status",
        "list_active_personas_missing_required_fields",
        "list_active_personas_missing_metric_modifiers",
        "list_persona_modifiers_out_of_range",
        "list_inactive_personas_with_modifiers",
        "list_active_personas_missing_descriptions",
        "list_persona_adjusted_weight_inputs",
        "list_enabled_feature_flags_without_access_rules",
        "list_disabled_feature_flags_without_access_rules",
        "list_data_journal_events_with_internal_payload_fields",
        "list_data_journal_events_referencing_non_public_content",
        "list_invalid_platform_metric_values",
        "list_inconsistent_insufficient_data_metrics",
        "list_platform_metrics_with_missing_methodology",
        "list_platform_metrics_with_missing_computed_at",
        "list_stale_platform_metrics",
        "list_high_confidence_low_sample_metrics",
        "list_mvp_countries_missing_global_platform_metrics",
        "list_mvp_countries_missing_scenario_risk_metrics",
        "list_invalid_trust_score_values",
        "list_inconsistent_trust_insufficient_data",
        "list_stale_trust_scores",
        "list_missing_required_methodology_sections",
        "list_missing_required_glossary_terms",
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


def test_data_quality_report_detects_invalid_timeline_data(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_without_timeline_event",
        lambda *_: [{"id": "signal-id", "country_slug": "russia"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_timeline_events_without_traceability",
        lambda *_: [{"id": "event-id", "legal_signal_id": "signal-id"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_unplanned_future_timeline_events",
        lambda *_: [{"id": "future-id", "event_date": "2100-01-01"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert {issue.code for issue in report.issues} == {
        "published_legal_signal_timeline_event_missing",
        "timeline_event_traceability_missing",
        "timeline_event_future_date",
    }
    assert report.valid is False


def test_data_quality_report_enforces_source_backed_depth(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_with_too_few_published_sources",
        lambda *_: [
            {
                "id": "country-id",
                "slug": "russia",
                "published_sources_count": 14,
                "required_sources_count": 15,
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_with_too_few_published_evidence",
        lambda *_: [
            {
                "id": "country-id",
                "slug": "russia",
                "published_evidence_count": 19,
                "required_evidence_count": 20,
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_with_too_few_published_legal_signals",
        lambda *_: [
            {
                "id": "country-id",
                "slug": "russia",
                "published_legal_signals_count": 7,
                "required_legal_signals_count": 8,
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_sources_with_example_invalid_url",
        lambda *_: [
            {
                "id": "source-id",
                "title": "Synthetic source",
                "url": "https://example.invalid/source",
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_score_breakdowns_without_source_ids",
        lambda *_: [
            {
                "id": "breakdown-id",
                "country_score_id": "score-id",
                "country_slug": "russia",
                "scenario_slug": "relocation_residence",
                "criterion": "legalization_score",
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_country_cards_with_demo_source_summary",
        lambda *_: [
            {
                "id": "card-id",
                "country_slug": "russia",
                "locale": "en",
                "source_summary": "Demo source summary",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {issue.code for issue in report.issues} == {
        "mvp_country_published_source_count_low",
        "mvp_country_published_evidence_count_low",
        "mvp_country_published_legal_signal_count_low",
        "published_source_example_invalid_url",
        "score_breakdown_source_ids_missing",
        "country_card_source_summary_demo",
    }
    assert report.critical_issues_count == 3
    assert report.warnings_count == 3
    assert {
        issue.severity
        for issue in report.issues
        if issue.code.startswith("mvp_country_published_")
    } == {"accepted_mvp_warning"}


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

    result = admin_route.admin_read_data_quality_report(CONNECTION, "admin")

    assert result.valid is True
    assert result.issues == []


def test_openapi_has_admin_data_quality_report() -> None:
    contract = load_contract()

    assert "/api/v1/admin/data-quality/report" in contract["paths"]
    assert "DataQualityIssue" in contract["components"]["schemas"]
    assert "DataQualityReport" in contract["components"]["schemas"]


def test_data_quality_report_detects_missing_cii(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_missing_cii",
        lambda *_: [{"country_slug": "russia"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(issue.code == "cii_score_missing" for issue in report.issues)
    assert any(issue.severity == "critical" for issue in report.issues)


def test_data_quality_report_detects_missing_formula_metadata(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_cii_scores_missing_formula_metadata",
        lambda *_: [
            {
                "country_slug": "uruguay",
                "version": "v1.0",
                "formula_version": None,
                "aggregation_method": None,
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(issue.code == "cii_formula_metadata_missing" for issue in report.issues)


def test_data_quality_report_detects_invalid_weight_sum(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_cii_metric_weights_with_invalid_sum",
        lambda *_: [{"version": "v1.0", "weight_sum": 1.2}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(issue.code == "cii_weight_sum_invalid" for issue in report.issues)


def test_data_quality_report_detects_missing_metric_values(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_metrics_missing_values",
        lambda *_: [{"country_slug": "russia", "metric_slug": "safety"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(issue.code == "cii_metric_value_missing" for issue in report.issues)


def test_data_quality_report_detects_score_out_of_range(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_cii_scores_out_of_range",
        lambda *_: [
            {"country_slug": "russia", "version": "v1.0", "overall_score": 150.0}
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(issue.code == "cii_score_out_of_range" for issue in report.issues)

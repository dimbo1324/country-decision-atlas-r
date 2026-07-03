"""Data-quality checks for decision personalization: feature-flag mismatches and missing criteria/dependencies."""

from app.repositories import data_quality as repository
from app.services import data_quality, decision_criteria
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_decision_personalization_dq_detects_feature_flag_mismatch(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_decision_personalization_feature_flag_mismatches",
        lambda *_: [{"feature_key": "decision_wizard_enabled", "status": "disabled"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is False
    assert "decision_personalization_feature_flag_invalid" in {
        issue.code for issue in report.issues
    }


def test_decision_personalization_dq_detects_missing_criterion(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_decision_scores_missing_required_criteria",
        lambda *_: [
            {
                "country_slug": "uruguay",
                "scenario_slug": "relocation_residence",
                "criterion": "safety_score",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is False
    assert "decision_score_required_criterion_missing" in {
        issue.code for issue in report.issues
    }


def test_decision_personalization_dq_detects_missing_wizard_dependency(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_decision_wizard_rule_mismatches",
        lambda *_: [
            {
                "dependency_type": "persona",
                "dependency_slug": "family",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is False
    assert "decision_wizard_dependency_missing" in {
        issue.code for issue in report.issues
    }


def test_decision_personalization_dq_checks_are_present(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert {
        "decision_personalization_feature_flags_enabled",
        "decision_scores_include_personalization_criteria",
        "decision_wizard_rules_have_active_dependencies",
        "decision_criteria_registry_complete",
    }.issubset({check.code for check in report.checks})


def test_decision_criteria_registry_has_required_labels() -> None:
    assert len(decision_criteria.DECISION_CRITERIA) == 7
    assert set(decision_criteria.DECISION_CRITERIA) == set(
        decision_criteria.DECISION_CRITERIA_BY_SLUG
    )
    for definition in decision_criteria.DECISION_CRITERION_DEFINITIONS:
        assert definition.label_ru
        assert definition.label_en


def test_decision_personalization_dq_detects_invalid_criterion_metadata(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        decision_criteria,
        "list_decision_criterion_metadata_issues",
        lambda: [{"criterion": "safety_score", "reason": "missing_label_ru"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "decision_criterion_metadata_invalid" in {
        issue.code for issue in report.issues
    }

"""Data-quality checks for platform runtime configuration: flag/rule mismatches and internal-journal payload rules."""

from app.repositories import data_quality as repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_platform_runtime_dq_detects_enabled_flag_without_rule(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_enabled_feature_flags_without_access_rules",
        lambda *_: [{"key": "data_journal_enabled", "status": "enabled"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is False
    assert "enabled_feature_flag_without_access_rule" in {
        issue.code for issue in report.issues
    }


def test_platform_runtime_dq_detects_internal_journal_payload(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        repository,
        "list_data_journal_events_with_internal_payload_fields",
        lambda *_: [{"id": "event-id", "event_type": "route.published"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is False
    assert "data_journal_internal_payload_field" in {
        issue.code for issue in report.issues
    }


def test_platform_runtime_dq_cache_config_check_is_present(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert "cache_config_is_safe" in {check.code for check in report.checks}

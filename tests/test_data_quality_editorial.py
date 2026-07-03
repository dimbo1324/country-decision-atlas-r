"""Data-quality checks for the editorial publication lifecycle: legal status and required-field validation."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_legal_status_unknown_for_published_signal_is_warning(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_with_unknown_legal_status",
        lambda *_: [{"id": "signal-id", "title": "Signal", "legal_status": "unknown"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is True
    assert report.warnings_count == 1
    assert report.issues[0].code == "published_legal_signal_legal_status_unknown"
    assert report.issues[0].severity == "warning"


def test_missing_legal_status_for_published_signal_is_critical(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_with_missing_legal_status",
        lambda *_: [{"id": "signal-id", "title": "Signal", "legal_status": ""}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert report.issues[0].code == "published_legal_signal_legal_status_missing"
    assert report.issues[0].severity == "critical"


def test_review_source_without_required_fields_is_found(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_review_sources_with_missing_required_fields",
        lambda *_: [{"id": "source-id", "title": "", "missing_field": "title"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert report.issues[0].code == "review_source_required_field_missing"


def test_review_legal_signal_without_required_fields_is_found(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_review_legal_signals_with_missing_required_fields",
        lambda *_: [{"id": "signal-id", "title": "", "missing_field": "source_id"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert report.issues[0].code == "review_legal_signal_required_field_missing"


def test_published_invalid_content_is_found(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_evidence_items_with_missing_required_fields",
        lambda *_: [{"id": "evidence-id", "missing_field": "source_id"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_legal_signals_with_missing_required_fields",
        lambda *_: [{"id": "signal-id", "missing_field": "impact_level"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {issue.code for issue in report.issues} == {
        "published_evidence_validation_failed",
        "published_legal_signal_validation_failed",
    }


def test_invalid_domain_event_is_found(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_domain_events_for_dq",
        lambda *_: [{"id": "event-id", "event_key": "", "payload": None}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert report.issues[0].code == "domain_event_invalid"


def test_clean_editorial_foundation_report_has_no_critical(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is True
    assert report.critical_issues_count == 0
    assert "domain_events_no_historical_notification_storm" in {
        check.code for check in report.checks
    }


def test_legitimate_pending_domain_event_does_not_fail_historical_storm_check(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)

    checks = {check.code: check.status for check in report.checks}
    assert checks["domain_events_no_historical_notification_storm"] == "passed"

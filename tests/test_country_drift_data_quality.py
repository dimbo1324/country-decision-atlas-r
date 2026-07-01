from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_clean_drift_surface_produces_no_critical_issues(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is True
    drift_codes = {i.code for i in report.issues if "drift" in i.code}
    assert drift_codes == set()


def test_missing_drift_snapshot_for_active_country_is_detected(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_countries_missing_drift_snapshots",
        lambda *_: [{"slug": "argentina"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_missing_for_active_country" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "drift_missing_for_active_country"
    )
    assert report.valid is False


def test_invalid_drift_label_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_drift_snapshot_values",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "russia",
                "label": "skyrocketing",
                "confidence": "medium",
                "net_score": 50.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_value_invalid" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "drift_value_invalid"
    )
    assert report.valid is False


def test_invalid_drift_confidence_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_drift_snapshot_values",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "russia",
                "label": "stable",
                "confidence": "certain",
                "net_score": 5.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_value_invalid" for i in report.issues)


def test_invalid_drift_net_score_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_drift_snapshot_values",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "russia",
                "label": "positive",
                "confidence": "high",
                "net_score": 150.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_value_invalid" for i in report.issues)


def test_insufficient_data_inconsistency_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_snapshots_insufficient_data_inconsistent",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "uruguay",
                "label": "insufficient_data",
                "event_count": 10,
                "total_weight": 20.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_insufficient_data_inconsistent" for i in report.issues)
    assert report.valid is False


def test_insufficient_data_high_confidence_mismatch_is_detected(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_snapshots_insufficient_data_with_high_confidence",
        lambda *_: [
            {
                "id": "abc123",
                "country_slug": "uruguay",
                "label": "insufficient_data",
                "confidence": "medium",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(
        i.code == "drift_insufficient_data_confidence_mismatch" for i in report.issues
    )
    assert report.valid is False


def test_missing_methodology_version_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_snapshots_missing_methodology_version",
        lambda *_: [{"id": "abc123", "country_slug": "argentina"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_methodology_version_missing" for i in report.issues)
    assert report.valid is False


def test_missing_computed_at_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_snapshots_missing_computed_at",
        lambda *_: [{"id": "abc123", "country_slug": "argentina"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_computed_at_missing" for i in report.issues)
    assert report.valid is False


def test_non_object_input_summary_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_snapshots_with_non_object_input_summary",
        lambda *_: [{"id": "abc123", "country_slug": "argentina"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_input_summary_not_object" for i in report.issues)
    assert report.valid is False


def test_duplicate_drift_changed_event_key_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_duplicate_drift_changed_event_keys",
        lambda *_: [
            {
                "event_key": "country:argentina:drift.changed:2026-07-01:v1.0",
                "occurrences": 2,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_changed_event_key_duplicate" for i in report.issues)
    assert report.valid is False


def test_drift_changed_payload_missing_fields_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_drift_changed_events_missing_payload_fields",
        lambda *_: [
            {
                "id": "event-1",
                "event_key": "country:argentina:drift.changed:2026-07-01:v1.0",
                "payload": {"country_slug": "argentina"},
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "drift_changed_payload_incomplete" for i in report.issues)
    assert report.valid is False


def test_insufficient_data_alone_is_not_a_critical_issue(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_countries_missing_drift_snapshots",
        lambda *_: [],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    drift_codes = {i.code for i in report.issues if "drift" in i.code}
    assert drift_codes == set()
    assert report.valid is True

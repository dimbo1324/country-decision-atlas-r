from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_clean_platform_metrics_produces_no_critical_issues(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is True
    pm_codes = {i.code for i in report.issues if i.entity_type == "platform_metric"}
    assert pm_codes == set()


def test_missing_global_lvi_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_missing_global_platform_metrics",
        lambda *_: [
            {"country_slug": "russia", "missing_metric": "legal_velocity_index"}
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "platform_metric_global_missing" for i in report.issues)


def test_missing_contradiction_score_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_missing_global_platform_metrics",
        lambda *_: [
            {"country_slug": "uruguay", "missing_metric": "contradiction_score"}
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "platform_metric_global_missing" for i in report.issues)


def test_missing_ssrs_is_detected(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_mvp_countries_missing_scenario_risk_metrics",
        lambda *_: [
            {"country_slug": "russia", "scenario_slug": "relocation_residence"}
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "platform_metric_scenario_missing" for i in report.issues)


def test_invalid_metric_value_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_platform_metric_values",
        lambda *_: [
            {
                "id": "metric-1",
                "country_slug": "russia",
                "metric_key": "legal_velocity_index",
                "value": 150.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(i for i in report.issues if i.code == "platform_metric_value_invalid")
    assert issue.severity == "critical"
    assert report.valid is False


def test_insufficient_data_inconsistency_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_inconsistent_insufficient_data_metrics",
        lambda *_: [
            {
                "id": "metric-2",
                "country_slug": "russia",
                "metric_key": "legal_velocity_index",
                "label": "insufficient_data",
                "value": 55.0,
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        i
        for i in report.issues
        if i.code == "platform_metric_insufficient_data_inconsistent"
    )
    assert issue.severity == "critical"


def test_stale_metric_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_stale_platform_metrics",
        lambda *_: [
            {"id": "metric-3", "country_slug": "russia", "days_since_computed": 45}
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(i for i in report.issues if i.code == "platform_metric_stale")
    assert issue.severity == "warning"


def test_high_confidence_low_sample_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_high_confidence_low_sample_metrics",
        lambda *_: [
            {
                "id": "metric-4",
                "country_slug": "russia",
                "signal_count": 1,
                "event_count": 1,
                "confidence": "high",
            }
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        i
        for i in report.issues
        if i.code == "platform_metric_high_confidence_low_sample"
    )
    assert issue.severity == "warning"


def test_missing_methodology_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_platform_metrics_with_missing_methodology",
        lambda *_: [
            {"id": "metric-5", "country_slug": "russia", "methodology_version": None}
        ],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        i for i in report.issues if i.code == "platform_metric_methodology_missing"
    )
    assert issue.severity == "critical"


def test_missing_computed_at_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_platform_metrics_with_missing_computed_at",
        lambda *_: [{"id": "metric-6", "country_slug": "russia", "computed_at": None}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        i for i in report.issues if i.code == "platform_metric_computed_at_missing"
    )
    assert issue.severity == "critical"

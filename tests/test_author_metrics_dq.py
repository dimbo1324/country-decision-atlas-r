"""Data-quality checks for author metrics: methodology, source, scale, PII, and fork-lineage invariants."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_author_metrics_data_quality_checks_are_registered(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)
    check_codes = {check.code for check in report.checks}

    assert "author_metrics_published_have_methodology" in check_codes
    assert "author_metric_values_have_source_or_experience" in check_codes
    assert "author_metric_values_within_scale" in check_codes
    assert "author_metrics_public_text_has_no_pii" in check_codes
    assert "author_metric_fork_lineage_is_valid" in check_codes


def test_author_metrics_data_quality_detects_missing_methodology(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_author_metrics_without_methodology",
        lambda *_: [
            {"id": "metric-1", "methodology_en": "", "methodology_ru": ""}
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "author_metric_published_without_methodology" in {
        issue.code for issue in report.issues
    }


def test_author_metrics_data_quality_detects_value_and_scale_violations(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_author_metric_values_missing_source_or_experience",
        lambda *_: [{"id": "value-1"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_author_metric_values_out_of_scale",
        lambda *_: [
            {"id": "value-2", "value": 150, "scale_min": 0, "scale_max": 100}
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "author_metric_value_missing_source_or_experience",
        "author_metric_value_out_of_scale",
    }.issubset({issue.code for issue in report.issues})


def test_author_metrics_data_quality_detects_pii_and_dangling_fork(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_public_author_metrics_text",
        lambda *_: [
            {
                "id": "metric-3",
                "name_en": "Cost of Living",
                "name_ru": "Стоимость жизни",
                "methodology_en": "Contact me at author@example.com for details.",
                "methodology_ru": "",
            }
        ],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_author_metrics_with_dangling_fork_lineage",
        lambda *_: [{"id": "metric-4", "forked_from_id": "missing-1"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "author_metric_public_text_contains_pii",
        "author_metric_dangling_fork_lineage",
    }.issubset({issue.code for issue in report.issues})


def test_author_metrics_data_quality_ignores_clean_public_text(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_public_author_metrics_text",
        lambda *_: [
            {
                "id": "metric-5",
                "name_en": "Cost of Living",
                "name_ru": "Стоимость жизни",
                "methodology_en": "Computed from public statistics.",
                "methodology_ru": "Рассчитано из открытых данных.",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert "author_metric_public_text_contains_pii" not in {
        issue.code for issue in report.issues
    }

"""Data-quality checks for persona seed data and modifier coverage."""

import pytest
from app.repositories import data_quality as data_quality_repository
from app.services import data_quality, persona_weights
from fastapi import HTTPException
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _weight_rows(
    persona_slug: str = "family",
    scenario_slug: str = "relocation_residence",
    base_weight: float = 0.5,
) -> list[dict[str, Any]]:
    return [
        {
            "persona_slug": persona_slug,
            "scenario_slug": scenario_slug,
            "metric_id": "m1",
            "metric_slug": "rule_of_law",
            "metric_name": "Rule of Law",
            "base_weight": base_weight,
            "modifier": 0.0,
            "version": "v1.0",
        },
        {
            "persona_slug": persona_slug,
            "scenario_slug": scenario_slug,
            "metric_id": "m2",
            "metric_slug": "safety",
            "metric_name": "Safety",
            "base_weight": base_weight,
            "modifier": 0.0,
            "version": "v1.0",
        },
    ]


def _persona_issues(report: Any) -> list[Any]:
    return [
        issue for issue in report.issues if issue.code.startswith("persona_")
    ]


def test_persona_clean_seed_has_no_critical_issues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_persona_adjusted_weight_inputs",
        lambda *_: _weight_rows(),
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert [
        issue
        for issue in _persona_issues(report)
        if issue.severity == "critical"
    ] == []


def test_missing_persona_modifier_is_critical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_personas_missing_metric_modifiers",
        lambda *_: [
            {
                "persona_slug": "family",
                "metric_slug": "safety",
                "version": "v1.0",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue
        for issue in report.issues
        if issue.code == "persona_modifier_coverage"
    )

    assert issue.severity == "critical"
    assert issue.details["persona_slug"] == "family"
    assert issue.details["metric_slug"] == "safety"


def test_modifier_out_of_range_is_critical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_persona_modifiers_out_of_range",
        lambda *_: [
            {
                "persona_slug": "family",
                "metric_slug": "safety",
                "modifier": 0.8,
                "version": "v1.0",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue
        for issue in report.issues
        if issue.code == "persona_modifier_range"
    )

    assert issue.severity == "critical"
    assert issue.details["expected_range"] == [-0.5, 0.5]


def test_adjusted_weights_degenerate_is_critical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_persona_adjusted_weight_inputs",
        lambda *_: _weight_rows(base_weight=0.0),
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue
        for issue in report.issues
        if issue.code == "persona_adjusted_weights_valid"
    )

    assert issue.severity == "critical"
    assert issue.details["error_code"] == "persona_weights_degenerate"


@pytest.mark.parametrize("missing_field", ["name", "name_ru"])
def test_missing_required_persona_field_is_critical(
    monkeypatch: pytest.MonkeyPatch,
    missing_field: str,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_personas_missing_required_fields",
        lambda *_: [{"persona_slug": "family", "missing_field": missing_field}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue
        for issue in report.issues
        if issue.code == "persona_required_fields"
    )

    assert issue.severity == "critical"
    assert issue.details["missing_field"] == missing_field


@pytest.mark.parametrize("missing_field", ["description", "description_ru"])
def test_missing_persona_description_is_warning(
    monkeypatch: pytest.MonkeyPatch,
    missing_field: str,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_personas_missing_descriptions",
        lambda *_: [{"persona_slug": "family", "missing_field": missing_field}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue for issue in report.issues if issue.code == "persona_descriptions"
    )

    assert issue.severity == "warning"
    assert issue.details["missing_field"] == missing_field


def test_inactive_persona_modifiers_is_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_inactive_personas_with_modifiers",
        lambda *_: [
            {
                "persona_slug": "retired_profile",
                "modifier_count": 6,
                "version": "v1.0",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issue = next(
        issue
        for issue in report.issues
        if issue.code == "inactive_persona_modifiers"
    )

    assert issue.severity == "warning"
    assert issue.details["modifier_count"] == 6


def test_dq_uses_persona_weight_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    install_clean_report_fakes(monkeypatch)
    calls: list[list[dict[str, Any]]] = []
    monkeypatch.setattr(
        data_quality_repository,
        "list_persona_adjusted_weight_inputs",
        lambda *_: _weight_rows(),
    )

    def fake_build_adjusted_weights(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        calls.append(rows)
        return [{**row, "adjusted_weight": 0.5} for row in rows]

    monkeypatch.setattr(
        persona_weights,
        "build_adjusted_weights",
        fake_build_adjusted_weights,
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert calls
    assert _persona_issues(report) == []


def test_one_broken_persona_scenario_pair_does_not_abort_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    rows = [
        *_weight_rows("family", "relocation_residence"),
        *_weight_rows("entrepreneur", "business_self_employment"),
    ]
    monkeypatch.setattr(
        data_quality_repository,
        "list_persona_adjusted_weight_inputs",
        lambda *_: rows,
    )

    def fake_build_adjusted_weights(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if rows[0]["persona_slug"] == "family":
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "persona_weights_degenerate",
                        "message": "Broken",
                    }
                },
            )
        return [{**row, "adjusted_weight": 0.5} for row in rows]

    monkeypatch.setattr(
        persona_weights,
        "build_adjusted_weights",
        fake_build_adjusted_weights,
    )

    report = data_quality.build_data_quality_report(CONNECTION)
    issues = [
        issue
        for issue in report.issues
        if issue.code == "persona_adjusted_weights_valid"
    ]

    assert len(issues) == 1
    assert issues[0].details["persona_slug"] == "family"
    assert issues[0].details["error_code"] == "persona_weights_degenerate"

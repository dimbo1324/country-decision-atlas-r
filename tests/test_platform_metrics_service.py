"""Platform metrics service: building LVI/contradiction/SSRS metrics across global and scenario scopes."""

import pytest
from app.repositories import platform_metrics as repository
from app.services import platform_metrics
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock


COUNTRY = {"id": "country-1", "slug": "russia"}
SCENARIOS = [
    {"slug": "relocation_residence"},
    {"slug": "permanent_residence_citizenship"},
    {"slug": "low_budget_living"},
    {"slug": "business_self_employment"},
    {"slug": "safety_political_risk"},
]


def legal_event(index: int) -> dict[str, Any]:
    return {
        "event_id": f"event-{index}",
        "event_date": date.today() - timedelta(days=index),
        "impact_direction": "negative",
        "impact_level": "medium",
        "signal_type": "migration",
        "affected_groups": ["migrants"],
        "source_id": f"source-{index}",
        "evidence_item_id": f"evidence-{index}",
    }


def risk_signal(index: int, scenario_slug: str) -> dict[str, Any]:
    signal_type = {
        "relocation_residence": "migration",
        "permanent_residence_citizenship": "citizenship",
        "low_budget_living": "cost_of_living",
        "business_self_employment": "business",
        "safety_political_risk": "safety",
    }[scenario_slug]
    return {
        "signal_id": f"signal-{scenario_slug}-{index}",
        "event_id": f"event-{scenario_slug}-{index}",
        "event_date": date.today() - timedelta(days=index),
        "signal_type": signal_type,
        "impact_direction": "negative",
        "impact_level": "medium",
        "affected_groups": ["migrants"],
        "source_id": f"source-{scenario_slug}-{index}",
        "evidence_item_id": f"evidence-{scenario_slug}-{index}",
    }


def contradiction_row(index: int) -> dict[str, Any]:
    return {
        "signal_id": f"signal-{index}",
        "event_id": f"event-{index}",
        "signal_type": "migration" if index < 3 else "tax",
        "affected_groups": ["migrants"] if index < 3 else ["tax"],
        "impact_direction": "positive" if index % 2 else "negative",
        "impact_level": "high",
        "source_type": "official" if index % 2 else "media",
        "source_id": f"source-{index}",
        "evidence_item_id": f"evidence-{index}",
        "confidence": "medium",
    }


def patch_repository(
    monkeypatch: pytest.MonkeyPatch, stored: list[dict[str, Any]]
) -> None:
    monkeypatch.setattr(repository, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        repository, "list_active_countries", lambda *_a: [COUNTRY]
    )
    monkeypatch.setattr(
        repository, "list_active_mvp_scenarios", lambda *_a: SCENARIOS
    )
    monkeypatch.setattr(
        repository,
        "list_legal_velocity_events",
        lambda *_a: [legal_event(index) for index in range(1, 4)],
    )
    monkeypatch.setattr(
        repository,
        "list_scenario_risk_inputs",
        lambda _c, _country_id, scenario_slug, _w: [
            risk_signal(index, scenario_slug) for index in range(1, 3)
        ],
    )
    monkeypatch.setattr(
        repository,
        "list_contradiction_inputs",
        lambda *_a: [contradiction_row(index) for index in range(1, 5)],
    )
    monkeypatch.setattr(
        repository, "upsert_country_platform_metric", _append(stored)
    )


def _append(
    stored: list[dict[str, Any]],
) -> Any:
    def append_row(
        _connection: Any,
        country_id: str,
        metric_key: str,
        scenario_slug: str | None,
        value: Decimal | None,
        label: str,
        confidence: str,
        freshness_status: str,
        window_days: int,
        methodology_version: str,
        input_summary: dict[str, Any],
        source_count: int,
        evidence_count: int,
        signal_count: int,
        event_count: int,
    ) -> dict[str, Any]:
        stored.append(
            {
                "country_id": country_id,
                "metric_key": metric_key,
                "scenario_slug": scenario_slug,
                "value": value,
                "label": label,
                "confidence": confidence,
                "freshness_status": freshness_status,
                "window_days": window_days,
                "methodology_version": methodology_version,
                "input_summary": input_summary,
                "source_count": source_count,
                "evidence_count": evidence_count,
                "signal_count": signal_count,
                "event_count": event_count,
            }
        )
        return stored[-1]

    return append_row


def test_compute_country_platform_metrics_builds_lvi_contradiction_and_ssrs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    results = platform_metrics.compute_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert [result.metric_key for result in results].count(
        "legal_velocity_index"
    ) == 1
    assert [result.metric_key for result in results].count(
        "contradiction_score"
    ) == 1
    assert [result.metric_key for result in results].count(
        "scenario_specific_risk_score"
    ) == 5


def test_returns_global_and_scenario_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    results = platform_metrics.compute_country_platform_metrics(
        MagicMock(), "russia"
    )
    global_results = [
        result for result in results if result.scenario_slug == "__global__"
    ]
    scenario_results = [
        result for result in results if result.scenario_slug != "__global__"
    ]
    assert len(global_results) == 2
    assert {result.scenario_slug for result in scenario_results} == {
        row["slug"] for row in SCENARIOS
    }


def test_output_count_correct_for_mvp_scenarios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    assert (
        len(
            platform_metrics.compute_country_platform_metrics(
                MagicMock(), "russia"
            )
        )
        == 7
    )


def test_insufficient_data_metrics_are_included(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    monkeypatch.setattr(
        repository, "list_legal_velocity_events", lambda *_a: []
    )
    results = platform_metrics.compute_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert any(result.label == "insufficient_data" for result in results)
    assert len(results) == 7


def test_all_computations_have_methodology_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    results = platform_metrics.compute_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert {result.methodology_version for result in results} == {"v1.0"}


def test_values_are_between_zero_and_100_or_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    results = platform_metrics.compute_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert all(
        result.value is None or Decimal("0") <= result.value <= Decimal("100")
        for result in results
    )


def test_compute_and_store_country_platform_metrics_upserts_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    result = platform_metrics.compute_and_store_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert len(result) == 7
    assert len(stored) == 7


def test_repeated_compute_and_store_does_not_duplicate_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    patch_repository(monkeypatch, stored)
    monkeypatch.setattr(
        repository, "upsert_country_platform_metric", _upsert(unique)
    )
    platform_metrics.compute_and_store_country_platform_metrics(
        MagicMock(), "russia"
    )
    platform_metrics.compute_and_store_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert len(unique) == 7


def _upsert(
    unique: dict[tuple[str, str, str, str], dict[str, Any]],
) -> Any:
    def upsert(
        _connection: Any,
        country_id: str,
        metric_key: str,
        scenario_slug: str | None,
        value: Decimal | None,
        label: str,
        confidence: str,
        freshness_status: str,
        window_days: int,
        methodology_version: str,
        input_summary: dict[str, Any],
        source_count: int,
        evidence_count: int,
        signal_count: int,
        event_count: int,
    ) -> dict[str, Any]:
        key = (
            country_id,
            metric_key,
            scenario_slug or "__global__",
            methodology_version,
        )
        unique[key] = {
            "country_id": country_id,
            "metric_key": metric_key,
            "scenario_slug": scenario_slug,
            "value": value,
            "label": label,
            "confidence": confidence,
            "freshness_status": freshness_status,
            "window_days": window_days,
            "methodology_version": methodology_version,
            "input_summary": input_summary,
            "source_count": source_count,
            "evidence_count": evidence_count,
            "signal_count": signal_count,
            "event_count": event_count,
        }
        return unique[key]

    return upsert


def test_compute_and_store_all_handles_all_active_countries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    monkeypatch.setattr(
        repository,
        "list_active_countries",
        lambda *_a: [
            {"id": "country-1", "slug": "russia"},
            {"id": "country-2", "slug": "uruguay"},
        ],
    )
    result = platform_metrics.compute_and_store_all_country_platform_metrics(
        MagicMock()
    )
    assert len(result) == 14


def test_cii_and_decision_tables_are_not_modified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored: list[dict[str, Any]] = []
    patch_repository(monkeypatch, stored)
    platform_metrics.compute_and_store_country_platform_metrics(
        MagicMock(), "russia"
    )
    assert all(row["metric_key"] != "country_cii_scores" for row in stored)
    assert all(row["metric_key"] != "country_scores" for row in stored)

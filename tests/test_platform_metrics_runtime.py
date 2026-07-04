"""Platform metrics runtime computation: per-country and batch recompute, idempotency, and dry-run mode."""

import pytest
from app.repositories import (
    feature_flags as ff_repo,
    platform_metrics as pm_repo,
)
from app.services import platform_metrics as pm_service
from app.services.platform_metric_types import (
    METHODOLOGY_VERSION,
    PlatformMetricComputation,
)
from app.services.platform_metrics_runtime import (
    compute_one_platform_metric,
    compute_platform_metrics_for_all_countries,
    compute_platform_metrics_for_country,
)
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock


COUNTRY = {"id": "country-1", "slug": "russia"}
COUNTRIES = [
    {"id": "country-1", "slug": "russia"},
    {"id": "country-2", "slug": "uruguay"},
    {"id": "country-3", "slug": "argentina"},
]

COMPUTATION_LVI = PlatformMetricComputation(
    metric_key="legal_velocity_index",
    scenario_slug="__global__",
    value=Decimal("45.0"),
    label="moderate",
    confidence="medium",
    freshness_status="fresh",
    window_days=365,
    methodology_version=METHODOLOGY_VERSION,
    input_summary={"event_count": 3},
    source_count=2,
    evidence_count=2,
    signal_count=3,
    event_count=3,
)

COMPUTATION_CONTRADICTION = PlatformMetricComputation(
    metric_key="contradiction_score",
    scenario_slug="__global__",
    value=Decimal("30.0"),
    label="low",
    confidence="medium",
    freshness_status="fresh",
    window_days=365,
    methodology_version=METHODOLOGY_VERSION,
    input_summary={"signal_count": 4},
    source_count=2,
    evidence_count=2,
    signal_count=4,
    event_count=0,
)

COMPUTATION_SSRS = PlatformMetricComputation(
    metric_key="scenario_specific_risk_score",
    scenario_slug="relocation_residence",
    value=Decimal("60.0"),
    label="elevated",
    confidence="medium",
    freshness_status="fresh",
    window_days=365,
    methodology_version=METHODOLOGY_VERSION,
    input_summary={"signal_count": 2},
    source_count=1,
    evidence_count=1,
    signal_count=2,
    event_count=0,
)


def _seven_computations() -> list[PlatformMetricComputation]:
    scenarios = [
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ]
    result = [COMPUTATION_LVI, COMPUTATION_CONTRADICTION]
    for s in scenarios:
        result.append(
            PlatformMetricComputation(
                metric_key="scenario_specific_risk_score",
                scenario_slug=s,
                value=Decimal("50.0"),
                label="moderate",
                confidence="medium",
                freshness_status="fresh",
                window_days=365,
                methodology_version=METHODOLOGY_VERSION,
                input_summary={},
                source_count=1,
                evidence_count=1,
                signal_count=2,
                event_count=0,
            )
        )
    return result


def _install_feature_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )


def _install_feature_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "disabled",
            "access_tier": "public",
            "default_enabled": False,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": False}],
    )


def test_compute_country_writes_expected_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: _seven_computations(),
    )
    stored: list[dict[str, Any]] = []

    def fake_upsert(*args: Any, **_kwargs: Any) -> dict[str, Any]:
        stored.append({"metric_key": args[2]})
        return {}

    monkeypatch.setattr(pm_repo, "upsert_country_platform_metric", fake_upsert)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(conn, "russia")
    assert result.feature_enabled is True
    assert result.metrics_computed == 7
    assert result.metrics_written == 7
    assert result.metrics_failed == 0
    assert result.errors == []


def test_compute_all_writes_expected_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "list_active_countries", lambda *_a: COUNTRIES)
    monkeypatch.setattr(
        pm_repo,
        "get_country_by_slug",
        lambda _conn, slug: next(c for c in COUNTRIES if c["slug"] == slug),
    )
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: _seven_computations(),
    )
    monkeypatch.setattr(
        pm_repo, "upsert_country_platform_metric", lambda *_a, **_kw: {}
    )
    conn = MagicMock()
    result = compute_platform_metrics_for_all_countries(conn)
    assert result.feature_enabled is True
    assert result.countries_requested == 3
    assert result.countries_processed == 3
    assert result.metrics_computed == 21
    assert result.metrics_written == 21
    assert result.metrics_failed == 0


def test_repeated_recompute_does_not_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: [COMPUTATION_LVI],
    )
    call_count = [0]

    def fake_upsert(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        call_count[0] += 1
        return {}

    monkeypatch.setattr(pm_repo, "upsert_country_platform_metric", fake_upsert)
    conn = MagicMock()
    compute_platform_metrics_for_country(conn, "russia")
    compute_platform_metrics_for_country(conn, "russia")
    assert call_count[0] == 2


def test_dry_run_does_not_write(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: _seven_computations(),
    )
    upsert_called = [False]

    def fake_upsert(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        upsert_called[0] = True
        return {}

    monkeypatch.setattr(pm_repo, "upsert_country_platform_metric", fake_upsert)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(conn, "russia", dry_run=True)
    assert result.metrics_computed == 7
    assert result.metrics_written == 0
    assert upsert_called[0] is False


def test_unknown_country_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: None)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(conn, "unknown-country")
    assert result.metrics_computed == 0
    assert "country_not_found" in result.errors


def test_invalid_metric_key_returns_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(
        conn, "russia", metric_key="bad_key"
    )
    assert "platform_metric_invalid_key: bad_key" in result.errors


def test_invalid_scenario_slug_returns_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(
        conn, "russia", scenario_slug="bad_scenario"
    )
    assert "platform_metric_invalid_scenario: bad_scenario" in result.errors


def test_feature_disabled_returns_disabled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_disabled(monkeypatch)
    conn = MagicMock()
    result = compute_platform_metrics_for_country(conn, "russia")
    assert result.feature_enabled is False
    assert "self_computed_intelligence_disabled" in result.errors


def test_one_failed_country_in_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "list_active_countries", lambda *_a: [COUNTRY])
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: _seven_computations(),
    )

    call_count = [0]

    def failing_upsert(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        call_count[0] += 1
        raise RuntimeError("db error")

    monkeypatch.setattr(
        pm_repo, "upsert_country_platform_metric", failing_upsert
    )
    conn = MagicMock()
    summary = compute_platform_metrics_for_all_countries(conn)
    assert summary.metrics_failed == 7
    assert len(summary.errors) > 0


def test_all_persisted_metrics_have_methodology_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: _seven_computations(),
    )
    written: list[str] = []

    def capture_upsert(
        _conn: Any,
        _country_id: Any,
        _metric_key: Any,
        _scenario_slug: Any,
        _value: Any,
        _label: Any,
        _confidence: Any,
        _freshness: Any,
        _window_days: Any,
        methodology_version: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        written.append(methodology_version)
        return {}

    monkeypatch.setattr(
        pm_repo, "upsert_country_platform_metric", capture_upsert
    )
    conn = MagicMock()
    compute_platform_metrics_for_country(conn, "russia")
    assert all(v == METHODOLOGY_VERSION for v in written)
    assert len(written) == 7


def test_compute_one_metric_filters_correctly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY)
    computations = _seven_computations()
    monkeypatch.setattr(
        pm_service,
        "compute_country_platform_metrics",
        lambda *_a, **_kw: computations,
    )
    written: list[str] = []

    def capture_upsert(
        _conn: Any,
        _country_id: Any,
        metric_key: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        written.append(metric_key)
        return {}

    monkeypatch.setattr(
        pm_repo, "upsert_country_platform_metric", capture_upsert
    )
    conn = MagicMock()
    result = compute_one_platform_metric(conn, "russia", "legal_velocity_index")
    assert result.metrics_written == 1
    assert all(k == "legal_velocity_index" for k in written)

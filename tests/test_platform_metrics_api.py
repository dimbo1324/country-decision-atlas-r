"""Platform metrics API: listing, pre-recompute empty state, feature-disabled and unknown-country errors."""

from app.api.v1 import platform_metrics as pm_api
from app.core.auth import CurrentUser
from app.repositories import feature_flags as ff_repo, platform_metrics as pm_repo
from app.schemas.platform_metrics import (
    PlatformMetricsRecomputeResult,
    PlatformMetricsRecomputeSummary,
)
from app.services.platform_metric_types import METHODOLOGY_VERSION
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock
import yaml


CONNECTION = cast(Connection[Any], object())

ADMIN_USER = CurrentUser(
    id="admin-id",
    email="admin@example.local",
    display_name="Admin",
    role="admin",
    status="active",
)

COUNTRY_ROW = {"id": "country-1", "slug": "russia"}

METRIC_ROW = {
    "country_slug": "russia",
    "metric_key": "legal_velocity_index",
    "scenario_slug": "__global__",
    "value": Decimal("45.0"),
    "label": "moderate",
    "confidence": "medium",
    "freshness_status": "fresh",
    "window_days": 365,
    "methodology_version": METHODOLOGY_VERSION,
    "input_summary": {"event_count": 3},
    "source_count": 2,
    "evidence_count": 2,
    "signal_count": 3,
    "event_count": 3,
    "computed_at": datetime(2026, 6, 30, tzinfo=UTC),
    "expires_at": None,
}

SSRS_ROW = {
    "country_slug": "russia",
    "metric_key": "scenario_specific_risk_score",
    "scenario_slug": "relocation_residence",
    "value": Decimal("60.0"),
    "label": "elevated",
    "confidence": "medium",
    "freshness_status": "fresh",
    "window_days": 365,
    "methodology_version": METHODOLOGY_VERSION,
    "input_summary": {"signal_count": 2},
    "source_count": 1,
    "evidence_count": 1,
    "signal_count": 2,
    "event_count": 0,
    "computed_at": datetime(2026, 6, 30, tzinfo=UTC),
    "expires_at": None,
}

CONTRADICTION_ROW = {
    "country_slug": "russia",
    "metric_key": "contradiction_score",
    "scenario_slug": "__global__",
    "value": Decimal("30.0"),
    "label": "low",
    "confidence": "medium",
    "freshness_status": "fresh",
    "window_days": 365,
    "methodology_version": METHODOLOGY_VERSION,
    "input_summary": {"signal_count": 4},
    "source_count": 2,
    "evidence_count": 2,
    "signal_count": 4,
    "event_count": 0,
    "computed_at": datetime(2026, 6, 30, tzinfo=UTC),
    "expires_at": None,
}


def install_feature_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
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


def install_feature_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_list_metrics_for_russia_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(
        pm_repo,
        "list_country_platform_metrics",
        lambda *_a: [METRIC_ROW, CONTRADICTION_ROW],
    )
    result = pm_api.list_country_platform_metrics(
        "russia", CONNECTION, scenario=None, locale=None, include_input_summary=True
    )
    assert result.country_slug == "russia"
    assert len(result.items) == 2


def test_list_metrics_before_recompute_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "list_country_platform_metrics", lambda *_a: [])
    result = pm_api.list_country_platform_metrics(
        "russia", CONNECTION, scenario=None, locale=None, include_input_summary=True
    )
    assert result.items == []


def test_list_metrics_feature_disabled_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_disabled(monkeypatch)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        pm_api.list_country_platform_metrics(
            "russia", CONNECTION, scenario=None, locale=None, include_input_summary=True
        )
    assert exc_info.value.status_code == 403


def test_list_metrics_unknown_country_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: None)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        pm_api.list_country_platform_metrics(
            "nonexistent",
            CONNECTION,
            scenario=None,
            locale=None,
            include_input_summary=True,
        )
    assert exc_info.value.status_code == 404


def test_list_metrics_invalid_scenario_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        pm_api.list_country_platform_metrics(
            "russia",
            CONNECTION,
            scenario="bad_scenario",
            locale=None,
            include_input_summary=True,
        )
    assert exc_info.value.status_code == 422


def test_get_lvi_detail_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "get_country_platform_metric", lambda *_a: METRIC_ROW)
    result = pm_api.get_country_platform_metric(
        "russia",
        "legal_velocity_index",
        CONNECTION,
        scenario=None,
        locale=None,
        include_input_summary=True,
    )
    assert result.item.metric_key == "legal_velocity_index"
    assert result.item.scenario_slug is None


def test_get_contradiction_score_detail_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(
        pm_repo, "get_country_platform_metric", lambda *_a: CONTRADICTION_ROW
    )
    result = pm_api.get_country_platform_metric(
        "russia",
        "contradiction_score",
        CONNECTION,
        scenario=None,
        locale=None,
        include_input_summary=True,
    )
    assert result.item.metric_key == "contradiction_score"


def test_get_ssrs_scenario_detail_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "get_country_platform_metric", lambda *_a: SSRS_ROW)
    result = pm_api.get_country_platform_metric(
        "russia",
        "scenario_specific_risk_score",
        CONNECTION,
        scenario="relocation_residence",
        locale=None,
        include_input_summary=True,
    )
    assert result.item.scenario_slug == "relocation_residence"


def test_global_scenario_slug_is_null_in_api(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "get_country_platform_metric", lambda *_a: METRIC_ROW)
    result = pm_api.get_country_platform_metric(
        "russia",
        "legal_velocity_index",
        CONNECTION,
        scenario=None,
        locale=None,
        include_input_summary=True,
    )
    assert result.item.scenario_slug is None


def test_include_input_summary_false_hides_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "get_country_platform_metric", lambda *_a: METRIC_ROW)
    result = pm_api.get_country_platform_metric(
        "russia",
        "legal_velocity_index",
        CONNECTION,
        scenario=None,
        locale=None,
        include_input_summary=False,
    )
    assert result.item.input_summary is None


def test_get_metric_not_found_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    monkeypatch.setattr(pm_repo, "get_country_platform_metric", lambda *_a: None)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        pm_api.get_country_platform_metric(
            "russia",
            "legal_velocity_index",
            CONNECTION,
            scenario=None,
            locale=None,
            include_input_summary=True,
        )
    assert exc_info.value.status_code == 404


def test_get_metric_invalid_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        pm_api.get_country_platform_metric(
            "russia",
            "bad_metric",
            CONNECTION,
            scenario=None,
            locale=None,
            include_input_summary=True,
        )
    assert exc_info.value.status_code == 422


def test_admin_recompute_all_writes_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    expected_summary = PlatformMetricsRecomputeSummary(
        feature_enabled=True,
        dry_run=False,
        countries_requested=3,
        countries_processed=3,
        countries_skipped=0,
        metrics_computed=21,
        metrics_written=21,
        metrics_failed=0,
    )
    monkeypatch.setattr(
        "app.api.v1.platform_metrics.compute_platform_metrics_for_all_countries",
        lambda *_a, **_kw: expected_summary,
    )
    from app.schemas.platform_metrics import PlatformMetricsRecomputeRequest

    conn = MagicMock()
    result = pm_api.admin_recompute_all_platform_metrics(
        PlatformMetricsRecomputeRequest(), conn, ADMIN_USER
    )
    assert result.metrics_written == 21


def test_admin_recompute_dry_run_writes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_feature_enabled(monkeypatch)
    dry_summary = PlatformMetricsRecomputeSummary(
        feature_enabled=True,
        dry_run=True,
        countries_requested=3,
        countries_processed=3,
        countries_skipped=0,
        metrics_computed=21,
        metrics_written=0,
        metrics_failed=0,
    )
    monkeypatch.setattr(
        "app.api.v1.platform_metrics.compute_platform_metrics_for_all_countries",
        lambda *_a, **_kw: dry_summary,
    )
    from app.schemas.platform_metrics import PlatformMetricsRecomputeRequest

    conn = MagicMock()
    result = pm_api.admin_recompute_all_platform_metrics(
        PlatformMetricsRecomputeRequest(dry_run=True), conn, ADMIN_USER
    )
    assert result.dry_run is True
    assert result.metrics_written == 0


def test_admin_recompute_one_country_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_feature_enabled(monkeypatch)
    monkeypatch.setattr(pm_repo, "get_country_by_slug", lambda *_a: COUNTRY_ROW)
    expected = PlatformMetricsRecomputeResult(
        feature_enabled=True,
        dry_run=False,
        country_slug="russia",
        metrics_computed=7,
        metrics_written=7,
        metrics_failed=0,
    )
    monkeypatch.setattr(
        "app.api.v1.platform_metrics.compute_platform_metrics_for_country",
        lambda *_a, **_kw: expected,
    )
    from app.schemas.platform_metrics import PlatformMetricsRecomputeRequest

    conn = MagicMock()
    result = pm_api.admin_recompute_country_platform_metrics(
        "russia", PlatformMetricsRecomputeRequest(), conn, ADMIN_USER
    )
    assert result.metrics_written == 7


def test_admin_recompute_feature_disabled_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_feature_disabled(monkeypatch)
    from app.schemas.platform_metrics import PlatformMetricsRecomputeRequest
    from fastapi import HTTPException

    conn = MagicMock()
    with pytest.raises(HTTPException) as exc_info:
        pm_api.admin_recompute_all_platform_metrics(
            PlatformMetricsRecomputeRequest(), conn, ADMIN_USER
        )
    assert exc_info.value.status_code == 403


def load_contract() -> dict[str, Any]:
    contract_path = Path("contracts/openapi.yaml")
    return cast(
        dict[str, Any], yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    )


def test_openapi_contract_contains_platform_metrics_endpoints() -> None:
    contract = load_contract()
    paths = set(contract["paths"])
    assert "/api/v1/countries/{country_slug}/platform-metrics" in paths
    assert "/api/v1/countries/{country_slug}/platform-metrics/{metric_key}" in paths
    assert "/api/v1/admin/platform-metrics/recompute" in paths
    assert "/api/v1/admin/platform-metrics/recompute/{country_slug}" in paths


def test_openapi_contract_contains_platform_metric_schema() -> None:
    contract = load_contract()
    schemas = contract["components"]["schemas"]
    assert "PlatformMetric" in schemas
    assert "PlatformMetricsRecomputeSummary" in schemas

"""Flexible methodology v1: migration, typed config, public parameter API, and DQ guardrails."""

import pytest
from app.api.v1 import methodology as methodology_api
from app.core.database import get_connection
from app.repositories import data_quality as data_quality_repository
from app.services import data_quality, methodology_config
from datetime import UTC, datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
MIGRATION = Path("database/migrations/046_flexible_methodology_v1.sql")
MIGRATION_SQL = MIGRATION.read_text(encoding="utf-8")
METHODOLOGY_SEED_SQL = (
    MIGRATION_SQL
    + Path("database/migrations/047_trip_planner_v1.sql").read_text(
        encoding="utf-8"
    )
    + Path("database/migrations/048_rights_capabilities.sql").read_text(
        encoding="utf-8"
    )
    + Path("database/migrations/049_author_metrics_v1.sql").read_text(
        encoding="utf-8"
    )
)
NOW = datetime(2026, 7, 4, tzinfo=UTC)


def _row(param_key: str, value: float) -> dict[str, Any]:
    return {
        "id": f"{param_key}-id",
        "version": "v1.0",
        "param_key": param_key,
        "value_numeric": value,
        "value_json": None,
        "description": f"{param_key} description",
        "effective_from": NOW,
        "created_at": NOW,
    }


def _rows(**overrides: float) -> list[dict[str, Any]]:
    values = {
        methodology_config.SCORE_LABEL_WEAK_BELOW: 30.0,
        methodology_config.SCORE_LABEL_LIMITED_BELOW: 50.0,
        methodology_config.SCORE_LABEL_MODERATE_BELOW: 70.0,
        methodology_config.SCORE_LABEL_STRONG_BELOW: 85.0,
        methodology_config.STRENGTH_MIN_SCORE: 70.0,
        methodology_config.WEAKNESS_MAX_SCORE: 50.0,
        methodology_config.CONFIDENCE_HIGH_MIN_AVERAGE: 2.5,
        methodology_config.CONFIDENCE_MEDIUM_MIN_AVERAGE: 1.7,
        methodology_config.RECOMMENDATION_TIE_DELTA_BELOW: 3.0,
        methodology_config.RECOMMENDATION_MEDIUM_CONFIDENCE_DELTA_BELOW: 10.0,
        methodology_config.BOARD_MAX_ACTIVE_POSTS: 5.0,
        methodology_config.BOARD_MAX_CONTACT_REQUESTS_PER_DAY: 20.0,
        methodology_config.BOARD_MAX_REPORTS_PER_DAY: 20.0,
        methodology_config.BOARD_AUTO_HIDE_REPORT_THRESHOLD: 3.0,
        methodology_config.FLOWS_K_ANONYMITY: 20.0,
        methodology_config.TRIP_WARNING_HIGH_IMPACT_MIN_RANK: 3.0,
        methodology_config.TRIP_WARNING_RESTRICTIVE_PAIR_SEVERITY_RANK: 3.0,
        methodology_config.TRIP_WARNING_MISSING_PAIR_SEVERITY_RANK: 2.0,
        methodology_config.AUTHOR_METRICS_MIN_METHODOLOGY_LENGTH: 120.0,
        methodology_config.AUTHOR_METRICS_MIN_COUNTRY_COVERAGE: 5.0,
    }
    values.update(overrides)
    return [_row(param_key, value) for param_key, value in values.items()]


def test_migration_creates_methodology_and_weight_profile_tables() -> None:
    assert "CREATE TABLE IF NOT EXISTS methodology_parameters" in MIGRATION_SQL
    assert "CREATE TABLE IF NOT EXISTS user_weight_profiles" in MIGRATION_SQL
    assert (
        "CONSTRAINT uq_methodology_param UNIQUE (version, param_key)"
        in MIGRATION_SQL
    )
    assert "CONSTRAINT uq_profile_name UNIQUE (user_id, name)" in MIGRATION_SQL


def test_migration_seeds_required_current_constants() -> None:
    for param_key in methodology_config.REQUIRED_NUMERIC_KEYS:
        assert f"'{param_key}'" in METHODOLOGY_SEED_SQL
    assert "'flows.k_anonymity'" in METHODOLOGY_SEED_SQL
    assert "20" in METHODOLOGY_SEED_SQL


def test_methodology_config_builds_typed_active_version() -> None:
    config = methodology_config.build_methodology_config("v1.0", _rows())

    assert config.version == "v1.0"
    assert config.score_labels.weak_below == 30.0
    assert config.decision.strength_min_score == 70.0
    assert config.board.max_active_posts == 5
    assert config.flows_k_anonymity == 20
    assert config.trip_warnings.high_impact_min_rank == 3


def test_methodology_config_missing_key_is_hard_error() -> None:
    rows = [
        row
        for row in _rows()
        if row["param_key"] != methodology_config.FLOWS_K_ANONYMITY
    ]

    with pytest.raises(methodology_config.MethodologyConfigError):
        methodology_config.build_methodology_config("v1.0", rows)


def test_methodology_config_rejects_unordered_thresholds() -> None:
    rows = _rows(**{methodology_config.SCORE_LABEL_LIMITED_BELOW: 20.0})

    with pytest.raises(methodology_config.MethodologyConfigError):
        methodology_config.build_methodology_config("v1.0", rows)


def test_public_parameters_endpoint_returns_active_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    methodology_config.clear_methodology_config_cache()
    monkeypatch.setattr(
        "app.repositories.methodology_config.get_active_methodology_version",
        lambda *_: "v1.0",
    )
    monkeypatch.setattr(
        "app.repositories.methodology_config.list_parameters_for_version",
        lambda *_: _rows(),
    )
    app = FastAPI()
    app.include_router(methodology_api.router, prefix="/api/v1")
    app.dependency_overrides[get_connection] = lambda: CONNECTION

    response = TestClient(app).get("/api/v1/methodology/parameters")

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "v1.0"
    assert {item["param_key"] for item in body["items"]}.issuperset(
        methodology_config.REQUIRED_NUMERIC_KEYS
    )
    methodology_config.clear_methodology_config_cache()


def test_methodology_dq_detects_missing_required_parameter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_missing_required_methodology_parameters",
        lambda *_: [{"version": "v1.0", "param_key": "score_label.weak_below"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "methodology_parameter_missing" in {
        issue.code for issue in report.issues
    }


def test_methodology_dq_checks_are_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)

    assert {
        "methodology_active_version_complete",
        "methodology_numeric_parameters_in_range",
        "methodology_thresholds_ordered",
    }.issubset({check.code for check in report.checks})

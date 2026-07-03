from app.repositories import platform_metrics as repository
from decimal import Decimal
from pathlib import Path
import pytest
from typing import Any
from unittest.mock import MagicMock


MIGRATION_SQL = Path(
    "database/migrations/032_computed_intelligence.sql"
).read_text(encoding="utf-8")


class FakeMetricStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def upsert(self, params: tuple[Any, ...]) -> dict[str, Any]:
        row = {
            "country_id": params[0],
            "metric_key": params[1],
            "scenario_slug": params[2],
            "value": params[3],
            "label": params[4],
            "confidence": params[5],
            "freshness_status": params[6],
            "window_days": params[7],
            "methodology_version": params[8],
            "input_summary": params[9],
            "source_count": params[10],
            "evidence_count": params[11],
            "signal_count": params[12],
            "event_count": params[13],
        }
        self._validate(row)
        existing = next(
            (
                item
                for item in self.rows
                if (
                    item["country_id"],
                    item["metric_key"],
                    item["scenario_slug"],
                    item["methodology_version"],
                )
                == (
                    row["country_id"],
                    row["metric_key"],
                    row["scenario_slug"],
                    row["methodology_version"],
                )
            ),
            None,
        )
        if existing is None:
            row["id"] = f"metric-{len(self.rows) + 1}"
            self.rows.append(row)
            return row
        existing.update(row)
        return existing

    def _validate(self, row: dict[str, Any]) -> None:
        if row["metric_key"] not in {
            "legal_velocity_index",
            "scenario_specific_risk_score",
            "contradiction_score",
        }:
            raise ValueError("metric_key")
        if row["value"] is not None and not Decimal("0") <= row["value"] <= Decimal(
            "100"
        ):
            raise ValueError("value")
        if row["label"] not in {
            "insufficient_data",
            "low",
            "moderate",
            "elevated",
            "high",
            "critical",
        }:
            raise ValueError("label")
        if row["confidence"] not in {"low", "medium", "high"}:
            raise ValueError("confidence")
        if row["freshness_status"] not in {"fresh", "stale", "unknown"}:
            raise ValueError("freshness_status")
        if not isinstance(getattr(row["input_summary"], "obj", {}), dict):
            raise ValueError("input_summary")
        if any(
            row[key] < 0
            for key in ("source_count", "evidence_count", "signal_count", "event_count")
        ):
            raise ValueError("counts")


def metric_params(**overrides: Any) -> dict[str, Any]:
    params: dict[str, Any] = {
        "connection": MagicMock(),
        "country_id": "country-1",
        "metric_key": "legal_velocity_index",
        "scenario_slug": None,
        "value": Decimal("42.50"),
        "label": "moderate",
        "confidence": "medium",
        "freshness_status": "fresh",
        "window_days": 365,
        "methodology_version": "v1.0",
        "input_summary": {"raw_points": 5},
        "source_count": 1,
        "evidence_count": 1,
        "signal_count": 1,
        "event_count": 3,
    }
    params.update(overrides)
    return params


def test_migration_creates_country_platform_metrics_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_platform_metrics" in MIGRATION_SQL
    assert "scenario_slug TEXT NOT NULL DEFAULT '__global__'" in MIGRATION_SQL
    assert "CONSTRAINT country_platform_metrics_unique" in MIGRATION_SQL


def test_migration_has_constraints_and_indexes() -> None:
    for name in [
        "country_platform_metrics_metric_key_check",
        "country_platform_metrics_value_check",
        "country_platform_metrics_label_check",
        "country_platform_metrics_confidence_check",
        "country_platform_metrics_freshness_status_check",
        "country_platform_metrics_input_summary_object_check",
        "idx_country_platform_metrics_country_metric_scenario",
    ]:
        assert name in MIGRATION_SQL


def test_upsert_inserts_new_metric(monkeypatch: pytest.MonkeyPatch) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_country_platform_metric(**metric_params())
    assert row["id"] == "metric-1"
    assert row["metric_key"] == "legal_velocity_index"


def test_upsert_updates_existing_metric(monkeypatch: pytest.MonkeyPatch) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    repository.upsert_country_platform_metric(**metric_params(value=Decimal("10.00")))
    row = repository.upsert_country_platform_metric(
        **metric_params(value=Decimal("20.00"))
    )
    assert len(store.rows) == 1
    assert row["value"] == Decimal("20.00")


def test_global_metric_with_none_scenario_stores_global(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_country_platform_metric(**metric_params(scenario_slug=None))
    assert row["scenario_slug"] == "__global__"


def test_repeated_global_upsert_does_not_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    repository.upsert_country_platform_metric(**metric_params(scenario_slug=""))
    repository.upsert_country_platform_metric(**metric_params(scenario_slug=None))
    assert len(store.rows) == 1


def test_scenario_metric_unique_per_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    base = metric_params(metric_key="scenario_specific_risk_score")
    repository.upsert_country_platform_metric(
        **{**base, "scenario_slug": "relocation_residence"}
    )
    repository.upsert_country_platform_metric(
        **{**base, "scenario_slug": "business_self_employment"}
    )
    assert len(store.rows) == 2


def test_list_country_platform_metrics_returns_expected_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = [{"metric_key": "legal_velocity_index"}]
    monkeypatch.setattr(repository, "fetch_all", lambda *_args: expected)
    assert repository.list_country_platform_metrics(MagicMock(), "russia") == expected


def test_get_country_platform_metric_returns_expected_global_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {"metric_key": "legal_velocity_index", "scenario_slug": "__global__"}
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: expected)
    assert (
        repository.get_country_platform_metric(
            MagicMock(), "russia", "legal_velocity_index", None
        )
        == expected
    )


def test_get_country_platform_metric_returns_expected_scenario_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {
        "metric_key": "scenario_specific_risk_score",
        "scenario_slug": "relocation_residence",
    }
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: expected)
    assert (
        repository.get_country_platform_metric(
            MagicMock(),
            "russia",
            "scenario_specific_risk_score",
            "relocation_residence",
        )
        == expected
    )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"value": Decimal("101.00")}, "value"),
        ({"metric_key": "cii"}, "metric_key"),
        ({"label": "bad"}, "label"),
        ({"confidence": "certain"}, "confidence"),
        ({"freshness_status": "new"}, "freshness_status"),
        ({"input_summary": []}, "input_summary"),
        ({"source_count": -1}, "counts"),
    ],
)
def test_invalid_values_rejected(
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, Any],
    message: str,
) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    with pytest.raises(ValueError, match=message):
        repository.upsert_country_platform_metric(**metric_params(**overrides))


def test_value_none_accepted_for_insufficient_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeMetricStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_country_platform_metric(
        **metric_params(value=None, label="insufficient_data")
    )
    assert row["value"] is None

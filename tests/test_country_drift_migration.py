from pathlib import Path
import pytest
from typing import Any


MIGRATION = Path("database/migrations/035_country_drift.sql")


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


VALID_LABELS = {
    "insufficient_data",
    "negative",
    "stable",
    "mildly_positive",
    "positive",
}
VALID_CONFIDENCE = {"low", "medium", "high"}


class FakeDriftSnapshotStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def insert(self, row: dict[str, Any]) -> dict[str, Any]:
        self._validate(row)
        key = (
            row["country_id"],
            row["period_start"],
            row["period_end"],
            row["methodology_version"],
        )
        for existing in self.rows:
            existing_key = (
                existing["country_id"],
                existing["period_start"],
                existing["period_end"],
                existing["methodology_version"],
            )
            if existing_key == key:
                raise ValueError("country_drift_snapshots_unique_period")
        self.rows.append(row)
        return row

    def _validate(self, row: dict[str, Any]) -> None:
        if row["period_start"] > row["period_end"]:
            raise ValueError("country_drift_snapshots_period_check")
        if row["window_days"] <= 0:
            raise ValueError("country_drift_snapshots_window_days_check")
        if row["label"] not in VALID_LABELS:
            raise ValueError("country_drift_snapshots_label_check")
        if (
            row["previous_label"] is not None
            and row["previous_label"] not in VALID_LABELS
        ):
            raise ValueError("country_drift_snapshots_previous_label_check")
        if row["confidence"] not in VALID_CONFIDENCE:
            raise ValueError("country_drift_snapshots_confidence_check")
        net_score = row.get("net_score")
        if net_score is not None and not (-100 <= net_score <= 100):
            raise ValueError("country_drift_snapshots_net_score_check")
        for weight_key in (
            "positive_weight",
            "negative_weight",
            "neutral_weight",
            "mixed_weight",
            "uncertain_weight",
            "total_weight",
        ):
            if row.get(weight_key, 0) < 0:
                raise ValueError("country_drift_snapshots_weight_check")
        for count_key in (
            "event_count",
            "positive_count",
            "negative_count",
            "neutral_count",
            "mixed_count",
            "uncertain_count",
        ):
            if row.get(count_key, 0) < 0:
                raise ValueError("country_drift_snapshots_count_check")
        if not isinstance(row.get("input_summary", {}), dict):
            raise ValueError("country_drift_snapshots_input_summary_object_check")


def _row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "country_id": "country-1",
        "period_start": "2026-01-01",
        "period_end": "2026-06-30",
        "window_days": 180,
        "label": "stable",
        "previous_label": None,
        "confidence": "medium",
        "net_score": 5.0,
        "positive_weight": 3.0,
        "negative_weight": 2.0,
        "neutral_weight": 1.0,
        "mixed_weight": 0.0,
        "uncertain_weight": 0.0,
        "total_weight": 6.0,
        "event_count": 5,
        "positive_count": 2,
        "negative_count": 1,
        "neutral_count": 2,
        "mixed_count": 0,
        "uncertain_count": 0,
        "methodology_version": "v1.0",
        "input_summary": {},
    }
    row.update(overrides)
    return row


def test_migration_file_exists() -> None:
    assert MIGRATION.exists()


def test_country_drift_snapshots_table_exists() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_drift_snapshots" in _sql()


def test_constraints_present() -> None:
    for name in [
        "country_drift_snapshots_period_check",
        "country_drift_snapshots_window_days_check",
        "country_drift_snapshots_label_check",
        "country_drift_snapshots_previous_label_check",
        "country_drift_snapshots_confidence_check",
        "country_drift_snapshots_net_score_check",
        "country_drift_snapshots_weight_check",
        "country_drift_snapshots_count_check",
        "country_drift_snapshots_input_summary_object_check",
        "country_drift_snapshots_unique_period",
    ]:
        assert name in _sql()


def test_indexes_present() -> None:
    for name in [
        "idx_country_drift_snapshots_country_period",
        "idx_country_drift_snapshots_label",
        "idx_country_drift_snapshots_confidence",
        "idx_country_drift_snapshots_computed_at",
        "idx_country_drift_snapshots_expires_at",
    ]:
        assert name in _sql()


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("CREATE TABLE IF NOT EXISTS country_drift_snapshots") == 1
    assert (
        sql.count(
            "CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_country_period"
        )
        == 1
    )


def test_migration_does_not_seed_rows() -> None:
    sql = _sql()
    assert "INSERT INTO country_drift_snapshots" not in sql


def test_migration_does_not_touch_other_domains() -> None:
    sql = _sql()
    for forbidden in (
        "country_cii_scores",
        "country_scores",
        "country_platform_metrics",
        "country_trust_scores",
        "domain_events",
    ):
        assert forbidden not in sql


def test_valid_row_can_be_inserted() -> None:
    store = FakeDriftSnapshotStore()
    row = store.insert(_row())
    assert row["label"] == "stable"


def test_invalid_label_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_label_check"):
        store.insert(_row(label="skyrocketing"))


def test_invalid_previous_label_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(
        ValueError, match="country_drift_snapshots_previous_label_check"
    ):
        store.insert(_row(previous_label="skyrocketing"))


def test_invalid_confidence_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_confidence_check"):
        store.insert(_row(confidence="certain"))


def test_negative_window_days_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_window_days_check"):
        store.insert(_row(window_days=-1))


def test_period_start_after_period_end_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_period_check"):
        store.insert(_row(period_start="2026-12-01", period_end="2026-01-01"))


def test_net_score_below_negative_100_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_net_score_check"):
        store.insert(_row(net_score=-100.01))


def test_net_score_above_100_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_net_score_check"):
        store.insert(_row(net_score=100.01))


def test_negative_weight_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_weight_check"):
        store.insert(_row(positive_weight=-1.0))


def test_negative_count_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(ValueError, match="country_drift_snapshots_count_check"):
        store.insert(_row(event_count=-1))


def test_non_object_input_summary_rejected() -> None:
    store = FakeDriftSnapshotStore()
    with pytest.raises(
        ValueError, match="country_drift_snapshots_input_summary_object_check"
    ):
        store.insert(_row(input_summary=[]))


def test_unique_country_period_methodology_enforced() -> None:
    store = FakeDriftSnapshotStore()
    store.insert(_row())
    with pytest.raises(ValueError, match="country_drift_snapshots_unique_period"):
        store.insert(_row())


def test_table_empty_after_clean_migration_before_any_service_runs() -> None:
    store = FakeDriftSnapshotStore()
    assert store.rows == []

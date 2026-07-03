"""Country drift repository queries: active countries, drift input events, lookups by slug."""

from app.repositories import country_drift as repository
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
import inspect
import pytest
from typing import Any
from unittest.mock import MagicMock


TODAY = date.today()

_FIXTURE_EVENTS: list[dict[str, Any]] = [
    {
        "event_id": "event-in-window",
        "legal_signal_id": "signal-in-window",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": date(2026, 3, 1),
        "impact_direction": "positive",
        "impact_level": "medium",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "effective",
        "status": "published",
        "source_id": "source-1",
        "evidence_item_id": "evidence-1",
        "evidence_count": 1,
    },
    {
        "event_id": "event-before-window",
        "legal_signal_id": "signal-before-window",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": date(2025, 1, 1),
        "impact_direction": "negative",
        "impact_level": "low",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "effective",
        "status": "published",
        "source_id": "source-2",
        "evidence_item_id": None,
        "evidence_count": 0,
    },
    {
        "event_id": "event-after-window",
        "legal_signal_id": "signal-after-window",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": date(2026, 12, 1),
        "impact_direction": "negative",
        "impact_level": "low",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "effective",
        "status": "published",
        "source_id": "source-3",
        "evidence_item_id": None,
        "evidence_count": 0,
    },
    {
        "event_id": "event-future",
        "legal_signal_id": "signal-future",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": TODAY + timedelta(days=30),
        "impact_direction": "positive",
        "impact_level": "low",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "proposed",
        "status": "published",
        "source_id": "source-4",
        "evidence_item_id": None,
        "evidence_count": 0,
    },
    {
        "event_id": "event-draft",
        "legal_signal_id": "signal-draft",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": date(2026, 3, 15),
        "impact_direction": "negative",
        "impact_level": "high",
        "signal_type": "policy",
        "affected_groups": [],
        "legal_status": "unknown",
        "status": "draft",
        "source_id": "source-5",
        "evidence_item_id": None,
        "evidence_count": 0,
    },
    {
        "event_id": "event-other-country",
        "legal_signal_id": "signal-other-country",
        "country_id": "country-2",
        "country_slug": "uruguay",
        "event_date": date(2026, 3, 1),
        "impact_direction": "neutral",
        "impact_level": "low",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "effective",
        "status": "published",
        "source_id": "source-6",
        "evidence_item_id": None,
        "evidence_count": 0,
    },
    {
        "event_id": "event-multi-evidence",
        "legal_signal_id": "signal-multi-evidence",
        "country_id": "country-1",
        "country_slug": "russia",
        "event_date": date(2026, 4, 1),
        "impact_direction": "positive",
        "impact_level": "high",
        "signal_type": "law",
        "affected_groups": [],
        "legal_status": "effective",
        "status": "published",
        "source_id": "source-7",
        "evidence_item_id": "evidence-7-a",
        "evidence_count": 3,
    },
]


def _query_drift_input_events(
    country_slug: str, period_start: date, period_end: date
) -> list[dict[str, Any]]:
    rows = []
    for event in _FIXTURE_EVENTS:
        if event["country_slug"] != country_slug:
            continue
        if event["status"] != "published":
            continue
        if event["event_date"] < period_start:
            continue
        if event["event_date"] > period_end:
            continue
        if event["event_date"] > TODAY:
            continue
        row = {key: value for key, value in event.items() if key != "status"}
        rows.append(row)
    return rows


class FakeSnapshotStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def upsert(self, params: tuple[Any, ...]) -> dict[str, Any]:
        keys = [
            "country_id",
            "period_start",
            "period_end",
            "window_days",
            "label",
            "previous_label",
            "confidence",
            "net_score",
            "positive_weight",
            "negative_weight",
            "neutral_weight",
            "mixed_weight",
            "uncertain_weight",
            "total_weight",
            "event_count",
            "positive_count",
            "negative_count",
            "neutral_count",
            "mixed_count",
            "uncertain_count",
            "methodology_version",
            "input_summary",
            "computed_at",
            "expires_at",
        ]
        row = dict(zip(keys, params, strict=True))
        existing = next(
            (
                item
                for item in self.rows
                if (
                    item["country_id"],
                    item["period_start"],
                    item["period_end"],
                    item["methodology_version"],
                )
                == (
                    row["country_id"],
                    row["period_start"],
                    row["period_end"],
                    row["methodology_version"],
                )
            ),
            None,
        )
        if existing is None:
            row["id"] = f"snapshot-{len(self.rows) + 1}"
            self.rows.append(row)
            return row
        existing.update(row)
        return existing


def snapshot_params(**overrides: Any) -> dict[str, Any]:
    params: dict[str, Any] = {
        "country_id": "country-1",
        "period_start": date(2026, 1, 1),
        "period_end": date(2026, 6, 30),
        "window_days": 180,
        "label": "stable",
        "previous_label": None,
        "confidence": "medium",
        "net_score": Decimal("5.00"),
        "positive_weight": Decimal("3"),
        "negative_weight": Decimal("2"),
        "neutral_weight": Decimal("1"),
        "mixed_weight": Decimal("0"),
        "uncertain_weight": Decimal("0"),
        "total_weight": Decimal("6"),
        "event_count": 5,
        "positive_count": 2,
        "negative_count": 1,
        "neutral_count": 2,
        "mixed_count": 0,
        "uncertain_count": 0,
        "methodology_version": "v1.0",
        "input_summary": {"window_days": 180},
        "computed_at": datetime(2026, 7, 1, tzinfo=UTC),
        "expires_at": None,
    }
    params.update(overrides)
    return params


def test_list_countries_for_drift_returns_active_countries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = [{"country_id": "country-1", "slug": "russia", "name": "Russia"}]
    monkeypatch.setattr(repository, "fetch_all", lambda *_args: expected)
    assert repository.list_countries_for_drift(MagicMock()) == expected


def test_get_country_for_drift_returns_country_by_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {"id": "country-1", "slug": "russia", "name": "Russia"}
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: expected)
    assert repository.get_country_for_drift(MagicMock(), "russia") == expected


def test_get_country_for_drift_returns_none_for_unknown_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: None)
    assert repository.get_country_for_drift(MagicMock(), "nowhere") is None


def test_list_drift_input_events_filters_by_country(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "fetch_all",
        lambda _c, _q, params: _query_drift_input_events(*params),
    )
    rows = repository.list_drift_input_events(
        MagicMock(), "uruguay", date(2020, 1, 1), date(2030, 1, 1)
    )
    assert all(row["country_id"] == "country-2" for row in rows)
    assert {row["event_id"] for row in rows} == {"event-other-country"}


def test_list_drift_input_events_filters_by_date_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "fetch_all",
        lambda _c, _q, params: _query_drift_input_events(*params),
    )
    rows = repository.list_drift_input_events(
        MagicMock(), "russia", date(2026, 1, 1), date(2026, 6, 30)
    )
    event_ids = {row["event_id"] for row in rows}
    assert "event-before-window" not in event_ids
    assert "event-after-window" not in event_ids


def test_list_drift_input_events_excludes_future_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "fetch_all",
        lambda _c, _q, params: _query_drift_input_events(*params),
    )
    rows = repository.list_drift_input_events(
        MagicMock(), "russia", date(2026, 1, 1), TODAY + timedelta(days=60)
    )
    event_ids = {row["event_id"] for row in rows}
    assert "event-future" not in event_ids


def test_list_drift_input_events_excludes_non_published_legal_signals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "fetch_all",
        lambda _c, _q, params: _query_drift_input_events(*params),
    )
    rows = repository.list_drift_input_events(
        MagicMock(), "russia", date(2026, 1, 1), date(2026, 6, 30)
    )
    event_ids = {row["event_id"] for row in rows}
    assert "event-draft" not in event_ids


def test_list_drift_input_events_returns_one_row_per_event_with_evidence_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "fetch_all",
        lambda _c, _q, params: _query_drift_input_events(*params),
    )
    rows = repository.list_drift_input_events(
        MagicMock(), "russia", date(2026, 1, 1), date(2026, 6, 30)
    )
    matching = [row for row in rows if row["event_id"] == "event-multi-evidence"]
    assert len(matching) == 1
    assert matching[0]["evidence_count"] == 3


def test_list_drift_input_events_uses_lateral_evidence_summary() -> None:
    source = inspect.getsource(repository.list_drift_input_events)
    assert "LATERAL" in source
    assert "COUNT(*)" in source
    assert "evidence_count" in source


def test_upsert_drift_snapshot_inserts_first_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeSnapshotStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_drift_snapshot(MagicMock(), **snapshot_params())
    assert row["id"] == "snapshot-1"
    assert row["label"] == "stable"
    assert len(store.rows) == 1


def test_upsert_drift_snapshot_updates_existing_period_instead_of_duplicating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeSnapshotStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    repository.upsert_drift_snapshot(MagicMock(), **snapshot_params(label="stable"))
    row = repository.upsert_drift_snapshot(
        MagicMock(), **snapshot_params(label="mildly_positive")
    )
    assert len(store.rows) == 1
    assert row["label"] == "mildly_positive"


def test_upsert_drift_snapshot_supports_none_net_score_for_insufficient_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeSnapshotStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_drift_snapshot(
        MagicMock(),
        **snapshot_params(label="insufficient_data", net_score=None, event_count=1),
    )
    assert row["net_score"] is None
    assert row["label"] == "insufficient_data"


def test_upsert_drift_snapshot_wraps_input_summary_as_jsonb(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = FakeSnapshotStore()
    monkeypatch.setattr(
        repository, "execute_one", lambda _c, _q, params: store.upsert(params)
    )
    row = repository.upsert_drift_snapshot(MagicMock(), **snapshot_params())
    assert getattr(row["input_summary"], "obj", None) == {"window_days": 180}


def test_get_latest_drift_snapshot_returns_newest_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {"id": "snapshot-1", "period_end": date(2026, 6, 30)}
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: expected)
    assert repository.get_latest_drift_snapshot(MagicMock(), "russia") == expected


def test_get_latest_drift_snapshot_orders_by_period_end_desc() -> None:
    source = inspect.getsource(repository.get_latest_drift_snapshot)
    assert "ORDER BY cds.period_end DESC, cds.computed_at DESC" in source
    assert "LIMIT 1" in source


def test_get_previous_drift_snapshot_returns_prior_period_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(
        _conn: Any, _query: str, params: tuple[Any, ...]
    ) -> dict[str, Any]:
        captured["params"] = params
        return {"id": "snapshot-0", "period_end": date(2026, 1, 1)}

    monkeypatch.setattr(repository, "fetch_one", fake_fetch_one)
    result = repository.get_previous_drift_snapshot(
        MagicMock(), "country-1", date(2026, 6, 30)
    )
    assert result == {"id": "snapshot-0", "period_end": date(2026, 1, 1)}
    assert captured["params"] == ("country-1", date(2026, 6, 30), "v1.0")


def test_get_previous_drift_snapshot_filters_period_end_less_than() -> None:
    source = inspect.getsource(repository.get_previous_drift_snapshot)
    assert "cds.period_end < %s" in source


def test_list_drift_snapshots_returns_newest_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = [
        {"id": "snapshot-2", "period_end": date(2026, 6, 30)},
        {"id": "snapshot-1", "period_end": date(2026, 1, 1)},
    ]
    monkeypatch.setattr(repository, "fetch_all", lambda *_args: expected)
    result = repository.list_drift_snapshots(MagicMock(), "russia")
    assert result == expected


def test_list_drift_snapshots_orders_by_period_end_desc() -> None:
    source = inspect.getsource(repository.list_drift_snapshots)
    assert "ORDER BY cds.period_end DESC, cds.computed_at DESC" in source


def test_count_drift_snapshots_works_globally(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: {"total": 7})
    assert repository.count_drift_snapshots(MagicMock()) == 7


def test_count_drift_snapshots_works_per_country(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: {"total": 3})
    assert repository.count_drift_snapshots(MagicMock(), "russia") == 3


def test_count_drift_snapshots_returns_zero_when_no_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "fetch_one", lambda *_args: None)
    assert repository.count_drift_snapshots(MagicMock()) == 0

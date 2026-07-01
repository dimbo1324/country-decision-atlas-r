from app.repositories import (
    country_drift as country_drift_repo,
    domain_events as domain_events_repo,
)
from app.services.country_drift import (
    CountryDriftCountryNotFoundError,
    build_drift_period,
    compute_and_store_all_country_drifts,
    compute_and_store_country_drift,
    compute_country_drift_snapshot,
)
from datetime import date, timedelta
import inspect
import pytest
from typing import Any
from unittest.mock import MagicMock


COUNTRY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "slug": "argentina",
    "name": "Argentina",
}


def _positive_events(count: int) -> list[dict[str, Any]]:
    return [
        {
            "event_id": f"event-{i}",
            "legal_signal_id": f"signal-{i}",
            "impact_direction": "positive",
            "impact_level": "high",
        }
        for i in range(count)
    ]


def _install_country_and_events(
    monkeypatch: pytest.MonkeyPatch,
    events: list[dict[str, Any]],
    previous_snapshot: dict[str, Any] | None,
) -> None:
    monkeypatch.setattr(country_drift_repo, "get_country_for_drift", lambda *_: COUNTRY)
    monkeypatch.setattr(
        country_drift_repo, "list_drift_input_events", lambda *_: events
    )
    monkeypatch.setattr(
        country_drift_repo, "get_previous_drift_snapshot", lambda *_: previous_snapshot
    )


class FakeSnapshotStore:
    def __init__(self) -> None:
        self.rows: dict[tuple[Any, ...], dict[str, Any]] = {}

    def upsert(self, **kwargs: Any) -> dict[str, Any]:
        key = (
            kwargs["country_id"],
            kwargs["period_start"],
            kwargs["period_end"],
            kwargs["methodology_version"],
        )
        row = dict(kwargs)
        row["id"] = self.rows.get(key, {}).get("id") or f"snapshot-{len(self.rows) + 1}"
        self.rows[key] = row
        return row


class FakeDomainEventStore:
    def __init__(self) -> None:
        self.events: dict[str, dict[str, Any]] = {}

    def insert(self, **kwargs: Any) -> dict[str, Any] | None:
        key = kwargs["event_key"]
        if key in self.events:
            return None
        row = dict(kwargs)
        row["id"] = f"event-{len(self.events) + 1}"
        self.events[key] = row
        return row


class TestBuildDriftPeriod:
    def test_uses_today_when_period_end_omitted(self) -> None:
        _start, end = build_drift_period(window_days=10)
        assert end == date.today()

    def test_uses_provided_period_end(self) -> None:
        provided = date(2026, 7, 1)
        _start, end = build_drift_period(period_end=provided, window_days=10)
        assert end == provided

    def test_period_start_calculation(self) -> None:
        provided = date(2026, 7, 1)
        start, _end = build_drift_period(period_end=provided, window_days=180)
        assert start == provided - timedelta(days=179)

    def test_invalid_window_days_rejected(self) -> None:
        with pytest.raises(ValueError, match="window_days"):
            build_drift_period(window_days=0)

    def test_negative_window_days_rejected(self) -> None:
        with pytest.raises(ValueError, match="window_days"):
            build_drift_period(window_days=-5)


class TestComputeCountryDriftSnapshot:
    def test_reads_country_and_events(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _install_country_and_events(monkeypatch, _positive_events(5), None)
        draft = compute_country_drift_snapshot(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert draft.country_slug == "argentina"
        assert draft.event_count == 5

    def test_sets_previous_label(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        draft = compute_country_drift_snapshot(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert draft.previous_label == "stable"

    def test_unknown_country_raises_controlled_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            country_drift_repo, "get_country_for_drift", lambda *_: None
        )
        with pytest.raises(CountryDriftCountryNotFoundError):
            compute_country_drift_snapshot(MagicMock(), country_slug="nowhere")


class TestComputeAndStoreCountryDrift:
    def test_inserts_snapshot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _install_country_and_events(monkeypatch, _positive_events(5), None)
        store = FakeSnapshotStore()
        monkeypatch.setattr(
            country_drift_repo,
            "upsert_drift_snapshot",
            lambda _conn, **kwargs: store.upsert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.stored is True
        assert result.computed is True
        assert len(store.rows) == 1

    def test_repeated_compute_updates_same_snapshot(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(monkeypatch, _positive_events(5), None)
        store = FakeSnapshotStore()
        monkeypatch.setattr(
            country_drift_repo,
            "upsert_drift_snapshot",
            lambda _conn, **kwargs: store.upsert(**kwargs),
        )
        compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert len(store.rows) == 1

    def test_unknown_country_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            country_drift_repo, "get_country_for_drift", lambda *_: None
        )
        result = compute_and_store_country_drift(MagicMock(), country_slug="nowhere")
        assert result.country_not_found is True
        assert result.computed is False
        assert result.stored is False


class TestDriftChangedEmission:
    def test_first_snapshot_does_not_emit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(monkeypatch, _positive_events(5), None)
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.event_emitted is False
        assert len(events_store.events) == 0

    def test_same_label_does_not_emit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "positive"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.label == "positive"
        assert result.event_emitted is False
        assert len(events_store.events) == 0

    def test_changed_label_emits_one_event(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.label == "positive"
        assert result.event_emitted is True
        assert len(events_store.events) == 1

    def test_repeated_recompute_of_changed_label_does_not_duplicate_event(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        second = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert len(events_store.events) == 1
        assert second.event_emitted is False

    def test_new_label_insufficient_data_does_not_emit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(monkeypatch, [], {"label": "stable"})
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.label == "insufficient_data"
        assert result.event_emitted is False
        assert len(events_store.events) == 0

    def test_insufficient_data_to_normal_label_emits_event(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "insufficient_data"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        events_store = FakeDomainEventStore()
        monkeypatch.setattr(
            domain_events_repo,
            "insert_domain_event",
            lambda _conn, **kwargs: events_store.insert(**kwargs),
        )
        result = compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert result.previous_label == "insufficient_data"
        assert result.label == "positive"
        assert result.event_emitted is True


class TestBatch:
    def test_processes_active_countries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        countries = [
            {"country_id": "c1", "slug": "russia", "name": "Russia"},
            {"country_id": "c2", "slug": "uruguay", "name": "Uruguay"},
        ]
        monkeypatch.setattr(
            country_drift_repo, "list_countries_for_drift", lambda *_: countries
        )
        monkeypatch.setattr(
            country_drift_repo,
            "get_country_for_drift",
            lambda _c, slug: next(
                {"id": c["country_id"], "slug": c["slug"], "name": c["name"]}
                for c in countries
                if c["slug"] == slug
            ),
        )
        monkeypatch.setattr(
            country_drift_repo,
            "list_drift_input_events",
            lambda *_: _positive_events(5),
        )
        monkeypatch.setattr(
            country_drift_repo, "get_previous_drift_snapshot", lambda *_: None
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        monkeypatch.setattr(
            domain_events_repo, "insert_domain_event", lambda _conn, **kwargs: kwargs
        )
        summary = compute_and_store_all_country_drifts(
            MagicMock(), period_end=date(2026, 7, 1)
        )
        assert summary.countries_processed == 2
        assert summary.snapshots_written == 2

    def test_batch_summary_counts_insufficient_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        countries = [{"country_id": "c1", "slug": "russia", "name": "Russia"}]
        monkeypatch.setattr(
            country_drift_repo, "list_countries_for_drift", lambda *_: countries
        )
        monkeypatch.setattr(
            country_drift_repo,
            "get_country_for_drift",
            lambda *_: {"id": "c1", "slug": "russia", "name": "Russia"},
        )
        monkeypatch.setattr(
            country_drift_repo, "list_drift_input_events", lambda *_: []
        )
        monkeypatch.setattr(
            country_drift_repo, "get_previous_drift_snapshot", lambda *_: None
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        summary = compute_and_store_all_country_drifts(
            MagicMock(), period_end=date(2026, 7, 1)
        )
        assert summary.insufficient_data_count == 1
        assert summary.events_emitted == 0


class TestDomainEventShape:
    def test_payload_contains_required_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        captured: dict[str, Any] = {}

        def fake_insert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return kwargs

        monkeypatch.setattr(domain_events_repo, "insert_domain_event", fake_insert)
        compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        payload = captured["payload"]
        for field_name in (
            "country_slug",
            "event_type",
            "previous_label",
            "new_label",
            "period_start",
            "period_end",
            "window_days",
            "net_score",
            "confidence",
            "event_count",
            "methodology_version",
        ):
            assert field_name in payload

    def test_event_key_contains_country_slug_period_end_methodology_version(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        monkeypatch.setattr(
            country_drift_repo, "upsert_drift_snapshot", lambda _conn, **kwargs: kwargs
        )
        captured: dict[str, Any] = {}

        def fake_insert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return kwargs

        monkeypatch.setattr(domain_events_repo, "insert_domain_event", fake_insert)
        compute_and_store_country_drift(
            MagicMock(), country_slug="argentina", period_end=date(2026, 7, 1)
        )
        assert (
            captured["event_key"] == "country:argentina:drift.changed:2026-07-01:v1.0"
        )


class TestDryRun:
    def test_dry_run_writes_no_snapshot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        upsert_called = False

        def fake_upsert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal upsert_called
            upsert_called = True
            return kwargs

        monkeypatch.setattr(country_drift_repo, "upsert_drift_snapshot", fake_upsert)
        result = compute_and_store_country_drift(
            MagicMock(),
            country_slug="argentina",
            period_end=date(2026, 7, 1),
            dry_run=True,
        )
        assert result.stored is False
        assert upsert_called is False

    def test_dry_run_emits_no_domain_event(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _install_country_and_events(
            monkeypatch, _positive_events(5), {"label": "stable"}
        )
        insert_called = False

        def fake_insert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal insert_called
            insert_called = True
            return kwargs

        monkeypatch.setattr(domain_events_repo, "insert_domain_event", fake_insert)
        result = compute_and_store_country_drift(
            MagicMock(),
            country_slug="argentina",
            period_end=date(2026, 7, 1),
            dry_run=True,
        )
        assert insert_called is False
        assert result.event_emitted is True


class TestRegressionInvariants:
    def test_service_module_does_not_touch_unrelated_domains(self) -> None:
        import app.services.country_drift as module

        source = inspect.getsource(module)
        for forbidden in (
            "cii",
            "decision_engine",
            "country_scores",
            "platform_metrics",
            "trust_score",
        ):
            assert forbidden not in source

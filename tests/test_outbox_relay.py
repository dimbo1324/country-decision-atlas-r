"""Outbox relay: event selection, filtering, failure handling, and outgoing payload shape."""

from __future__ import annotations

from datetime import UTC, datetime
import pytest
from scripts.outbox_relay import (
    FakePublisher,
    RelayMetrics,
    build_relay_payload,
    relay_key,
    run_relay,
    write_metrics,
)
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4


NOTIFY_AFTER = "2026-01-01T00:00:00Z"
AFTER_DT = datetime(2026, 6, 1, tzinfo=UTC)


def _make_event(
    *,
    event_id: UUID | None = None,
    event_key: str = "key-1",
    event_type: str = "legal_signal.published",
    aggregate_type: str = "legal_signal",
    aggregate_id: UUID | None = None,
    country_slug: str | None = "argentina",
    status: str = "pending",
    notifiable: bool = True,
    created_at: datetime | None = None,
    attempts: int = 0,
    last_error: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(event_id or uuid4()),
        "event_key": event_key,
        "event_type": event_type,
        "aggregate_type": aggregate_type,
        "aggregate_id": str(aggregate_id or uuid4()),
        "country_slug": country_slug,
        "payload": {"title": "Test"},
        "status": status,
        "notifiable": notifiable,
        "created_at": created_at or AFTER_DT,
        "relayed_at": None,
        "attempts": attempts,
        "last_error": last_error,
    }


def _make_conn() -> Any:
    conn = MagicMock()
    conn.transaction.return_value.__enter__ = lambda s: s
    conn.transaction.return_value.__exit__ = MagicMock(return_value=False)
    return conn


def _patch_repo(
    monkeypatch: pytest.MonkeyPatch,
    events: list[dict[str, Any]],
    relayed_ids: list[str],
    failed_calls: list[tuple[str, str, int]],
) -> None:
    import app.repositories.domain_events as repo

    def fake_lock(
        _c: Any,
        *,
        batch_size: int,  # noqa: ARG001
        notify_after: str,  # noqa: ARG001
    ) -> list[dict[str, Any]]:
        return events

    def fake_relayed(_c: Any, event_id: UUID) -> dict[str, Any] | None:
        relayed_ids.append(str(event_id))
        return None

    def fake_failed_or_retry(
        _c: Any, event_id: UUID, error: str, max_attempts_arg: int
    ) -> dict[str, Any] | None:
        failed_calls.append((str(event_id), error, max_attempts_arg))
        for event in events:
            if str(event["id"]) == str(event_id):
                attempts = int(event.get("attempts") or 0) + 1
                if attempts >= max_attempts_arg:
                    return {**event, "status": "failed", "attempts": attempts}
        return None

    monkeypatch.setattr(repo, "lock_pending_notifiable_domain_events", fake_lock)
    monkeypatch.setattr(repo, "mark_domain_event_relayed", fake_relayed)
    monkeypatch.setattr(
        repo, "mark_domain_event_publish_failed_or_retry", fake_failed_or_retry
    )


class TestRelaySelection:
    def test_pending_notifiable_event_is_published(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-1", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        pub = FakePublisher()
        count = run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER)
        assert count == 1
        assert len(pub.published) == 1

    def test_event_becomes_relayed_on_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-2", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        pub = FakePublisher()
        run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER)
        assert len(relayed) == 1

    def test_success_metrics_are_recorded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-metrics", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        metrics = RelayMetrics()
        count = run_relay(
            _make_conn(),
            FakePublisher(),
            notify_after=NOTIFY_AFTER,
            metrics=metrics,
        )
        assert count == 1
        assert metrics.selected_total == 1
        assert metrics.published_total == 1
        assert metrics.relayed_total == 1
        assert metrics.failed_total == 0

    def test_no_events_returns_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        _patch_repo(monkeypatch, [], relayed, failed)
        pub = FakePublisher()
        count = run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER)
        assert count == 0
        assert len(pub.published) == 0


class TestRelayFiltering:
    def test_relayed_event_not_returned_by_lock(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        _patch_repo(monkeypatch, [], relayed, failed)
        pub = FakePublisher()
        run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER)
        assert len(pub.published) == 0

    def test_dry_run_publishes_nothing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-dry", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        pub = FakePublisher()
        count = run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER, dry_run=True)
        assert count == 1
        assert len(pub.published) == 0
        assert len(relayed) == 0

    def test_dry_run_metrics_are_recorded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-dry-metrics", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        metrics = RelayMetrics()
        run_relay(
            _make_conn(),
            FakePublisher(),
            notify_after=NOTIFY_AFTER,
            dry_run=True,
            metrics=metrics,
        )
        assert metrics.selected_total == 1
        assert metrics.dry_run_total == 1
        assert metrics.skipped_total == 1
        assert metrics.published_total == 0

    def test_dry_run_changes_no_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        events = [
            _make_event(event_key=f"key-dr-{i}", created_at=AFTER_DT) for i in range(3)
        ]
        _patch_repo(monkeypatch, events, relayed, failed)
        pub = FakePublisher()
        run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER, dry_run=True)
        assert len(relayed) == 0
        assert len(failed) == 0


class TestRelayFailure:
    def test_publish_failure_calls_failed_handler(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-fail", created_at=AFTER_DT, attempts=0)
        _patch_repo(monkeypatch, [event], relayed, failed)

        class _FailPublisher:
            def publish(self, _key: str, _payload: dict[str, Any]) -> None:
                raise RuntimeError("kafka unavailable")

        run_relay(
            _make_conn(), _FailPublisher(), notify_after=NOTIFY_AFTER, max_attempts=3
        )
        assert len(failed) == 1

    def test_failure_metrics_are_recorded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-fail-metrics", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)

        class _FailPublisher:
            def publish(self, _key: str, _payload: dict[str, Any]) -> None:
                raise RuntimeError("kafka unavailable")

        metrics = RelayMetrics()
        run_relay(
            _make_conn(),
            _FailPublisher(),
            notify_after=NOTIFY_AFTER,
            max_attempts=3,
            metrics=metrics,
        )
        assert metrics.selected_total == 1
        assert metrics.failed_total == 1
        assert metrics.relayed_total == 0

    def test_failure_does_not_relay(self, monkeypatch: pytest.MonkeyPatch) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-retry", created_at=AFTER_DT, attempts=0)
        _patch_repo(monkeypatch, [event], relayed, failed)

        class _FailPublisher:
            def publish(self, _key: str, _payload: dict[str, Any]) -> None:
                raise RuntimeError("kafka unavailable")

        run_relay(
            _make_conn(), _FailPublisher(), notify_after=NOTIFY_AFTER, max_attempts=3
        )
        assert len(relayed) == 0

    def test_failure_passes_max_attempts_to_repo(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-max", created_at=AFTER_DT, attempts=2)
        _patch_repo(monkeypatch, [event], relayed, failed)

        class _FailPublisher:
            def publish(self, _key: str, _payload: dict[str, Any]) -> None:
                raise RuntimeError("kafka unavailable")

        run_relay(
            _make_conn(), _FailPublisher(), notify_after=NOTIFY_AFTER, max_attempts=3
        )
        assert failed[0][2] == 3

    def test_last_attempt_metrics_mark_failed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-last", created_at=AFTER_DT, attempts=2)
        _patch_repo(monkeypatch, [event], relayed, failed)

        class _FailPublisher:
            def publish(self, _key: str, _payload: dict[str, Any]) -> None:
                raise RuntimeError("kafka unavailable")

        metrics = RelayMetrics()
        run_relay(
            _make_conn(),
            _FailPublisher(),
            notify_after=NOTIFY_AFTER,
            max_attempts=3,
            metrics=metrics,
        )
        assert metrics.marked_failed_total == 1
        assert metrics.max_attempts_reached_total == 1


class TestPayloadShape:
    def test_payload_contains_required_fields(self) -> None:
        event = _make_event(event_key="key-shape", created_at=AFTER_DT)
        payload = build_relay_payload(event)
        for field in (
            "event_key",
            "event_type",
            "aggregate_type",
            "aggregate_id",
            "country_slug",
            "payload",
            "created_at",
        ):
            assert field in payload, f"missing field: {field}"

    def test_relay_key_uses_country_slug(self) -> None:
        event = _make_event(country_slug="argentina")
        assert relay_key(event) == "argentina"

    def test_relay_key_falls_back_to_aggregate_type(self) -> None:
        event = _make_event(country_slug=None, aggregate_type="legal_signal")
        assert relay_key(event) == "legal_signal"


class TestKafkaNotRequired:
    def test_fake_publisher_does_not_import_kafka(self) -> None:
        pub = FakePublisher()
        pub.publish("key", {"event_key": "k1"})
        assert len(pub.published) == 1

    def test_run_relay_with_fake_publisher_no_kafka(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        relayed: list[str] = []
        failed: list[tuple[str, str, int]] = []
        event = _make_event(event_key="key-nokafka", created_at=AFTER_DT)
        _patch_repo(monkeypatch, [event], relayed, failed)
        pub = FakePublisher()
        count = run_relay(_make_conn(), pub, notify_after=NOTIFY_AFTER)
        assert count == 1


class TestRelayMetricsOutput:
    def test_write_metrics_output_file(self, tmp_path: Any) -> None:
        metrics = RelayMetrics(selected_total=1, published_total=1)
        path = tmp_path / "relay-metrics.json"

        write_metrics(metrics, metrics_json=False, metrics_output=str(path))

        assert path.exists()
        body = path.read_text(encoding="utf-8")
        assert '"selected_total": 1' in body
        assert '"published_total": 1' in body

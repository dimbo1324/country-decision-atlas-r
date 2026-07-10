from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID


DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_NOTIFY_AFTER = "2026-01-01T00:00:00Z"
DEFAULT_KAFKA_TOPIC = "cda.domain-events"
DEFAULT_STALE_IN_FLIGHT_SECONDS = 300
DEFAULT_MESSAGE_TIMEOUT_MS = 10_000
DEFAULT_DELIVERY_TIMEOUT_MS = 10_000


class EventPublisher(Protocol):
    def publish(self, key: str, payload: dict[str, Any]) -> None: ...


class FakePublisher:
    def __init__(self) -> None:
        self.published: list[tuple[str, dict[str, Any]]] = []

    def publish(self, key: str, payload: dict[str, Any]) -> None:
        self.published.append((key, payload))


class KafkaPublisher:
    def __init__(self, brokers: str, topic: str) -> None:
        self._brokers = brokers
        self._topic = topic
        self._producer: Any = None

    def _get_producer(self) -> Any:
        if self._producer is None:
            try:
                from confluent_kafka import Producer
            except ImportError as e:
                raise RuntimeError(
                    "confluent-kafka is not installed. "
                    "Install it with: pip install 'country-decision-atlas[alerts]'"
                ) from e
            self._producer = Producer(
                {
                    "bootstrap.servers": self._brokers,
                    "message.timeout.ms": DEFAULT_MESSAGE_TIMEOUT_MS,
                    "delivery.timeout.ms": DEFAULT_DELIVERY_TIMEOUT_MS,
                }
            )
        return self._producer

    def publish(self, key: str, payload: dict[str, Any]) -> None:
        producer = self._get_producer()
        producer.produce(
            self._topic,
            key=key.encode("utf-8"),
            value=json.dumps(payload, default=str).encode("utf-8"),
        )
        producer.flush()


@dataclass
class RelayMetrics:
    selected_total: int = 0
    published_total: int = 0
    relayed_total: int = 0
    failed_total: int = 0
    marked_failed_total: int = 0
    skipped_total: int = 0
    dry_run_total: int = 0
    duration_ms: int = 0
    notifiable_false_skipped_total: int = 0
    before_notify_after_skipped_total: int = 0
    max_attempts_reached_total: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def build_relay_payload(event: dict[str, Any]) -> dict[str, Any]:
    created_at = event.get("created_at")
    if isinstance(created_at, datetime):
        created_at_str = created_at.isoformat()
    else:
        created_at_str = str(created_at) if created_at is not None else ""
    return {
        "event_key": event["event_key"],
        "event_type": event["event_type"],
        "aggregate_type": event["aggregate_type"],
        "aggregate_id": str(event["aggregate_id"]),
        "country_slug": event.get("country_slug") or "",
        "payload": event.get("payload") or {},
        "created_at": created_at_str,
    }


def relay_key(event: dict[str, Any]) -> str:
    slug = event.get("country_slug")
    if slug:
        return str(slug)
    return str(event.get("aggregate_type", ""))


def run_relay(
    conn: Any,
    publisher: EventPublisher,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    notify_after: str = DEFAULT_NOTIFY_AFTER,
    dry_run: bool = False,
    metrics: RelayMetrics | None = None,
    stale_in_flight_seconds: int = DEFAULT_STALE_IN_FLIGHT_SECONDS,
) -> int:
    from app.repositories.domain_events import (
        list_pending_domain_events,
        lock_and_mark_in_flight_domain_events,
        mark_domain_event_publish_failed_or_retry,
        mark_domain_event_relayed,
        requeue_stale_in_flight_domain_events,
    )

    started = time.monotonic()
    metrics = metrics or RelayMetrics()
    try:
        if dry_run:
            events = list_pending_domain_events(conn, limit=batch_size)
            metrics.selected_total = len(events)
            metrics.dry_run_total = len(events)
            metrics.skipped_total = len(events)
            return len(events)

        with conn.transaction():
            requeue_stale_in_flight_domain_events(
                conn, stale_after_seconds=stale_in_flight_seconds
            )

        with conn.transaction():
            events = lock_and_mark_in_flight_domain_events(
                conn,
                batch_size=batch_size,
                notify_after=notify_after,
            )
        metrics.selected_total = len(events)
        if not events:
            return 0

        for event in events:
            event_id = UUID(str(event["id"]))
            payload = build_relay_payload(event)
            key = relay_key(event)
            try:
                publisher.publish(key, payload)
                metrics.published_total += 1
                with conn.transaction():
                    mark_domain_event_relayed(conn, event_id)
                metrics.relayed_total += 1
            except Exception as exc:
                metrics.failed_total += 1
                with conn.transaction():
                    updated = mark_domain_event_publish_failed_or_retry(
                        conn, event_id, str(exc), max_attempts
                    )
                attempts = int(event.get("attempts") or 0) + 1
                if (
                    updated and updated.get("status") == "failed"
                ) or attempts >= max_attempts:
                    metrics.marked_failed_total += 1
                    metrics.max_attempts_reached_total += 1

        return len(events)
    finally:
        metrics.duration_ms = int((time.monotonic() - started) * 1000)


def write_metrics(
    metrics: RelayMetrics, *, metrics_json: bool, metrics_output: str | None
) -> None:
    payload = json.dumps(metrics.to_dict(), sort_keys=True)
    if metrics_output:
        path = Path(metrics_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    if metrics_json:
        print(payload)

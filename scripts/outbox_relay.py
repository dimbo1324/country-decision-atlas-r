from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
import sys
from typing import Any, Protocol
from uuid import UUID


DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_NOTIFY_AFTER = "2026-01-01T00:00:00Z"
DEFAULT_KAFKA_TOPIC = "cda.domain-events"


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
            self._producer = Producer({"bootstrap.servers": self._brokers})
        return self._producer

    def publish(self, key: str, payload: dict[str, Any]) -> None:
        producer = self._get_producer()
        producer.produce(
            self._topic,
            key=key.encode("utf-8"),
            value=json.dumps(payload, default=str).encode("utf-8"),
        )
        producer.flush()


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
) -> int:
    from app.repositories.domain_events import (
        lock_pending_notifiable_domain_events,
        mark_domain_event_publish_failed_or_retry,
        mark_domain_event_relayed,
    )

    with conn.transaction():
        events = lock_pending_notifiable_domain_events(
            conn,
            batch_size=batch_size,
            notify_after=notify_after,
        )

        if not events:
            return 0

        if dry_run:
            return len(events)

        for event in events:
            event_id = UUID(str(event["id"]))
            payload = build_relay_payload(event)
            key = relay_key(event)
            try:
                publisher.publish(key, payload)
                mark_domain_event_relayed(conn, event_id)
            except Exception as exc:
                mark_domain_event_publish_failed_or_retry(
                    conn, event_id, str(exc), max_attempts
                )

        return len(events)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outbox relay: domain_events → Kafka")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument(
        "--notify-after",
        default=os.environ.get("NOTIFY_AFTER", DEFAULT_NOTIFY_AFTER),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    kafka_brokers = os.environ.get("KAFKA_BROKERS", "localhost:9092")
    kafka_topic = os.environ.get("KAFKA_TOPIC", DEFAULT_KAFKA_TOPIC)

    import psycopg

    publisher: EventPublisher = KafkaPublisher(kafka_brokers, kafka_topic)

    with psycopg.connect(database_url, row_factory=psycopg.rows.dict_row) as conn:
        count = run_relay(
            conn,
            publisher,
            batch_size=args.batch_size,
            max_attempts=args.max_attempts,
            notify_after=args.notify_after,
            dry_run=args.dry_run,
        )

    if args.dry_run:
        print(f"dry-run: {count} eligible events found, nothing published")
    else:
        print(f"relayed: {count} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())

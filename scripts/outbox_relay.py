from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from scripts.outbox_relay_runner import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_KAFKA_TOPIC,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_NOTIFY_AFTER,
    EventPublisher,
    FakePublisher as FakePublisher,
    KafkaPublisher,
    RelayMetrics as RelayMetrics,
    build_relay_payload as build_relay_payload,
    relay_key as relay_key,
    run_relay as run_relay,
    write_metrics as write_metrics,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outbox relay: domain_events -> Kafka")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument(
        "--notify-after",
        default=os.environ.get("NOTIFY_AFTER", DEFAULT_NOTIFY_AFTER),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--metrics-json", action="store_true")
    parser.add_argument("--metrics-output")
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
        metrics = RelayMetrics()
        count = run_relay(
            conn,
            publisher,
            batch_size=args.batch_size,
            max_attempts=args.max_attempts,
            notify_after=args.notify_after,
            dry_run=args.dry_run,
            metrics=metrics,
        )

    if args.metrics_json or args.metrics_output:
        write_metrics(
            metrics, metrics_json=args.metrics_json, metrics_output=args.metrics_output
        )
    elif args.dry_run:
        print(f"dry-run: {count} eligible events found, nothing published")
    else:
        print(f"relayed: {count} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())

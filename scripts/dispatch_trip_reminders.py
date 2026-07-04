from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
    sys.path.insert(0, str(ROOT_DIR))

import psycopg  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.services.trip_planner.reminders import (  # noqa: E402
    dispatch_due_reminders,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dispatch due trip reminders into the domain_events outbox."
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    if args.limit < 1:
        print(json.dumps({"error": "limit must be positive"}), file=sys.stderr)
        return 2

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            summary = dispatch_due_reminders(
                conn, now=datetime.now(UTC), limit=args.limit
            )
            if args.dry_run:
                conn.rollback()
                summary["dry_run"] = True
            else:
                conn.commit()
                summary["dry_run"] = False
            print(json.dumps(summary, indent=2, default=str))
            return 0
    except psycopg.OperationalError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

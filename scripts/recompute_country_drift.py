from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings  # noqa: E402
from app.services.country_drift import (  # noqa: E402
    compute_and_store_all_country_drifts,
    compute_and_store_country_drift,
)
import psycopg  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Recompute country drift snapshots.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--country", type=str)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--no-events", action="store_true", default=False)
    args = parser.parse_args()

    settings = get_settings()
    emit_events = not args.no_events
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            if args.all:
                summary = compute_and_store_all_country_drifts(
                    conn,
                    dry_run=args.dry_run,
                    emit_events=emit_events,
                )
                if not args.dry_run:
                    conn.commit()
                print(
                    json.dumps(
                        {
                            "countries_processed": summary.countries_processed,
                            "snapshots_written": summary.snapshots_written,
                            "events_emitted": summary.events_emitted,
                            "insufficient_data_count": summary.insufficient_data_count,
                            "errors": summary.errors,
                        },
                        indent=2,
                        default=str,
                    )
                )
                return 1 if summary.errors else 0
            else:
                result = compute_and_store_country_drift(
                    conn,
                    country_slug=args.country,
                    dry_run=args.dry_run,
                    emit_events=emit_events,
                )
                if not args.dry_run and result.stored:
                    conn.commit()
                print(
                    json.dumps(
                        {
                            "country_slug": result.country_slug,
                            "country_not_found": result.country_not_found,
                            "dry_run": result.dry_run,
                            "computed": result.computed,
                            "stored": result.stored,
                            "label": result.label,
                            "previous_label": result.previous_label,
                            "confidence": result.confidence,
                            "net_score": float(result.net_score)
                            if result.net_score is not None
                            else None,
                            "event_count": result.event_count,
                            "event_emitted": result.event_emitted,
                            "error": result.error,
                        },
                        indent=2,
                        default=str,
                    )
                )
                return 1 if (result.error or result.country_not_found) else 0
    except psycopg.OperationalError as exc:
        print(f"DB connection error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

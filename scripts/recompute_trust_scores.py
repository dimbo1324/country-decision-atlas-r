from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
    sys.path.insert(0, str(ROOT_DIR))

import psycopg  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.services.trust_runtime import (  # noqa: E402
    compute_and_store_trust_for_all_countries,
    compute_and_store_trust_for_country,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recompute country trust scores."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--country", type=str)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            if args.all:
                summary = compute_and_store_trust_for_all_countries(
                    conn,
                    dry_run=args.dry_run,
                )
                if not args.dry_run:
                    conn.commit()
                print(json.dumps(summary, indent=2, default=str))
                failed = summary.get("countries_failed", 0)
                return 1 if failed > 0 else 0
            else:
                result = compute_and_store_trust_for_country(
                    conn,
                    args.country,
                    dry_run=args.dry_run,
                )
                if not args.dry_run and result.get("stored"):
                    conn.commit()
                print(json.dumps(result, indent=2, default=str))
                return 1 if result.get("error") else 0
    except psycopg.OperationalError as exc:
        print(f"DB connection error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

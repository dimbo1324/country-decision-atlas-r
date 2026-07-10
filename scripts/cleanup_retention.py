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
from app.services.retention import run_retention_cleanup  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete rows past their configured retention window "
        "from analytics_events, ai_interaction_logs, relayed domain_events, "
        "and expired/revoked auth_sessions."
    )
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            result = run_retention_cleanup(conn, dry_run=args.dry_run)
            if not args.dry_run:
                conn.commit()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

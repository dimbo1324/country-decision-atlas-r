from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from psycopg import OperationalError, connect
from psycopg.rows import dict_row


ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
for import_path in (ROOT_DIR, API_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from app.core.config import get_settings  # noqa: E402
from app.services.platform_metrics_runtime import (  # noqa: E402
    compute_platform_metrics_for_all_countries,
)
from app.services.trust_runtime import (  # noqa: E402
    compute_and_store_trust_for_all_countries,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap computed runtime read models."
    )
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args(argv)

    settings = get_settings()
    try:
        with connect(settings.database_url, row_factory=dict_row) as conn:
            platform_summary = compute_platform_metrics_for_all_countries(
                conn, dry_run=args.dry_run
            )
            if not platform_summary.feature_enabled:
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "stage": "platform_metrics",
                            "platform_metrics": platform_summary.model_dump(),
                        },
                        default=str,
                    )
                )
                return 1
            if platform_summary.metrics_failed > 0:
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "stage": "platform_metrics",
                            "platform_metrics": platform_summary.model_dump(),
                        },
                        default=str,
                    )
                )
                return 1
            if not args.dry_run:
                conn.commit()

            trust_summary = compute_and_store_trust_for_all_countries(
                conn, dry_run=args.dry_run
            )
            if not args.dry_run:
                conn.commit()

            ok = (
                bool(trust_summary.get("feature_enabled", False))
                and int(trust_summary.get("countries_failed", 0)) == 0
            )
            print(
                json.dumps(
                    {
                        "ok": ok,
                        "dry_run": args.dry_run,
                        "platform_metrics": platform_summary.model_dump(),
                        "trust_scores": trust_summary,
                    },
                    default=str,
                )
            )
            return 0 if ok else 1
    except OperationalError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

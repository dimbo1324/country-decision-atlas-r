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
from app.services.platform_metrics_runtime import (  # noqa: E402
    compute_platform_metrics_for_all_countries,
    compute_platform_metrics_for_country,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recompute platform metrics.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--country", type=str)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--metric-key", type=str, default=None)
    parser.add_argument("--scenario-slug", type=str, default=None)
    args = parser.parse_args()

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            if args.all:
                summary = compute_platform_metrics_for_all_countries(
                    conn,
                    dry_run=args.dry_run,
                    metric_key=args.metric_key,
                    scenario_slug=args.scenario_slug,
                )
                print(json.dumps(summary.model_dump(), default=str))
                if not summary.feature_enabled:
                    return 1
                if summary.metrics_failed > 0:
                    return 1
            else:
                country_result = compute_platform_metrics_for_country(
                    conn,
                    args.country,
                    dry_run=args.dry_run,
                    metric_key=args.metric_key,
                    scenario_slug=args.scenario_slug,
                )
                print(json.dumps(country_result.model_dump(), default=str))
                if not country_result.feature_enabled:
                    return 1
                if (
                    country_result.errors
                    and country_result.metrics_computed == 0
                ):
                    return 1
                if country_result.metrics_failed > 0:
                    return 1
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

import argparse
import os
import sys


_repo_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
_api_path = os.path.join(_repo_root, "apps", "api")
if _api_path not in sys.path:
    sys.path.insert(0, _api_path)

import psycopg  # noqa: E402
from country_decision_atlas_shared.config import get_settings  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402


def _run_translation_jobs(args: argparse.Namespace) -> None:
    settings = get_settings()
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        from app.services.translation_jobs import process_batch
        from app.services.translation_providers import get_translation_provider

        provider = get_translation_provider()
        result = process_batch(
            conn,
            worker_id=args.worker_id,
            target_locale=args.target_locale or None,
            limit=args.limit,
            provider=provider,
            dry_run=args.dry_run,
        )
    print(
        f"processed={result['processed']} completed={result['completed']} failed={result['failed']}"
    )
    for r in result["results"]:
        print(
            f"  job={r['job_id']} status={r['status']} variant={r.get('variant_id')} error={r.get('error')}"
        )


def run() -> None:
    parser = argparse.ArgumentParser(prog="worker")
    subparsers = parser.add_subparsers(dest="command")

    tj = subparsers.add_parser("translation-jobs")
    tj.add_argument("--limit", type=int, default=10)
    tj.add_argument("--target-locale", type=str, default="en")
    tj.add_argument("--worker-id", type=str, default="local-worker")
    tj.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()

    if args.command == "translation-jobs":
        _run_translation_jobs(args)
    else:
        parser.print_help()
        sys.exit(1)

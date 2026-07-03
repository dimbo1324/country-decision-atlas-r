from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
from psycopg import connect
from psycopg.rows import dict_row
import sys
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
for import_path in (ROOT_DIR, API_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from app.core.config import get_settings  # noqa: E402
from app.repositories import auth as repository  # noqa: E402


def cleanup(connection: Any, limit: int, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        expired = repository.list_expired_unrevoked_sessions(connection, limit)
        return {"dry_run": True, "sessions_revoked": 0, "sessions_found": len(expired)}
    revoked = repository.cleanup_expired_sessions(connection, limit)
    return {"dry_run": False, "sessions_revoked": len(revoked)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Revoke expired, non-revoked auth sessions."
    )
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args(argv)

    settings = get_settings()
    try:
        with connect(settings.database_url, row_factory=dict_row) as connection:
            result = cleanup(connection, args.limit, args.dry_run)
            if not args.dry_run:
                connection.commit()
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1

    print(json.dumps({"ok": True, **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

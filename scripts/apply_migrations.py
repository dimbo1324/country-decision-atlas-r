from __future__ import annotations

import os
from pathlib import Path
import psycopg
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from scripts.migration_runner import (
    DEFAULT_DATABASE_URL,
    MIGRATION_ADVISORY_LOCK_ID,
    MIGRATIONS_DIR,
    applied_migrations,
    apply_migration,
    ensure_migration_table,
    migration_checksum as migration_checksum,
    migration_files,
    verify_or_record_checksum as verify_or_record_checksum,
)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    files = migration_files()
    if not files:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIR}.")
    with psycopg.connect(database_url) as connection:
        connection.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_ADVISORY_LOCK_ID,))
        try:
            ensure_migration_table(connection)
            seen = applied_migrations(connection)
            for path in files:
                if path.name in seen:
                    verify_or_record_checksum(connection, path, seen[path.name])
                    print(f"Skipping {path.name}")
                    continue
                print(f"Applying {path.name}")
                apply_migration(connection, path)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.execute(
                "SELECT pg_advisory_unlock(%s)", (MIGRATION_ADVISORY_LOCK_ID,)
            )
            connection.commit()


if __name__ == "__main__":
    main()

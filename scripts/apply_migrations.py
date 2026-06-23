from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import psycopg
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT_DIR / "database" / "migrations"
DEFAULT_DATABASE_URL = (
    "postgresql://country_atlas:change-me@localhost:5433/country_atlas"
)
MIGRATION_ADVISORY_LOCK_ID = 2727268367744705


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def ensure_migration_table(connection: psycopg.Connection[Any]) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            checksum TEXT,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    connection.execute(
        "ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum TEXT"
    )


def applied_migrations(connection: psycopg.Connection[Any]) -> dict[str, str | None]:
    cursor = connection.execute("SELECT version, checksum FROM schema_migrations")
    return {
        str(row[0]): str(row[1]) if row[1] is not None else None
        for row in cursor.fetchall()
    }


def migration_checksum(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def apply_migration(connection: psycopg.Connection[Any], path: Path) -> None:
    version = path.name
    sql = path.read_text(encoding="utf-8")
    checksum = migration_checksum(path)
    with connection.transaction():
        connection.execute(sql)
        connection.execute(
            "INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)",
            (version, checksum),
        )


def verify_or_record_checksum(
    connection: psycopg.Connection[Any], path: Path, stored_checksum: str | None
) -> None:
    checksum = migration_checksum(path)
    if stored_checksum is None:
        connection.execute(
            "UPDATE schema_migrations SET checksum = %s WHERE version = %s",
            (checksum, path.name),
        )
        print(f"Recorded checksum for {path.name}")
        return
    if stored_checksum != checksum:
        raise RuntimeError(
            f"Checksum mismatch for applied migration {path.name}: "
            f"stored={stored_checksum} current={checksum}"
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

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg

ROOT_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT_DIR / "database" / "migrations"
DEFAULT_DATABASE_URL = "postgresql://country_atlas:change-me@localhost:5433/country_atlas"


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def ensure_migration_table(connection: psycopg.Connection[Any]) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def applied_versions(connection: psycopg.Connection[Any]) -> set[str]:
    cursor = connection.execute("SELECT version FROM schema_migrations")
    return {str(row[0]) for row in cursor.fetchall()}


def apply_migration(connection: psycopg.Connection[Any], path: Path) -> None:
    version = path.name
    sql = path.read_text(encoding="utf-8")
    with connection.transaction():
        connection.execute(sql)
        connection.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
            (version,),
        )


def main() -> None:
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    files = migration_files()
    if not files:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIR}.")
    with psycopg.connect(database_url) as connection:
        ensure_migration_table(connection)
        seen = applied_versions(connection)
        for path in files:
            if path.name in seen:
                print(f"Skipping {path.name}")
                continue
            print(f"Applying {path.name}")
            apply_migration(connection, path)
        connection.commit()


if __name__ == "__main__":
    main()

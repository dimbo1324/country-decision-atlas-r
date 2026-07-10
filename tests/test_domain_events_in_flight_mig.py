"""Schema assertions for the domain events in-flight status migration (AE-4)."""

from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/053_domain_events_in_flight.sql"
).read_text(encoding="utf-8")


def test_migration_adds_locked_at_column() -> None:
    assert "ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ" in MIGRATION_SQL


def test_migration_widens_status_check_with_in_flight() -> None:
    assert "DROP CONSTRAINT IF EXISTS domain_events_status_check" in (
        MIGRATION_SQL
    )
    assert "'pending', 'in_flight', 'relayed', 'skipped', 'failed'" in (
        MIGRATION_SQL
    )


def test_migration_indexes_in_flight_rows() -> None:
    assert (
        "CREATE INDEX IF NOT EXISTS idx_domain_events_in_flight"
        in MIGRATION_SQL
    )

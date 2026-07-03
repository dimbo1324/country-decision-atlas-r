"""Schema assertions for the platform runtime foundations migration and its public data-journal flag."""

from pathlib import Path


MIGRATION = Path("database/migrations/031_platform_runtime.sql")


def test_platform_runtime_migration_exists() -> None:
    assert MIGRATION.exists()


def test_data_journal_flag_enabled_publicly() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "data_journal_enabled" in sql
    assert "status = 'enabled'" in sql
    assert "access_tier = 'public'" in sql
    assert "default_enabled = TRUE" in sql
    assert "ON CONFLICT (feature_key, access_tier)" in sql

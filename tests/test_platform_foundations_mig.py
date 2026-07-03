"""Schema assertions for the platform foundations migration: analytics events and feature-flag tables."""

from pathlib import Path


MIGRATION = Path("database/migrations/030_platform_foundations.sql")


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_platform_foundations_migration_exists() -> None:
    assert MIGRATION.exists()


def test_analytics_events_table_exists_in_migration() -> None:
    assert "CREATE TABLE IF NOT EXISTS analytics_events" in _sql()


def test_feature_flags_table_exists_in_migration() -> None:
    assert "CREATE TABLE IF NOT EXISTS feature_flags" in _sql()


def test_feature_access_rules_table_exists_in_migration() -> None:
    assert "CREATE TABLE IF NOT EXISTS feature_access_rules" in _sql()


def test_analytics_enabled_seeded() -> None:
    assert "'analytics_enabled'" in _sql()
    assert "'Anonymous analytics'" in _sql()


def test_feature_access_rules_seeded_from_feature_flags() -> None:
    sql = _sql()
    assert "INSERT INTO feature_access_rules" in sql
    assert "FROM feature_flags" in sql


def test_metadata_pii_constraint_exists() -> None:
    sql = _sql()
    assert "analytics_events_no_pii_metadata_keys_check" in sql
    assert "'email'" in sql
    assert "'user_agent'" in sql
    assert "'admin_token'" in sql


def test_metadata_object_constraint_exists() -> None:
    assert "analytics_events_metadata_object_check" in _sql()


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("CREATE TABLE IF NOT EXISTS") == 3
    assert "CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at" in sql
    assert "ON CONFLICT (key) DO NOTHING" in sql
    assert "ON CONFLICT (feature_key, access_tier) DO NOTHING" in sql

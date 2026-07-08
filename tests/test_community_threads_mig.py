"""Schema assertions for the Community Threads migration: table shape, lifecycle constraints, and seeded config."""

from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/051_community_threads_v1.sql"
).read_text(encoding="utf-8")


def test_community_threads_migration_creates_required_tables() -> None:
    for table in ["contact_threads", "thread_messages"]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in MIGRATION_SQL


def test_community_threads_migration_enforces_lifecycle_constraints() -> None:
    assert "contact_threads_status_check" in MIGRATION_SQL
    assert "status IN ('open', 'closed', 'frozen')" in MIGRATION_SQL
    assert "contact_threads_closed_state_check" in MIGRATION_SQL
    assert "thread_messages_body_check" in MIGRATION_SQL
    assert "BTRIM(body) <> ''" in MIGRATION_SQL


def test_community_threads_migration_adds_polling_index() -> None:
    assert "idx_thread_messages_thread_created" in MIGRATION_SQL
    assert "ON thread_messages (thread_id, created_at, id)" in MIGRATION_SQL


def test_community_threads_migration_seeds_methodology_parameter() -> None:
    assert "board.max_thread_messages_per_day" in MIGRATION_SQL
    assert "ON CONFLICT (version, param_key) DO NOTHING" in MIGRATION_SQL


def test_community_threads_migration_seeds_feature_flag() -> None:
    assert "community_threads_enabled" in MIGRATION_SQL
    assert "ON CONFLICT (key) DO NOTHING" in MIGRATION_SQL
    assert "ON CONFLICT (feature_key, access_tier) DO NOTHING" in MIGRATION_SQL

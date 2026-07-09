"""Schema assertions for the session security hardening migration (AE-3)."""

from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/052_session_security_hardening.sql"
).read_text(encoding="utf-8")


def test_session_security_migration_adds_rotation_columns() -> None:
    for column in (
        "ADD COLUMN IF NOT EXISTS previous_token_hash TEXT",
        "ADD COLUMN IF NOT EXISTS previous_token_expires_at TIMESTAMPTZ",
        "ADD COLUMN IF NOT EXISTS rotated_at TIMESTAMPTZ",
    ):
        assert column in MIGRATION_SQL


def test_session_security_migration_adds_device_visibility_columns() -> None:
    for column in (
        "ADD COLUMN IF NOT EXISTS device_label TEXT",
        "ADD COLUMN IF NOT EXISTS ip_display TEXT",
        "ADD COLUMN IF NOT EXISTS device_fingerprint_hash TEXT",
    ):
        assert column in MIGRATION_SQL


def test_session_security_migration_creates_notifications_table() -> None:
    assert (
        "CREATE TABLE IF NOT EXISTS user_security_notifications"
        in MIGRATION_SQL
    )
    assert "'new_device_login'" in MIGRATION_SQL


def test_session_security_migration_widens_audit_action_check() -> None:
    assert "DROP CONSTRAINT IF EXISTS audit_events_action_check" in (
        MIGRATION_SQL
    )
    assert "new_device_login" in MIGRATION_SQL


def test_session_security_migration_indexes_previous_token_hash() -> None:
    assert (
        "CREATE INDEX IF NOT EXISTS idx_auth_sessions_previous_token_hash"
        in MIGRATION_SQL
    )

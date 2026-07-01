from pathlib import Path


MIGRATION = Path("database/migrations/037_decision_personalization_closeout_v1.sql")


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_closeout_migration_file_exists() -> None:
    assert MIGRATION.exists()


def test_closeout_migration_enables_decision_wizard() -> None:
    sql = _sql()
    assert "UPDATE feature_flags" in sql
    assert "'decision_wizard_enabled'" in sql
    assert "status = 'enabled'" in sql
    assert "default_enabled = TRUE" in sql
    assert "access_tier = 'public'" in sql


def test_closeout_migration_enables_public_access_rule() -> None:
    sql = _sql()
    assert "INSERT INTO feature_access_rules" in sql
    assert "'decision_wizard_enabled'" in sql
    assert "'public'" in sql
    assert "TRUE" in sql
    assert "ON CONFLICT (feature_key, access_tier)" in sql


def test_closeout_migration_does_not_add_user_storage_tables() -> None:
    sql = _sql()
    for forbidden in (
        "user_decision_profiles",
        "saved_weight_sets",
        "wizard_sessions",
        "decision_customization_history",
    ):
        assert forbidden not in sql

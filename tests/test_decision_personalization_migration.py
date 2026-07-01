from pathlib import Path


MIGRATION = Path("database/migrations/036_decision_personalization_v1.sql")


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_file_exists() -> None:
    assert MIGRATION.exists()


def test_decision_personalization_enabled_seeded() -> None:
    sql = _sql()
    assert "'decision_personalization_enabled'" in sql
    assert "'enabled'" in sql


def test_decision_wizard_enabled_seeded() -> None:
    sql = _sql()
    assert "'decision_wizard_enabled'" in sql
    assert "'disabled'" in sql


def test_feature_access_rules_seeded() -> None:
    sql = _sql()
    assert "INSERT INTO feature_access_rules" in sql
    assert "'decision_personalization_enabled'" in sql
    assert "'decision_wizard_enabled'" in sql


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("INSERT INTO feature_flags") == 1
    assert "ON CONFLICT (key) DO UPDATE" in sql
    assert sql.count("INSERT INTO feature_access_rules") == 1
    assert "ON CONFLICT (feature_key, access_tier)" in sql


def test_migration_does_not_add_user_storage_tables() -> None:
    sql = _sql()
    for forbidden in (
        "user_decision_profiles",
        "saved_weight_sets",
        "wizard_sessions",
        "decision_customization_history",
    ):
        assert forbidden not in sql


def test_migration_does_not_touch_other_domains() -> None:
    sql = _sql()
    for forbidden in (
        "country_cii_scores",
        "country_scores",
        "country_score_breakdowns",
        "scenario_metric_weights",
        "persona_metric_modifiers",
    ):
        assert forbidden not in sql

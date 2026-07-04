"""Schema assertions for the AI-grounded assistant foundation migration."""

from pathlib import Path


MIGRATION_SQL = Path("database/migrations/041_ai_assistant.sql").read_text(
    encoding="utf-8"
)


def test_migration_creates_ai_interaction_logs() -> None:
    assert "CREATE TABLE IF NOT EXISTS ai_interaction_logs" in MIGRATION_SQL
    assert "CONSTRAINT ai_interaction_logs_request_type_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_interaction_logs_ai_mode_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_interaction_logs_status_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_interaction_logs_counts_check" in MIGRATION_SQL
    assert (
        "CONSTRAINT ai_interaction_logs_metadata_object_check" in MIGRATION_SQL
    )


def test_migration_adds_ai_feature_flags() -> None:
    for feature_key in [
        "ai_augmentation",
        "ai_grounded_qa",
        "ai_explain_number",
        "ai_nl_decision",
    ]:
        assert feature_key in MIGRATION_SQL
    assert "ON CONFLICT (key) DO UPDATE" in MIGRATION_SQL
    assert "ON CONFLICT (feature_key, access_tier)" in MIGRATION_SQL


def test_migration_does_not_touch_trusted_score_tables() -> None:
    forbidden = [
        "ALTER TABLE country_scores",
        "ALTER TABLE country_score_breakdowns",
        "ALTER TABLE country_trust_scores",
        "ALTER TABLE country_drift_snapshots",
        "ALTER TABLE country_platform_metrics",
    ]
    for statement in forbidden:
        assert statement not in MIGRATION_SQL


def test_migration_log_safety_constraints() -> None:
    for forbidden_key in ["email", "phone", "telegram_user_id", "ip_address"]:
        assert forbidden_key in MIGRATION_SQL
    assert "full user prompt" not in MIGRATION_SQL

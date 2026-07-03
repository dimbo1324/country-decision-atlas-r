from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/041_ai_assistant.sql"
).read_text(encoding="utf-8")


def test_ai_feature_flags_are_public_enabled_by_default() -> None:
    for feature_key in [
        "ai_augmentation",
        "ai_grounded_qa",
        "ai_explain_number",
        "ai_nl_decision",
    ]:
        assert f"'{feature_key}'" in MIGRATION_SQL
    assert "'enabled'" in MIGRATION_SQL
    assert "'public'" in MIGRATION_SQL
    assert "TRUE" in MIGRATION_SQL

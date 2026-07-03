from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/045_migration_board_companions_v1.sql"
).read_text(encoding="utf-8")


def test_migration_board_migration_creates_required_tables() -> None:
    for table in [
        "migration_board_posts",
        "migration_board_contact_requests",
        "migration_board_reports",
        "migration_board_blocks",
        "migration_board_post_tags",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in MIGRATION_SQL


def test_migration_board_migration_adds_feature_flags() -> None:
    for feature_key in [
        "migration_board_enabled",
        "companion_matching_enabled",
        "contact_requests_enabled",
        "migration_board_public_listing_enabled",
        "migration_board_moderation_enabled",
    ]:
        assert feature_key in MIGRATION_SQL
    assert "ON CONFLICT (key) DO NOTHING" in MIGRATION_SQL


def test_migration_board_migration_enforces_privacy_lifecycle_constraints() -> None:
    assert "migration_board_posts_published_state_check" in MIGRATION_SQL
    assert "risk_acknowledged IS TRUE" in MIGRATION_SQL
    assert "legal_disclaimer_acknowledged IS TRUE" in MIGRATION_SQL
    assert "migration_board_contact_requests_no_self_check" in MIGRATION_SQL
    assert "idx_migration_board_contact_requests_one_pending" in MIGRATION_SQL
    assert "migration_board_blocks_no_self_check" in MIGRATION_SQL

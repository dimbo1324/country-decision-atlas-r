from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/042_ai_drafts_community_foundation_v1.sql"
).read_text(encoding="utf-8")


def test_migration_creates_qna_tables() -> None:
    assert "CREATE TABLE IF NOT EXISTS qna_questions" in MIGRATION_SQL
    assert "CREATE TABLE IF NOT EXISTS qna_answers" in MIGRATION_SQL
    assert "CREATE TABLE IF NOT EXISTS qna_votes" in MIGRATION_SQL
    assert "CONSTRAINT qna_questions_status_check" in MIGRATION_SQL
    assert "CONSTRAINT qna_answers_status_check" in MIGRATION_SQL
    assert "CONSTRAINT qna_votes_vote_type_check" in MIGRATION_SQL
    assert "CONSTRAINT qna_votes_unique_identity_vote" in MIGRATION_SQL


def test_migration_creates_data_error_reports_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS data_error_reports" in MIGRATION_SQL
    assert "CONSTRAINT data_error_reports_type_check" in MIGRATION_SQL
    assert "CONSTRAINT data_error_reports_status_check" in MIGRATION_SQL


def test_migration_creates_user_story_ratings_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS user_story_ratings" in MIGRATION_SQL
    assert "CONSTRAINT user_story_ratings_status_check" in MIGRATION_SQL
    assert "CONSTRAINT user_story_ratings_score_range_check" in MIGRATION_SQL


def test_migration_identity_types_allow_telegram_and_anonymous_session() -> None:
    assert "'telegram', 'anonymous_session', 'system'" in MIGRATION_SQL


def test_migration_adds_community_feature_flags() -> None:
    for feature_key in [
        "community_enabled",
        "community_qna_enabled",
        "community_error_reports_enabled",
        "community_story_ratings_enabled",
    ]:
        assert feature_key in MIGRATION_SQL
    assert "ON CONFLICT (key) DO UPDATE" in MIGRATION_SQL
    assert "ON CONFLICT (feature_key, access_tier)" in MIGRATION_SQL


def test_migration_moderation_statuses_include_pending_and_published() -> None:
    assert "'pending', 'review', 'published', 'rejected', 'archived'" in MIGRATION_SQL


def test_migration_is_idempotent_style() -> None:
    assert MIGRATION_SQL.count("CREATE TABLE IF NOT EXISTS") >= 7
    assert "CREATE INDEX IF NOT EXISTS" in MIGRATION_SQL

"""Schema assertions for the episode 12-13 closeout migration's community Q&A indexes."""

from pathlib import Path


MIGRATION_SQL = Path("database/migrations/043_episode_12_13_closeout.sql").read_text(
    encoding="utf-8"
)


def test_closeout_migration_adds_required_community_indexes() -> None:
    assert "CREATE INDEX IF NOT EXISTS idx_qna_questions_route" in MIGRATION_SQL
    assert "CREATE INDEX IF NOT EXISTS idx_qna_answers_created_at" in MIGRATION_SQL
    assert "CREATE INDEX IF NOT EXISTS idx_qna_votes_identity" in MIGRATION_SQL
    assert "WHERE route_id IS NOT NULL" in MIGRATION_SQL

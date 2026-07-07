"""Schema assertions for the Country Contribution v1 migration."""

from pathlib import Path


MIGRATION_SQL = Path(
    "database/migrations/050_country_contribution_v1.sql"
).read_text(encoding="utf-8")


def test_country_contribution_migration_adds_is_demo_flag() -> None:
    assert (
        "ADD COLUMN IF NOT EXISTS is_demo BOOLEAN NOT NULL DEFAULT FALSE"
        in (MIGRATION_SQL)
    )


def test_country_contribution_migration_creates_proposals_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS country_proposals" in MIGRATION_SQL


def test_country_contribution_migration_enforces_lifecycle_constraint() -> None:
    assert "CONSTRAINT country_proposals_status_check" in MIGRATION_SQL
    assert "'draft', 'review', 'published', 'archived', 'rejected'" in (
        MIGRATION_SQL
    )


def test_country_contribution_migration_requires_unique_country_link() -> None:
    assert "country_id UUID NOT NULL UNIQUE REFERENCES countries(id)" in (
        MIGRATION_SQL
    )


def test_country_contribution_migration_conserves_demo_countries() -> None:
    assert (
        "UPDATE countries SET is_demo = TRUE WHERE slug IN "
        "('russia', 'uruguay', 'argentina')" in MIGRATION_SQL
    )
    assert "DELETE FROM" not in MIGRATION_SQL.upper()


def test_country_contribution_migration_adds_feature_flag() -> None:
    assert "country_contribution_enabled" in MIGRATION_SQL
    assert "ON CONFLICT (key) DO NOTHING" in MIGRATION_SQL
    assert "ON CONFLICT (feature_key, access_tier) DO NOTHING" in MIGRATION_SQL


def test_country_contribution_migration_has_curator_and_moderation_fields() -> (
    None
):
    for column in (
        "curator_user_id UUID REFERENCES users(id)",
        "readiness_snapshot JSONB",
        "moderated_by UUID REFERENCES users(id)",
        "moderation_reason TEXT",
    ):
        assert column in MIGRATION_SQL

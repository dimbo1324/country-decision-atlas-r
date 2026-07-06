"""Schema assertions for the Author Metrics v1 migration."""

from pathlib import Path


MIGRATION_SQL = Path("database/migrations/049_author_metrics_v1.sql").read_text(
    encoding="utf-8"
)


def test_author_metrics_migration_creates_required_tables() -> None:
    for table in [
        "author_metric_definitions",
        "author_metric_values",
        "author_subscriptions",
        "author_reputation",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in MIGRATION_SQL


def test_author_metrics_migration_adds_feature_flag() -> None:
    assert "author_metrics_enabled" in MIGRATION_SQL
    assert "ON CONFLICT (key) DO NOTHING" in MIGRATION_SQL
    assert "ON CONFLICT (feature_key, access_tier) DO NOTHING" in MIGRATION_SQL


def test_author_metrics_migration_seeds_methodology_parameters() -> None:
    assert "author_metrics.min_methodology_length" in MIGRATION_SQL
    assert "author_metrics.min_country_coverage" in MIGRATION_SQL
    assert "ON CONFLICT (version, param_key) DO NOTHING" in MIGRATION_SQL


def test_author_metrics_migration_enforces_lifecycle_and_value_constraints() -> (
    None
):
    assert "CONSTRAINT author_metric_definitions_status_check" in MIGRATION_SQL
    assert "'draft', 'review', 'published', 'archived', 'rejected'" in (
        MIGRATION_SQL
    )
    assert "CONSTRAINT author_metric_values_source_check" in MIGRATION_SQL
    assert "source_url IS NOT NULL OR is_personal_experience" in MIGRATION_SQL
    assert "CONSTRAINT author_subscriptions_target_check" in MIGRATION_SQL
    assert (
        "metric_id IS NOT NULL OR author_user_id IS NOT NULL" in MIGRATION_SQL
    )
    assert "uq_author_metric_definitions_author_slug" in MIGRATION_SQL
    assert "uq_author_metric_values_metric_country" in MIGRATION_SQL


def test_author_metrics_migration_supports_fork_lineage() -> None:
    assert "forked_from_id UUID REFERENCES author_metric_definitions(id)" in (
        MIGRATION_SQL
    )

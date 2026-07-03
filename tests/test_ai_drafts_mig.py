"""Schema assertions for the AI drafts and contradiction-candidates migration."""

from pathlib import Path


MIGRATION_SQL = Path("database/migrations/042_ai_drafts_community.sql").read_text(
    encoding="utf-8"
)


def test_migration_creates_ai_drafts_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS ai_drafts" in MIGRATION_SQL
    assert "CONSTRAINT ai_drafts_draft_type_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_drafts_status_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_drafts_confidence_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_drafts_citations_array_check" in MIGRATION_SQL
    assert "CONSTRAINT ai_drafts_input_context_object_check" in MIGRATION_SQL


def test_migration_creates_contradiction_candidates_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS contradiction_candidates" in MIGRATION_SQL
    assert "CONSTRAINT contradiction_candidates_severity_check" in MIGRATION_SQL
    assert "CONSTRAINT contradiction_candidates_status_check" in MIGRATION_SQL


def test_migration_expands_domain_event_types() -> None:
    assert "ai_draft.ready" in MIGRATION_SQL
    assert "contradiction_candidate.created" in MIGRATION_SQL
    assert "domain_events_event_type_check" in MIGRATION_SQL


def test_migration_default_statuses_are_needs_review() -> None:
    assert "status TEXT NOT NULL DEFAULT 'needs_review'" in MIGRATION_SQL


def test_migration_does_not_touch_trusted_score_tables() -> None:
    forbidden = [
        "ALTER TABLE country_scores",
        "ALTER TABLE country_score_breakdowns",
        "ALTER TABLE country_cii_scores",
        "ALTER TABLE country_trust_scores",
        "ALTER TABLE country_drift_snapshots",
        "ALTER TABLE country_platform_metrics",
        "ALTER TABLE scenario_metric_weights",
    ]
    for statement in forbidden:
        assert statement not in MIGRATION_SQL

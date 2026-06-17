from pathlib import Path

SEED_SQL = Path("database/migrations/004_seed_country_decision_data.sql").read_text(
    encoding="utf-8"
)
SCHEMA_SQL = Path("database/migrations/003_country_decision_engine.sql").read_text(encoding="utf-8")


def test_seed_contains_required_countries_and_scenarios() -> None:
    assert "'russia'" in SEED_SQL
    assert "'uruguay'" in SEED_SQL
    for slug in [
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ]:
        assert slug in SEED_SQL


def test_seed_contains_score_breakdown_criteria() -> None:
    for criterion in [
        "legalization_score",
        "long_term_status_score",
        "cost_of_living_score",
        "safety_score",
        "business_score",
        "legal_stability_score",
        "source_quality_score",
    ]:
        assert criterion in SEED_SQL


def test_schema_contains_decision_engine_tables() -> None:
    for table_name in [
        "country_cards",
        "country_score_breakdowns",
        "user_stories",
        "user_story_documents",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table_name}" in SCHEMA_SQL


def test_synthetic_user_stories_are_marked() -> None:
    assert "Synthetic example for MVP demonstration only." in SEED_SQL
    assert "TRUE" in SEED_SQL

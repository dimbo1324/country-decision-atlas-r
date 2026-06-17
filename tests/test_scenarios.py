from tests.test_seed_data import SEED_SQL


def test_required_decision_scenarios_are_seeded() -> None:
    assert SEED_SQL.count("relocation_residence") >= 1
    assert SEED_SQL.count("permanent_residence_citizenship") >= 1
    assert SEED_SQL.count("low_budget_living") >= 1
    assert SEED_SQL.count("business_self_employment") >= 1
    assert SEED_SQL.count("safety_political_risk") >= 1

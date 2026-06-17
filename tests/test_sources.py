from tests.test_openapi_contract import load_contract
from tests.test_seed_data import SEED_SQL


def test_sources_and_evidence_are_seeded_and_routed() -> None:
    paths = load_contract()["paths"]

    assert "/api/v1/sources" in paths
    assert "/api/v1/sources/{source_id}/evidence" in paths
    assert SEED_SQL.count("https://example.invalid/") >= 20
    assert "decision_evidence" in SEED_SQL

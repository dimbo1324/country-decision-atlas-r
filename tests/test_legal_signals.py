from tests.test_openapi_contract import load_contract
from tests.test_seed_data import SEED_SQL


def test_legal_signal_paths_and_seed_sources_exist() -> None:
    paths = load_contract()["paths"]

    assert "/api/v1/legal-signals" in paths
    assert "/api/v1/legal-signals/{signal_id}/evidence" in paths
    assert "source_id" in SEED_SQL
    assert "'published'" in SEED_SQL

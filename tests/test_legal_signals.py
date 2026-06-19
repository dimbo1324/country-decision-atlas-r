from tests.test_openapi_contract import load_contract
from tests.test_seed_data import SEED_SQL, SOURCE_DEPTH_SQL


def test_legal_signal_paths_and_seed_sources_exist() -> None:
    paths = load_contract()["paths"]

    assert "/api/v1/legal-signals" in paths
    assert "/api/v1/legal-signals/{signal_id}/evidence" in paths
    assert "source_id" in SEED_SQL
    assert "'published'" in SEED_SQL


def test_source_depth_legal_signals_are_source_backed() -> None:
    assert SOURCE_DEPTH_SQL.count("INSERT INTO legal_signals") == 1
    assert SOURCE_DEPTH_SQL.count("source_url") >= 3
    assert "ON CONFLICT (country_id, title) DO UPDATE" in SOURCE_DEPTH_SQL
    assert "JOIN sources s ON s.url = lsr.source_url" in SOURCE_DEPTH_SQL
    assert "legal_signal_id" in SOURCE_DEPTH_SQL

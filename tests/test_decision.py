"""Decision engine contract paths exist."""

from tests.test_openapi_contract import load_contract


def test_decision_contract_paths_exist() -> None:
    paths = load_contract()["paths"]
    schemas = load_contract()["components"]["schemas"]

    assert "/api/v1/decision/compare" in paths
    assert "/api/v1/decision/run" in paths
    assert "DecisionCompareInput" in schemas
    assert "DecisionRunResponse" in schemas

from country_decision_atlas_contracts import HealthResponse
def test_health_response_contract() -> None:
    response = HealthResponse(status="ok", service="api", environment="test")
    assert response.status == "ok"
    assert response.service == "api"
    assert response.environment == "test"

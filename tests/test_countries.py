from tests.test_openapi_contract import load_contract


def test_country_paths_exist() -> None:
    paths = load_contract()["paths"]

    assert "/api/v1/countries" in paths
    assert "/api/v1/countries/{country_slug}/card" in paths
    assert "/api/v1/countries/{country_slug}/sources" in paths

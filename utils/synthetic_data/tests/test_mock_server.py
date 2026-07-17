from __future__ import annotations

from fastapi.testclient import TestClient
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input
from utils.synthetic_data.core.world_models import SyntheticWorld
from utils.synthetic_data.mock_server.app import create_app


def _generate_world(seed: int = 42017) -> SyntheticWorld:
    return WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(
            seed=seed,
            profile="balanced",
            scale="small",
            generated_on="2026-01-01",
        )
    )


def _client(world: SyntheticWorld | None = None) -> TestClient:
    return TestClient(create_app(world or _generate_world()))


def test_root_reports_dataset_and_countries() -> None:
    world = _generate_world()
    client = _client(world)

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_id"] == world.metadata.dataset_id
    assert set(payload["countries"]) == {c.slug for c in world.countries}
    assert payload["fictional_notice"] == "SYNTHETIC TEST DATA - NOT REAL"


def test_every_response_carries_the_synthetic_data_header() -> None:
    client = _client()

    response = client.get("/api/v1/countries")

    assert response.headers["x-synthetic-data"] == "true"


def test_list_countries_returns_all_with_pagination() -> None:
    world = _generate_world()
    client = _client(world)

    response = client.get("/api/v1/countries")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == len(world.countries)
    assert payload["pagination"] == {
        "limit": 50,
        "offset": 0,
        "total": len(world.countries),
    }
    assert payload["locale"]["resolved_locale"] == "en"
    item = payload["items"][0]
    assert set(item) == {
        "id",
        "slug",
        "iso2",
        "iso3",
        "name",
        "official_name",
        "region",
        "subregion",
        "capital",
        "currency_code",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_list_countries_respects_limit_and_offset() -> None:
    client = _client()

    response = client.get("/api/v1/countries", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    assert payload["pagination"]["limit"] == 1
    assert payload["pagination"]["offset"] == 1


def test_get_country_returns_matching_slug() -> None:
    world = _generate_world()
    slug = world.countries[0].slug
    client = _client(world)

    response = client.get(f"/api/v1/countries/{slug}")

    assert response.status_code == 200
    assert response.json()["item"]["slug"] == slug


def test_get_country_404_uses_the_real_error_envelope() -> None:
    client = _client()

    response = client.get("/api/v1/countries/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "country_not_found",
            "message": "Country not found.",
            "details": {"country_slug": "does-not-exist"},
        }
    }


def test_get_country_profile_uses_the_articles_summary() -> None:
    world = _generate_world()
    slug = world.countries[0].slug
    article = next(
        a
        for a in world.articles
        if a.country_id == world.countries[0].country_id
    )
    client = _client(world)

    response = client.get(f"/api/v1/countries/{slug}/profile")

    assert response.status_code == 200
    assert response.json()["item"]["summary"] == article.summary


def test_get_country_profile_404_for_unknown_slug() -> None:
    client = _client()

    response = client.get("/api/v1/countries/does-not-exist/profile")

    assert response.status_code == 404


def test_get_country_trust_reuses_data_confidence_as_trust_score() -> None:
    world = _generate_world()
    country = world.countries[0]
    client = _client(world)

    response = client.get(f"/api/v1/countries/{country.slug}/trust")

    assert response.status_code == 200
    payload = response.json()
    assert payload["trust_score"] == float(
        country.current_metrics["data_confidence"]
    )
    assert payload["confidence"] in {"high", "medium", "low"}
    assert "SYNTHETIC TEST DATA" in payload["disclaimer"]


def test_get_country_trust_404_for_unknown_slug() -> None:
    client = _client()

    response = client.get("/api/v1/countries/does-not-exist/trust")

    assert response.status_code == 404


def test_get_country_cii_uses_only_synthetic_metric_slugs() -> None:
    world = _generate_world()
    slug = world.countries[0].slug
    client = _client(world)

    response = client.get(f"/api/v1/countries/{slug}/cii")

    assert response.status_code == 200
    payload = response.json()
    assert 0.0 <= payload["overall_score"] <= 100.0
    assert payload["confidence"] in {"high", "medium", "low"}
    assert all(
        metric["slug"].startswith("syn_") for metric in payload["metrics"]
    )
    assert any(
        "SYNTHETIC TEST DATA - NOT REAL" in warning
        for warning in payload["quality_warnings"]
    )


def test_get_country_cii_404_for_unknown_slug() -> None:
    client = _client()

    response = client.get("/api/v1/countries/does-not-exist/cii")

    assert response.status_code == 404


def test_compare_countries_is_not_swallowed_by_the_country_slug_route() -> None:
    """Regression guard: `/countries/compare` must resolve to the compare
    handler, not be matched as `{country_slug}="compare"` by a route
    registered earlier -- this exact bug was caught manually before this
    test existed."""
    world = _generate_world()
    slug_a, slug_b = world.countries[0].slug, world.countries[1].slug
    client = _client(world)

    response = client.get(
        "/api/v1/countries/compare",
        params={"countries": f"{slug_a},{slug_b}", "scenario": "relocation"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["slug"] == "relocation"
    assert {c["slug"] for c in payload["countries"]} == {slug_a, slug_b}
    assert len(payload["metrics"]) == 7
    for metric in payload["metrics"]:
        assert len(metric["values"]) == 2


def test_compare_countries_rejects_wrong_country_count() -> None:
    world = _generate_world()
    slug = world.countries[0].slug
    client = _client(world)

    response = client.get(
        "/api/v1/countries/compare",
        params={"countries": slug, "scenario": "relocation"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "countries_count_invalid"


def test_compare_countries_requires_scenario() -> None:
    world = _generate_world()
    slug_a, slug_b = world.countries[0].slug, world.countries[1].slug
    client = _client(world)

    response = client.get(
        "/api/v1/countries/compare",
        params={"countries": f"{slug_a},{slug_b}", "scenario": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "scenario_required"


def test_compare_countries_404_for_unknown_slug() -> None:
    world = _generate_world()
    slug = world.countries[0].slug
    client = _client(world)

    response = client.get(
        "/api/v1/countries/compare",
        params={
            "countries": f"{slug},does-not-exist",
            "scenario": "relocation",
        },
    )

    assert response.status_code == 404


def test_get_country_sources_returns_the_countrys_own_source() -> None:
    world = _generate_world()
    country = world.countries[0]
    client = _client(world)

    response = client.get(f"/api/v1/countries/{country.slug}/sources")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == len(country.sources)
    assert payload["items"][0]["url"] == country.sources[0].url


def test_get_country_sources_404_for_unknown_slug() -> None:
    client = _client()

    response = client.get("/api/v1/countries/does-not-exist/sources")

    assert response.status_code == 404


def test_search_matches_country_name() -> None:
    world = _generate_world()
    country = world.countries[0]
    client = _client(world)

    response = client.get("/api/v1/search", params={"q": country.name[:4]})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(
        item["country_slug"] == country.slug for item in payload["items"]
    )


def test_search_returns_empty_for_a_non_matching_query() -> None:
    client = _client()

    response = client.get(
        "/api/v1/search", params={"q": "zzz_no_such_text_zzz"}
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_cors_allows_the_configured_origin() -> None:
    world = _generate_world()
    app = create_app(world, cors_origins=("http://localhost:3000",))
    client = TestClient(app)

    response = client.get(
        "/api/v1/countries",
        headers={"Origin": "http://localhost:3000"},
    )

    assert (
        response.headers.get("access-control-allow-origin")
        == "http://localhost:3000"
    )

from app.core.database import get_connection
from app.core.errors import api_error
from app.main import app
from app.schemas.common import TranslationStatus, locale_resolution
from app.schemas.country_pairs import (
    CountryPairCompatibility,
    CountryPairCompatibilityListItem,
    CountryPairCompatibilityListResponse,
    CountryPairCompatibilityResponse,
    CountryPairCountry,
    CountryPairEvidenceRef,
    CountryPairSourceRef,
)
from app.services import country_pairs as country_pairs_service
from datetime import UTC, datetime
from fastapi.testclient import TestClient
from tests.test_openapi_contract import load_contract
from typing import Any


CONNECTION = object()
NOW = datetime(2026, 6, 1, tzinfo=UTC)


def compatibility() -> CountryPairCompatibility:
    return CountryPairCompatibility(
        label="mixed",
        confidence="low",
        freshness_status="current",
        visa_note="Visa note",
        tax_treaty_note="Tax note",
        banking_note="Banking note",
        flight_logistics_note="Flight note",
        timezone_note="Timezone note",
        language_note="Language note",
        migration_restriction_note="Migration note",
        practical_summary="Practical summary",
        last_verified_at=NOW,
    )


def pair_response(
    origin_slug: str = "russia", destination_slug: str = "uruguay"
) -> CountryPairCompatibilityResponse:
    return CountryPairCompatibilityResponse(
        origin_country=CountryPairCountry(slug=origin_slug, name="Origin", iso2="RU"),
        destination_country=CountryPairCountry(
            slug=destination_slug, name="Destination", iso2="UY"
        ),
        compatibility=compatibility(),
        sources=[
            CountryPairSourceRef(
                id="source-1",
                title="Official source",
                url="https://example.test",
                source_type="official",
                confidence="high",
                country_slug=destination_slug,
            )
        ],
        evidence=[
            CountryPairEvidenceRef(
                id="evidence-1",
                claim="Claim",
                excerpt="Excerpt",
                source_id="source-1",
                confidence="high",
                country_slug=destination_slug,
            )
        ],
        disclaimer="This is not legal advice.",
        locale=locale_resolution("en", "en", TranslationStatus.source),
    )


def list_response(origin_slug: str = "russia") -> CountryPairCompatibilityListResponse:
    return CountryPairCompatibilityListResponse(
        origin_country=CountryPairCountry(slug=origin_slug, name="Origin", iso2="RU"),
        items=[
            CountryPairCompatibilityListItem(
                destination_country=CountryPairCountry(
                    slug="uruguay", name="Uruguay", iso2="UY"
                ),
                compatibility=compatibility(),
                sources=[],
                evidence=[],
            )
        ],
        disclaimer="This is not legal advice.",
        locale=locale_resolution("en", "en", TranslationStatus.source),
    )


def get_json(path: str) -> tuple[int, dict[str, Any]]:
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    try:
        response = TestClient(app).get(path)
    finally:
        app.dependency_overrides.clear()
    return response.status_code, response.json()


def test_get_pair_success(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        country_pairs_service,
        "get_country_pair_context",
        lambda *_: pair_response(),
    )

    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=en")

    assert status == 200
    assert body["origin_country"]["slug"] == "russia"
    assert body["destination_country"]["slug"] == "uruguay"
    assert body["compatibility"]["label"] == "mixed"


def test_list_destination_compatibility_success(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        country_pairs_service,
        "list_destination_pair_contexts",
        lambda *_: list_response(),
    )

    status, body = get_json(
        "/api/v1/countries/russia/destination-compatibility?locale=en"
    )

    assert status == 200
    assert body["origin_country"]["slug"] == "russia"
    assert body["items"][0]["destination_country"]["slug"] == "uruguay"


def test_unknown_origin_returns_country_not_found(monkeypatch: Any) -> None:
    def fake(*_: Any) -> CountryPairCompatibilityResponse:
        raise api_error(404, "country_not_found", "Country not found.")

    monkeypatch.setattr(country_pairs_service, "get_country_pair_context", fake)

    status, body = get_json("/api/v1/country-pairs/unknown/uruguay?locale=en")

    assert status == 404
    assert body["error"]["code"] == "country_not_found"


def test_unknown_destination_returns_country_not_found(monkeypatch: Any) -> None:
    def fake(*_: Any) -> CountryPairCompatibilityResponse:
        raise api_error(404, "country_not_found", "Country not found.")

    monkeypatch.setattr(country_pairs_service, "get_country_pair_context", fake)

    status, body = get_json("/api/v1/country-pairs/russia/unknown?locale=en")

    assert status == 404
    assert body["error"]["code"] == "country_not_found"


def test_missing_pair_returns_country_pair_not_found(monkeypatch: Any) -> None:
    def fake(*_: Any) -> CountryPairCompatibilityResponse:
        raise api_error(404, "country_pair_not_found", "Country pair not found.")

    monkeypatch.setattr(country_pairs_service, "get_country_pair_context", fake)

    status, body = get_json("/api/v1/country-pairs/russia/argentina?locale=en")

    assert status == 404
    assert body["error"]["code"] == "country_pair_not_found"


def test_source_refs_included(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        country_pairs_service,
        "get_country_pair_context",
        lambda *_: pair_response(),
    )

    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=en")

    assert status == 200
    assert body["sources"][0]["id"] == "source-1"


def test_evidence_refs_included(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        country_pairs_service,
        "get_country_pair_context",
        lambda *_: pair_response(),
    )

    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=en")

    assert status == 200
    assert body["evidence"][0]["id"] == "evidence-1"


def test_locale_en_works(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        country_pairs_service,
        "get_country_pair_context",
        lambda *_: pair_response(),
    )

    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=en")

    assert status == 200
    assert body["locale"]["requested_locale"] == "en"


def test_locale_ru_works(monkeypatch: Any) -> None:
    def fake(
        _connection: Any, _origin: str, _destination: str, locale: str
    ) -> CountryPairCompatibilityResponse:
        response = pair_response()
        response.locale = locale_resolution(locale, "en", TranslationStatus.fallback)
        return response

    monkeypatch.setattr(country_pairs_service, "get_country_pair_context", fake)

    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=ru")

    assert status == 200
    assert body["locale"]["requested_locale"] == "ru"


def test_invalid_locale_returns_unsupported_locale() -> None:
    status, body = get_json("/api/v1/country-pairs/russia/uruguay?locale=es")

    assert status == 422
    assert body["error"]["code"] == "unsupported_locale"


def test_openapi_contains_country_pair_paths_and_schemas() -> None:
    contract = load_contract()

    assert "/api/v1/country-pairs/{origin_slug}/{destination_slug}" in contract["paths"]
    assert (
        "/api/v1/countries/{origin_slug}/destination-compatibility" in contract["paths"]
    )
    for schema_name in [
        "CountryPairCountry",
        "CountryPairSourceRef",
        "CountryPairEvidenceRef",
        "CountryPairCompatibility",
        "CountryPairCompatibilityResponse",
        "CountryPairCompatibilityListResponse",
        "CountryPairCompatibilitySummary",
        "CountryPairNote",
    ]:
        assert schema_name in contract["components"]["schemas"]

from app.core.database import get_connection
from app.core.errors import api_error
from app.main import app
from app.schemas.common import Pagination, TranslationStatus, locale_resolution
from app.schemas.routes import (
    RouteDetailResponse,
    RouteEligibility,
    RouteListItem,
    RouteListResponse,
)
from app.services import routes as routes_service
from datetime import UTC, datetime
from fastapi.testclient import TestClient
from tests.test_openapi_contract import load_contract
from typing import Any


ROUTE_ID = "11111111-1111-1111-1111-111111111111"
SOURCE_ID = "33333333-3333-3333-3333-333333333333"
EVIDENCE_ID = "44444444-4444-4444-4444-444444444444"
DOCUMENT_ID = "55555555-5555-5555-5555-555555555555"
CHECKLIST_ITEM_ID = "66666666-6666-6666-6666-666666666666"
CONNECTION = object()
NOW = datetime(2026, 6, 26, tzinfo=UTC)


def eligibility() -> RouteEligibility:
    return RouteEligibility(
        allows_work="yes",
        allows_family="unknown",
        leads_to_pr="yes",
        leads_to_citizenship="unknown",
        requires_income_proof="unknown",
        requires_local_address="yes",
        requires_criminal_record_check="unknown",
    )


def route_list_response(country_slug: str = "russia") -> RouteListResponse:
    return RouteListResponse(
        items=[
            RouteListItem(
                id=ROUTE_ID,
                country_slug=country_slug,
                route_type="temporary_residence",
                slug="temporary-residence",
                title="Temporary residence",
                summary="Summary",
                eligibility_summary="Eligibility",
                eligibility=eligibility(),
                legal_status="effective",
                status="published",
                updated_at=NOW,
            )
        ],
        pagination=Pagination(limit=50, offset=0, total=1),
        locale=locale_resolution("ru", "ru", TranslationStatus.translated),
    )


def route_detail_response(country_slug: str = "russia") -> RouteDetailResponse:
    return RouteDetailResponse(
        id=ROUTE_ID,
        country_slug=country_slug,
        route_type="temporary_residence",
        slug="temporary-residence",
        title="Temporary residence",
        summary="Summary",
        eligibility_summary="Eligibility",
        income_requirement_note="Income",
        fees_note="Fees",
        processing_time_note="Processing",
        stay_period_note="Stay",
        renewal_note="Renewal",
        tax_warning="Tax",
        legal_warning="Legal",
        eligibility=eligibility(),
        legal_status="effective",
        status="published",
        updated_at=NOW,
        documents=[
            {
                "id": DOCUMENT_ID,
                "name": "Passport",
                "is_mandatory": True,
                "note": None,
                "display_order": 1,
            }
        ],
        sources=[
            {
                "id": SOURCE_ID,
                "title": "Official source",
                "url": "https://example.test",
                "source_type": "official",
                "publisher": "Authority",
                "confidence": "high",
                "country_slug": country_slug,
            }
        ],
        evidence=[
            {
                "id": EVIDENCE_ID,
                "source_id": SOURCE_ID,
                "claim": "Claim",
                "excerpt": "Excerpt",
                "source_title": "Official source",
                "source_url": "https://example.test",
                "confidence": "high",
                "country_slug": country_slug,
            }
        ],
        checklist=[
            {
                "id": CHECKLIST_ITEM_ID,
                "step_order": 1,
                "title": "Confirm the procedure",
                "description": None,
                "document_note": None,
                "cost_note": None,
                "timing_note": None,
                "official_requirement_note": None,
                "is_required": True,
                "source_id": SOURCE_ID,
                "evidence_item_id": None,
            }
        ],
        locale=locale_resolution("ru", "ru", TranslationStatus.translated),
    )


def get_json(path: str) -> tuple[int, dict[str, Any]]:
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    try:
        response = TestClient(app).get(path)
    finally:
        app.dependency_overrides.clear()
    return response.status_code, response.json()


def test_get_russia_routes_returns_200(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "list_country_routes",
        lambda *_: route_list_response("russia"),
    )

    status, body = get_json("/api/v1/countries/russia/routes?locale=ru")

    assert status == 200
    assert body["items"][0]["country_slug"] == "russia"


def test_get_uruguay_routes_returns_200(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "list_country_routes",
        lambda *_: route_list_response("uruguay"),
    )

    status, body = get_json("/api/v1/countries/uruguay/routes?locale=ru")

    assert status == 200
    assert body["items"][0]["country_slug"] == "uruguay"


def test_get_argentina_routes_returns_200(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "list_country_routes",
        lambda *_: route_list_response("argentina"),
    )

    status, body = get_json("/api/v1/countries/argentina/routes?locale=ru")

    assert status == 200
    assert body["items"][0]["country_slug"] == "argentina"


def test_route_list_response_has_pagination_and_locale(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "list_country_routes",
        lambda *_: route_list_response(),
    )

    status, body = get_json("/api/v1/countries/russia/routes?locale=ru")

    assert status == 200
    assert body["pagination"] == {"limit": 50, "offset": 0, "total": 1}
    assert body["locale"]["requested_locale"] == "ru"


def test_route_type_filter_is_passed_to_service(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_list_country_routes(*args: Any) -> RouteListResponse:
        captured["route_type"] = args[3]
        return route_list_response()

    monkeypatch.setattr(routes_service, "list_country_routes", fake_list_country_routes)

    status, _ = get_json(
        "/api/v1/countries/russia/routes?locale=ru&route_type=temporary_residence"
    )

    assert status == 200
    assert captured["route_type"] == "temporary_residence"


def test_allows_work_filter_is_passed_to_service(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_list_country_routes(*args: Any) -> RouteListResponse:
        captured["allows_work"] = args[4]
        return route_list_response()

    monkeypatch.setattr(routes_service, "list_country_routes", fake_list_country_routes)

    status, _ = get_json("/api/v1/countries/russia/routes?locale=ru&allows_work=yes")

    assert status == 200
    assert captured["allows_work"] == "yes"


def test_allows_family_filter_is_passed_to_service(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_list_country_routes(*args: Any) -> RouteListResponse:
        captured["allows_family"] = args[5]
        return route_list_response()

    monkeypatch.setattr(routes_service, "list_country_routes", fake_list_country_routes)

    status, _ = get_json("/api/v1/countries/russia/routes?locale=ru&allows_family=yes")

    assert status == 200
    assert captured["allows_family"] == "yes"


def test_leads_to_pr_filter_is_passed_to_service(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_list_country_routes(*args: Any) -> RouteListResponse:
        captured["leads_to_pr"] = args[6]
        return route_list_response()

    monkeypatch.setattr(routes_service, "list_country_routes", fake_list_country_routes)

    status, _ = get_json("/api/v1/countries/russia/routes?locale=ru&leads_to_pr=yes")

    assert status == 200
    assert captured["leads_to_pr"] == "yes"


def test_unknown_country_returns_country_not_found(monkeypatch: Any) -> None:
    def fake_list_country_routes(*_: Any) -> RouteListResponse:
        raise api_error(404, "country_not_found", "Country not found.")

    monkeypatch.setattr(routes_service, "list_country_routes", fake_list_country_routes)

    status, body = get_json("/api/v1/countries/missing/routes?locale=ru")

    assert status == 404
    assert body["error"]["code"] == "country_not_found"


def test_get_route_detail_returns_detail(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "get_route_detail",
        lambda *_: route_detail_response(),
    )

    status, body = get_json(f"/api/v1/routes/{ROUTE_ID}?locale=ru")

    assert status == 200
    assert body["documents"][0]["name"] == "Passport"
    assert body["sources"][0]["title"] == "Official source"
    assert body["evidence"][0]["claim"] == "Claim"


def test_get_route_detail_by_slug_returns_detail(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        routes_service,
        "get_route_detail_by_slug",
        lambda *_: route_detail_response("uruguay"),
    )

    status, body = get_json(
        "/api/v1/countries/uruguay/routes/temporary-residence?locale=ru"
    )

    assert status == 200
    assert body["country_slug"] == "uruguay"


def test_get_missing_route_returns_route_not_found(monkeypatch: Any) -> None:
    def fake_get_route_detail(*_: Any) -> RouteDetailResponse:
        raise api_error(404, "route_not_found", "Route not found.")

    monkeypatch.setattr(routes_service, "get_route_detail", fake_get_route_detail)

    status, body = get_json(
        "/api/v1/routes/99999999-9999-9999-9999-999999999999?locale=ru"
    )

    assert status == 404
    assert body["error"]["code"] == "route_not_found"


def test_invalid_route_type_returns_422() -> None:
    status, body = get_json("/api/v1/countries/russia/routes?route_type=invalid")

    assert status == 422
    assert body["error"]["code"] == "validation_error"


def test_invalid_eligibility_flag_returns_422() -> None:
    status, body = get_json("/api/v1/countries/russia/routes?allows_work=maybe")

    assert status == 422
    assert body["error"]["code"] == "validation_error"


def test_invalid_locale_returns_unsupported_locale() -> None:
    status, body = get_json("/api/v1/countries/russia/routes?locale=es")

    assert status == 422
    assert body["error"]["code"] == "unsupported_locale"


def test_openapi_contains_route_paths_and_schemas() -> None:
    contract = load_contract()

    assert "/api/v1/countries/{country_slug}/routes" in contract["paths"]
    assert "/api/v1/countries/{country_slug}/routes/{route_slug}" in contract["paths"]
    assert "/api/v1/routes/{route_id}" in contract["paths"]
    for schema_name in [
        "RouteEligibility",
        "RouteDocument",
        "RouteSourceRef",
        "RouteEvidenceRef",
        "RouteListItem",
        "RouteListResponse",
        "RouteDetailResponse",
    ]:
        assert schema_name in contract["components"]["schemas"]

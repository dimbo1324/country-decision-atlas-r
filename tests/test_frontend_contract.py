from app.api.v1 import (
    admin as admin_route,
    countries as countries_route,
    decision as decision_route,
    legal_signals as legal_signals_route,
    sources as sources_route,
)
from app.core.locales import get_locale
from app.schemas.common import (
    Pagination,
    SortMeta,
    locale_resolution,
    source_locale_resolution,
)
from app.schemas.data_quality import DataQualityReport
from app.schemas.decision_engine import (
    DecisionCountryRef,
    DecisionCountryResult,
    DecisionRunMeta,
    DecisionRunRequest,
    DecisionRunResponse,
    DecisionScenarioRef,
)
from datetime import UTC, datetime
from fastapi import HTTPException
from psycopg import Connection
from tests.test_country_read_model import sample_response
from tests.test_openapi_contract import load_contract
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
NOW = datetime.now(UTC)


def test_countries_list_frontend_contract(monkeypatch: Any) -> None:
    rows = [
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "slug": "russia",
            "iso2": "RU",
            "iso3": "RUS",
            "name": "Russia",
            "official_name": None,
            "region": "Europe",
            "subregion": None,
            "capital": "Moscow",
            "currency_code": "RUB",
            "is_active": True,
            "created_at": NOW,
            "updated_at": NOW,
            "translation_status": "source",
            "resolved_locale": "en",
        },
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "slug": "uruguay",
            "iso2": "UY",
            "iso3": "URY",
            "name": "Uruguay",
            "official_name": None,
            "region": "Americas",
            "subregion": None,
            "capital": "Montevideo",
            "currency_code": "UYU",
            "is_active": True,
            "created_at": NOW,
            "updated_at": NOW,
            "translation_status": "source",
            "resolved_locale": "en",
        },
    ]
    monkeypatch.setattr(countries_route, "list_countries", lambda *_: rows)
    monkeypatch.setattr(countries_route, "count_countries", lambda *_: 2)

    result = countries_route.read_countries(CONNECTION, get_locale("en"), 50, 0)
    body = result.model_dump(mode="json")

    assert {"items", "pagination", "locale"} == set(body)
    assert {"russia", "uruguay"}.issubset({item["slug"] for item in body["items"]})
    assert body["pagination"]["total"] == 2
    assert body["locale"]["requested_locale"] == "en"


def test_country_detail_frontend_contract(monkeypatch: Any) -> None:
    row = {
        "id": "00000000-0000-0000-0000-000000000002",
        "slug": "uruguay",
        "iso2": "UY",
        "iso3": "URY",
        "name": "Uruguay",
        "official_name": None,
        "region": "Americas",
        "subregion": None,
        "capital": "Montevideo",
        "currency_code": "UYU",
        "is_active": True,
        "created_at": NOW,
        "updated_at": NOW,
        "translation_status": "source",
        "resolved_locale": "en",
    }
    monkeypatch.setattr(countries_route, "get_country", lambda *_: row)

    result = countries_route.read_country("uruguay", CONNECTION, get_locale("en"))
    body = result.model_dump(mode="json")

    assert {"item", "locale"} == set(body)
    assert body["item"]["slug"] == "uruguay"
    assert body["item"]["iso2"] == "UY"


def test_country_card_frontend_contract(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        countries_route,
        "get_country_read_model",
        lambda *_: sample_response("russia", "en"),
    )

    result = countries_route.read_country_card("russia", CONNECTION, get_locale("en"))
    body = result.model_dump(mode="json")

    assert {
        "country",
        "profile",
        "scores",
        "legal_signals",
        "sources",
        "evidence_summary",
        "user_stories_summary",
        "cii",
        "meta",
        "locale",
    } == set(body)
    assert len(body["scores"]) == 5
    assert body["scores"][0]["breakdowns"]


def test_decision_run_frontend_contract(monkeypatch: Any) -> None:
    response = DecisionRunResponse(
        scenario=DecisionScenarioRef(
            slug="relocation_residence",
            title="Relocation",
            description="Scenario",
        ),
        origin_country=DecisionCountryRef(
            id="russia-id",
            slug="russia",
            name="Russia",
            iso_code="RU",
        ),
        results=[
            DecisionCountryResult(
                rank=1,
                country=DecisionCountryRef(
                    id="uruguay-id",
                    slug="uruguay",
                    name="Uruguay",
                    iso_code="UY",
                ),
                score=78,
                score_label="strong",
                summary="Summary",
                strengths=[],
                weaknesses=[],
                risk_warnings=[],
                confidence="high",
                breakdown=[],
                sources=[],
            )
        ],
        meta=DecisionRunMeta(candidate_count=2, generated_at=NOW),
        locale=locale_resolution("en", "en", "source"),
    )
    monkeypatch.setattr(
        "app.api.v1.decision.decision_engine.run_decision", lambda *_: response
    )

    result = decision_route.run_decision(
        DecisionRunRequest(
            origin_country_slug="russia",
            candidate_country_slugs=["uruguay", "russia"],
            scenario_slug="relocation_residence",
        ),
        CONNECTION,
    )
    body = result.model_dump(mode="json")

    assert {"scenario", "origin_country", "results", "meta", "locale"} == set(body)
    assert {
        "rank",
        "country",
        "score",
        "score_label",
        "summary",
        "strengths",
        "weaknesses",
        "risk_warnings",
        "confidence",
        "breakdown",
        "sources",
        "localization",
    } == set(body["results"][0])


def test_list_endpoint_frontend_contracts(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "app.api.v1.legal_signals.decision_engine.list_legal_signals",
        lambda *_: (
            [],
            Pagination(limit=20, offset=0, total=0),
            locale_resolution("en", "en", "source"),
            SortMeta(sort="published_date", order="desc"),
        ),
    )
    monkeypatch.setattr(sources_route, "list_sources", lambda *_: [])
    monkeypatch.setattr(sources_route, "count_sources", lambda *_: 0)
    monkeypatch.setattr(sources_route, "list_evidence_items", lambda *_: [])
    monkeypatch.setattr(sources_route, "count_evidence_items", lambda *_: 0)

    legal_signals = legal_signals_route.read_legal_signals(
        CONNECTION,
        get_locale("en"),
        None,
        None,
        None,
        None,
        "published",
        "published_date",
        "desc",
        20,
        0,
    ).model_dump(mode="json")
    sources = sources_route.read_sources(
        CONNECTION,
        get_locale("en"),
        None,
        None,
        None,
        None,
        "published",
        "last_checked_at",
        "desc",
        20,
        0,
    ).model_dump(mode="json")
    evidence = sources_route.read_evidence_items(
        CONNECTION,
        get_locale("en"),
        None,
        None,
        None,
        None,
        "published",
        "retrieved_at",
        "desc",
        20,
        0,
    ).model_dump(mode="json")

    assert {"items", "pagination", "sort", "locale"} == set(legal_signals)
    assert {"items", "pagination", "sort", "locale"} == set(sources)
    assert {"items", "pagination", "sort", "locale"} == set(evidence)
    assert sources["locale"] == source_locale_resolution("en").model_dump(mode="json")


def test_data_quality_report_frontend_contract(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        admin_route,
        "build_data_quality_report",
        lambda *_: DataQualityReport(valid=True),
    )

    result = admin_route.admin_read_data_quality_report(CONNECTION, "admin")
    body = result.model_dump(mode="json")

    assert {
        "overall_status",
        "valid",
        "critical_issues_count",
        "warnings_count",
        "checks",
        "issues",
        "checked_at",
    } == set(body)
    assert body["valid"] is True


def test_unsupported_locale_frontend_error_contract() -> None:
    try:
        get_locale("es")
    except HTTPException as error:
        detail = cast(dict[str, Any], error.detail)
        assert error.status_code == 422
        assert detail["error"]["code"] == "unsupported_locale"
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_openapi_contains_frontend_critical_contract() -> None:
    contract = load_contract()
    paths = contract["paths"]
    schemas = contract["components"]["schemas"]

    for path in {
        "/api/v1/countries",
        "/api/v1/countries/{country_slug}",
        "/api/v1/countries/{country_slug}/card",
        "/api/v1/legal-signals",
        "/api/v1/sources",
        "/api/v1/evidence-items",
        "/api/v1/scenarios",
        "/api/v1/user-stories",
        "/api/v1/decision/run",
        "/api/v1/admin/data-quality/report",
    }:
        assert path in paths

    for schema in {
        "CountryListResponse",
        "CountryResponse",
        "CountryReadModelResponse",
        "DecisionRunRequest",
        "DecisionRunResponse",
        "LegalSignalDetailListResponse",
        "SourceListResponse",
        "EvidenceItemListResponse",
        "ScenarioListResponse",
        "UserStoryListResponse",
        "DataQualityReport",
        "LocaleResolution",
        "ErrorResponse",
    }:
        assert schema in schemas

    report_path = paths["/api/v1/admin/data-quality/report"]["get"]
    assert report_path["security"] == [{"AdminTokenAuth": []}]

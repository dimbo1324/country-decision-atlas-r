from pathlib import Path
from typing import Any, cast
import yaml


def load_contract() -> dict[str, Any]:
    contract_path = Path("contracts/openapi.yaml")
    return cast(
        dict[str, Any], yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    )


def test_openapi_contract_has_required_paths() -> None:
    contract = load_contract()
    expected_paths = {
        "/health",
        "/api/v1/countries",
        "/api/v1/countries/{country_slug}",
        "/api/v1/countries/{country_slug}/card",
        "/api/v1/countries/{country_slug}/sources",
        "/api/v1/countries/{country_id}/profile",
        "/api/v1/countries/{country_id}/legal-signals",
        "/api/v1/countries/{country_id}/scores",
        "/api/v1/scenarios",
        "/api/v1/scenarios/{slug}",
        "/api/v1/scenarios/{slug}/countries",
        "/api/v1/scenario-runs",
        "/api/v1/sources",
        "/api/v1/sources/{source_id}",
        "/api/v1/sources/{source_id}/evidence",
        "/api/v1/evidence-items",
        "/api/v1/translations",
        "/api/v1/legal-signals",
        "/api/v1/legal-signals/{signal_id}",
        "/api/v1/legal-signals/{signal_id}/evidence",
        "/api/v1/user-stories",
        "/api/v1/user-stories/{story_id}",
        "/api/v1/decision/compare",
        "/api/v1/decision/run",
        "/api/v1/admin/legal-signals",
        "/api/v1/admin/data-quality/report",
        "/api/v1/admin/translations/jobs",
    }
    assert expected_paths.issubset(set(contract["paths"]))


def test_openapi_contract_uses_locale_resolution_schema() -> None:
    contract = load_contract()
    schemas = contract["components"]["schemas"]
    assert "LocaleResolution" in schemas
    assert schemas["LocaleCode"]["enum"] == ["en", "ru"]
    assert schemas["TranslationStatus"]["enum"] == [
        "source",
        "translated",
        "fallback",
        "missing",
    ]


def test_openapi_contract_has_decision_engine_schemas() -> None:
    contract = load_contract()
    schemas = contract["components"]["schemas"]

    for schema_name in [
        "CountryReadModelResponse",
        "CountryReadModelScore",
        "CountryReadModelScoreBreakdown",
        "CountryScoreBreakdown",
        "DecisionCompareInput",
        "DecisionCompareResult",
        "DecisionRunRequest",
        "DecisionRunResponse",
        "DecisionCountryResult",
        "DecisionRiskWarning",
        "DecisionBreakdownItem",
        "LegalSignalDetailListResponse",
        "SourceListResponse",
        "EvidenceItemListResponse",
        "ScenarioListResponse",
        "UserStoryListResponse",
        "DataQualityReport",
        "DataQualityIssue",
        "ErrorResponse",
        "Pagination",
        "SortMeta",
        "UserStory",
        "UserStoryCreate",
    ]:
        assert schema_name in schemas

    run_path = contract["paths"]["/api/v1/decision/run"]["post"]
    assert run_path["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/DecisionRunRequest"
    }
    assert run_path["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/DecisionRunResponse"
    }


def test_openapi_contract_has_admin_token_security() -> None:
    contract = load_contract()
    security_schemes = contract["components"]["securitySchemes"]
    report_path = contract["paths"]["/api/v1/admin/data-quality/report"]["get"]

    assert security_schemes["AdminTokenAuth"] == {
        "type": "apiKey",
        "in": "header",
        "name": "X-Admin-Token",
    }
    assert report_path["security"] == [{"AdminTokenAuth": []}]

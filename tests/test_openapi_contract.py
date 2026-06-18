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
        "/api/v1/countries/{country_id}",
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
        "CountryCard",
        "CountryScoreBreakdown",
        "DecisionCompareInput",
        "DecisionCompareResult",
        "DecisionRunInput",
        "DecisionRunResult",
        "UserStory",
        "UserStoryCreate",
    ]:
        assert schema_name in schemas

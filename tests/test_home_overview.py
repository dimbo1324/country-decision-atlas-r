from app.core.database import get_connection
from app.main import app
from app.schemas.cii_matrix import (
    CompareMatrixResponse,
    MatrixCell,
    MatrixCountry,
    MatrixScenario,
)
from app.schemas.common import TranslationStatus, locale_resolution
from app.schemas.home_overview import HomeMatrixPreview, HomeOverviewResponse
from app.services.home_overview import build_home_overview
from datetime import date
from fastapi.testclient import TestClient
from tests.test_openapi_contract import load_contract
from typing import Any
from unittest.mock import MagicMock, patch


CONNECTION = MagicMock()
COUNTRIES = [
    MatrixCountry(slug="russia", name="Russia", iso2="RU"),
    MatrixCountry(slug="uruguay", name="Uruguay", iso2="UY"),
]
SCENARIOS = [
    MatrixScenario(slug="relocation_residence", name="Relocation", display_order=1),
    MatrixScenario(
        slug="permanent_residence_citizenship",
        name="Permanent residence",
        display_order=2,
    ),
    MatrixScenario(slug="low_budget_living", name="Low budget", display_order=3),
    MatrixScenario(slug="business_self_employment", name="Business", display_order=4),
    MatrixScenario(slug="safety_political_risk", name="Safety", display_order=5),
]
CELLS = [
    MatrixCell(
        country_slug=country.slug,
        scenario_slug=scenario.slug,
        cii_score=(25.0 + index if country.slug == "russia" else 65.0 + index),
        cii_confidence="high",
        score_label="weak" if country.slug == "russia" else "moderate",
    )
    for index, scenario in enumerate(SCENARIOS)
    for country in COUNTRIES
]


def matrix(
    locale: str = "en", cells: list[MatrixCell] | None = None
) -> CompareMatrixResponse:
    return CompareMatrixResponse(
        locale=locale_resolution(locale, locale, TranslationStatus.source),
        countries=COUNTRIES,
        scenarios=SCENARIOS,
        cells=CELLS if cells is None else cells,
        formula_version="cii-v1.0",
        aggregation_method="geometric",
        weights_version="cii-scenario-weights-v1.0",
    )


def event_row() -> dict[str, Any]:
    return {
        "legal_signal_id": "11111111-1111-4111-8111-111111111111",
        "country_slug": "russia",
        "country_name": "Russia",
        "event_date": date(2026, 6, 19),
        "title": "Legal change",
        "summary": "Confirmed legal change",
        "title_en": "Legal change",
        "title_ru": "Правовое изменение",
        "summary_en": "Confirmed legal change",
        "summary_ru": "Подтверждённое правовое изменение",
        "impact_direction": "negative",
        "impact_level": "high",
        "source_ref_id": "22222222-2222-4222-8222-222222222222",
        "source_title": "Official source",
        "source_url": "https://government.example/source",
        "translation_status": "source",
        "resolved_locale": "en",
    }


def build(
    locale: str = "en",
    events: list[dict[str, Any]] | None = None,
    cells: list[MatrixCell] | None = None,
) -> HomeOverviewResponse:
    rows = [event_row()] if events is None else events
    with (
        patch(
            "app.services.home_overview.build_matrix_response",
            return_value=matrix(locale, cells),
        ),
        patch(
            "app.services.home_overview.repository.list_latest_legal_events",
            return_value=rows,
        ),
        patch(
            "app.services.home_overview.overlay_localized_fields",
            side_effect=lambda _connection, items, *_args: items,
        ),
    ):
        return build_home_overview(CONNECTION, locale)


def test_home_overview_contains_two_mvp_countries() -> None:
    result = build()

    assert {country.slug for country in result.countries_summary} == {
        "russia",
        "uruguay",
    }


def test_home_overview_contains_five_scenario_winners() -> None:
    result = build()

    assert len(result.scenario_winners) == 5
    assert all(
        winner.winner_country_slug == "uruguay" for winner in result.scenario_winners
    )


def test_home_overview_matrix_has_expected_shape() -> None:
    result = build()

    assert len(result.matrix_preview.countries) == 2
    assert len(result.matrix_preview.scenarios) == 5
    assert len(result.matrix_preview.cells) == 10


def test_country_summary_computes_best_weakest_and_average() -> None:
    result = build()
    russia = next(
        country for country in result.countries_summary if country.slug == "russia"
    )

    assert russia.best_score == 29.0
    assert russia.weakest_score == 25.0
    assert russia.average_score == 27.0
    assert russia.confidence == "high"


def test_home_overview_contains_latest_legal_events_and_insights() -> None:
    result = build()

    assert result.latest_legal_events
    assert result.latest_legal_events[0].source is not None
    assert result.key_insights
    assert result.generated_at is not None


def test_home_overview_handles_missing_legal_events() -> None:
    result = build(events=[])

    assert result.latest_legal_events == []
    assert any(
        insight.kind == "legal_events_missing" for insight in result.key_insights
    )


def test_home_overview_handles_partial_matrix_cells() -> None:
    result = build(cells=CELLS[:1])

    assert len(result.countries_summary) == 2
    assert len(result.scenario_winners) == 5
    assert result.countries_summary[1].average_score is None


def test_home_overview_supports_en_and_ru_locales() -> None:
    assert build(locale="en").locale.requested_locale == "en"
    assert build(locale="ru").locale.requested_locale == "ru"


def test_home_overview_endpoint_returns_200(monkeypatch: Any) -> None:
    response_model = HomeOverviewResponse(
        locale=locale_resolution("en", "en", TranslationStatus.source),
        matrix_preview=HomeMatrixPreview(),
    )
    monkeypatch.setattr(
        "app.api.v1.home.build_home_overview", lambda *_: response_model
    )
    app.dependency_overrides[get_connection] = lambda: CONNECTION
    try:
        response = TestClient(app).get("/api/v1/home/overview?locale=en")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["matrix_preview"]["cells"] == []


def test_openapi_contains_home_overview_endpoint_and_schemas() -> None:
    contract = load_contract()

    assert "/api/v1/home/overview" in contract["paths"]
    for schema in [
        "HomeOverviewResponse",
        "CountryOverviewCard",
        "ScenarioWinner",
        "HomeMatrixPreview",
        "HomeMatrixCountry",
        "HomeMatrixScenario",
        "HomeMatrixCell",
        "LatestLegalEvent",
        "HomeKeyInsight",
        "HomeOverviewLinks",
    ]:
        assert schema in contract["components"]["schemas"]

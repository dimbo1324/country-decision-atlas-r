from app.repositories.cii import (
    get_cii_matrix_cells,
    list_matrix_countries,
    list_matrix_scenarios,
)
from app.schemas.cii_matrix import (
    CompareMatrixResponse,
    MatrixCell,
    MatrixCountry,
    MatrixScenario,
)
from app.schemas.common import TranslationStatus, locale_resolution
from psycopg import Connection
from typing import Any


MVP_COUNTRIES = ["russia", "uruguay"]

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]

_MVP_SCENARIO_ORDER: dict[str, int] = {
    slug: i + 1 for i, slug in enumerate(MVP_SCENARIOS)
}

WEIGHTS_VERSION = "cii-scenario-weights-v1.0"


def _score_label(score: float | None) -> str | None:
    if score is None:
        return "missing"
    if score < 30:
        return "weak"
    if score < 50:
        return "limited"
    if score < 70:
        return "moderate"
    if score < 85:
        return "strong"
    return "excellent"


def _confidence_label(confidence: str | None) -> str | None:
    if confidence is None:
        return "missing"
    return confidence


def build_matrix_response(
    connection: Connection[Any],
    country_slugs_param: list[str] | None,
    scenario_slugs_param: list[str] | None,
    locale: str,
) -> CompareMatrixResponse:
    country_slugs = country_slugs_param if country_slugs_param else MVP_COUNTRIES
    scenario_slugs = scenario_slugs_param if scenario_slugs_param else MVP_SCENARIOS

    country_rows = list_matrix_countries(connection, country_slugs, locale)
    found_country_slugs = {r["slug"] for r in country_rows}

    scenario_rows = list_matrix_scenarios(connection, scenario_slugs, locale)
    found_scenario_slugs = {r["slug"] for r in scenario_rows}

    quality_warnings: list[str] = []
    for slug in country_slugs:
        if slug not in found_country_slugs:
            quality_warnings.append(f"country '{slug}' not found")
    for slug in scenario_slugs:
        if slug not in found_scenario_slugs:
            quality_warnings.append(f"scenario '{slug}' not found or inactive")

    countries: list[MatrixCountry] = []
    for slug in country_slugs:
        row = next((r for r in country_rows if r["slug"] == slug), None)
        if row:
            countries.append(
                MatrixCountry(slug=row["slug"], name=row["name"], iso2=row.get("iso2"))
            )

    scenarios: list[MatrixScenario] = []
    for slug in scenario_slugs:
        row = next((r for r in scenario_rows if r["slug"] == slug), None)
        if row:
            order = _MVP_SCENARIO_ORDER.get(slug, 99)
            scenarios.append(
                MatrixScenario(slug=row["slug"], name=row["name"], display_order=order)
            )

    cell_rows = get_cii_matrix_cells(connection, country_slugs, scenario_slugs)
    cells_by_key: dict[tuple[str, str], dict[str, Any]] = {
        (r["country_slug"], r["scenario_slug"]): r for r in cell_rows
    }

    formula_version: str | None = None
    aggregation_method: str | None = None
    for r in cell_rows:
        formula_version = formula_version or r.get("formula_version")
        aggregation_method = aggregation_method or r.get("aggregation_method")

    weights_version: str | None = WEIGHTS_VERSION

    cells: list[MatrixCell] = []
    for country in countries:
        for scenario in scenarios:
            key = (country.slug, scenario.slug)
            row = cells_by_key.get(key)
            cell_warnings: list[str] = []
            if row is None:
                cell_warnings.append(
                    f"no CII score for '{country.slug}' / '{scenario.slug}'"
                )
                quality_warnings.append(
                    f"missing CII score for '{country.slug}' in scenario '{scenario.slug}'"
                )
                cells.append(
                    MatrixCell(
                        country_slug=country.slug,
                        scenario_slug=scenario.slug,
                        cii_score=None,
                        cii_confidence=None,
                        country_drift=None,
                        score_label="missing",
                        confidence_label="missing",
                        formula_version=formula_version,
                        aggregation_method=aggregation_method,
                        weights_version=weights_version,
                        quality_warnings=cell_warnings,
                    )
                )
            else:
                score = row.get("cii_score")
                confidence = row.get("cii_confidence")
                cells.append(
                    MatrixCell(
                        country_slug=country.slug,
                        scenario_slug=scenario.slug,
                        cii_score=score,
                        cii_confidence=confidence,
                        country_drift=row.get("country_drift"),
                        score_label=_score_label(score),
                        confidence_label=_confidence_label(confidence),
                        formula_version=row.get("formula_version") or formula_version,
                        aggregation_method=row.get("aggregation_method")
                        or aggregation_method,
                        weights_version=weights_version,
                        quality_warnings=cell_warnings,
                    )
                )

    resolved_locale = locale_resolution(locale, locale, TranslationStatus.source)

    return CompareMatrixResponse(
        locale=resolved_locale,
        countries=countries,
        scenarios=scenarios,
        cells=cells,
        formula_version=formula_version,
        aggregation_method=aggregation_method,
        weights_version=weights_version,
        quality_warnings=quality_warnings,
    )

import pytest
from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.cii"
_SVC = "app.services.cii_matrix"
_ROUTE = "app.api.v1.countries"

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]

_COUNTRY_ROWS = [
    {"slug": "russia", "name": "Россия", "iso2": "RU"},
    {"slug": "uruguay", "name": "Уругвай", "iso2": "UY"},
]

_SCENARIO_ROWS = [
    {"slug": s, "name": s.replace("_", " ").title()} for s in MVP_SCENARIOS
]

_CELL_ROWS = [
    {
        "country_slug": "russia",
        "scenario_slug": "relocation_residence",
        "cii_score": 24.88,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "russia",
        "scenario_slug": "permanent_residence_citizenship",
        "cii_score": 23.08,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "russia",
        "scenario_slug": "low_budget_living",
        "cii_score": 27.56,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "russia",
        "scenario_slug": "business_self_employment",
        "cii_score": 29.38,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "russia",
        "scenario_slug": "safety_political_risk",
        "cii_score": 22.86,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "scenario_slug": "relocation_residence",
        "cii_score": 69.11,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "scenario_slug": "permanent_residence_citizenship",
        "cii_score": 70.80,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "scenario_slug": "low_budget_living",
        "cii_score": 69.04,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "scenario_slug": "business_self_employment",
        "cii_score": 69.17,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "scenario_slug": "safety_political_risk",
        "cii_score": 70.12,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
]


def _make_connection() -> MagicMock:
    return MagicMock()


def _run_matrix(
    country_slugs: list[str] | None = None,
    scenario_slugs: list[str] | None = None,
    locale: str = "ru",
    country_rows: list[dict[str, Any]] | None = None,
    scenario_rows: list[dict[str, Any]] | None = None,
    cell_rows: list[dict[str, Any]] | None = None,
) -> Any:
    from app.services.cii_matrix import build_matrix_response

    with (
        patch(
            f"{_SVC}.list_matrix_countries", return_value=country_rows or _COUNTRY_ROWS
        ),
        patch(
            f"{_SVC}.list_matrix_scenarios",
            return_value=scenario_rows or _SCENARIO_ROWS,
        ),
        patch(
            f"{_SVC}.get_cii_matrix_cells",
            return_value=cell_rows if cell_rows is not None else _CELL_ROWS,
        ),
    ):
        return build_matrix_response(
            _make_connection(), country_slugs, scenario_slugs, locale
        )


class TestMatrixDefaults:
    def test_default_returns_two_countries(self) -> None:
        result = _run_matrix()
        slugs = [c.slug for c in result.countries]
        assert "russia" in slugs
        assert "uruguay" in slugs

    def test_default_returns_five_scenarios(self) -> None:
        result = _run_matrix()
        assert len(result.scenarios) == 5

    def test_default_returns_ten_cells(self) -> None:
        result = _run_matrix()
        assert len(result.cells) == 10

    def test_all_scenarios_present_by_default(self) -> None:
        result = _run_matrix()
        slugs = {s.slug for s in result.scenarios}
        assert slugs == set(MVP_SCENARIOS)


class TestMatrixCells:
    def test_cells_have_cii_score(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.cii_score is not None

    def test_cells_have_cii_confidence(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.cii_confidence is not None

    def test_cells_have_score_label(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.score_label is not None

    def test_cells_have_confidence_label(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.confidence_label is not None

    def test_cells_have_formula_version(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.formula_version is not None

    def test_cells_have_aggregation_method(self) -> None:
        result = _run_matrix()
        for cell in result.cells:
            assert cell.aggregation_method is not None

    def test_response_has_formula_version(self) -> None:
        result = _run_matrix()
        assert result.formula_version == "cii-v1.0"

    def test_response_has_aggregation_method(self) -> None:
        result = _run_matrix()
        assert result.aggregation_method == "geometric"

    def test_response_has_weights_version(self) -> None:
        result = _run_matrix()
        assert result.weights_version is not None

    def test_response_has_quality_warnings_list(self) -> None:
        result = _run_matrix()
        assert isinstance(result.quality_warnings, list)

    def test_cell_lookup_by_country_and_scenario(self) -> None:
        result = _run_matrix()
        cell = next(
            (
                c
                for c in result.cells
                if c.country_slug == "russia"
                and c.scenario_slug == "relocation_residence"
            ),
            None,
        )
        assert cell is not None
        assert cell.cii_score == pytest.approx(24.88)


class TestScoreLabels:
    def test_score_below_30_is_weak(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(22.5) == "weak"
        assert _score_label(0.0) == "weak"
        assert _score_label(29.9) == "weak"

    def test_score_30_to_50_is_limited(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(30.0) == "limited"
        assert _score_label(49.9) == "limited"

    def test_score_50_to_70_is_moderate(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(50.0) == "moderate"
        assert _score_label(69.9) == "moderate"

    def test_score_70_to_85_is_strong(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(70.0) == "strong"
        assert _score_label(84.9) == "strong"

    def test_score_85_plus_is_excellent(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(85.0) == "excellent"
        assert _score_label(100.0) == "excellent"

    def test_none_score_is_missing(self) -> None:
        from app.services.cii_matrix import _score_label

        assert _score_label(None) == "missing"

    def test_russia_scores_are_weak(self) -> None:
        result = _run_matrix()
        russia_cells = [c for c in result.cells if c.country_slug == "russia"]
        for cell in russia_cells:
            assert cell.score_label == "weak"

    def test_uruguay_scores_are_moderate(self) -> None:
        result = _run_matrix()
        uruguay_cells = [c for c in result.cells if c.country_slug == "uruguay"]
        for cell in uruguay_cells:
            assert cell.score_label in ("moderate", "strong")


class TestMissingCells:
    def test_missing_score_does_not_crash(self) -> None:
        result = _run_matrix(cell_rows=[])
        assert len(result.cells) == 10

    def test_missing_cells_have_none_score(self) -> None:
        result = _run_matrix(cell_rows=[])
        for cell in result.cells:
            assert cell.cii_score is None

    def test_missing_cells_have_missing_score_label(self) -> None:
        result = _run_matrix(cell_rows=[])
        for cell in result.cells:
            assert cell.score_label == "missing"

    def test_missing_cells_add_quality_warning(self) -> None:
        result = _run_matrix(cell_rows=[])
        assert len(result.quality_warnings) > 0

    def test_partial_missing_still_returns_all_cells(self) -> None:
        partial_cells = _CELL_ROWS[:5]
        result = _run_matrix(cell_rows=partial_cells)
        assert len(result.cells) == 10


class TestOrdering:
    def test_scenario_display_order_is_stable(self) -> None:
        result = _run_matrix()
        orders = [s.display_order for s in result.scenarios]
        assert orders == sorted(orders)

    def test_scenario_order_matches_mvp_order(self) -> None:
        result = _run_matrix()
        slugs = [s.slug for s in result.scenarios]
        assert slugs.index("relocation_residence") < slugs.index(
            "business_self_employment"
        )

    def test_countries_in_response(self) -> None:
        result = _run_matrix()
        slugs = [c.slug for c in result.countries]
        assert "russia" in slugs
        assert "uruguay" in slugs


class TestLocale:
    def test_locale_resolution_in_response(self) -> None:
        result = _run_matrix(locale="ru")
        assert result.locale.requested_locale == "ru"
        assert result.locale.resolved_locale == "ru"


class TestFiltering:
    def test_single_scenario_filter(self) -> None:
        single_scenario_rows = [{"slug": "relocation_residence", "name": "Релокация"}]
        single_cells = [
            c for c in _CELL_ROWS if c["scenario_slug"] == "relocation_residence"
        ]
        result = _run_matrix(
            scenario_slugs=["relocation_residence"],
            scenario_rows=single_scenario_rows,
            cell_rows=single_cells,
        )
        assert len(result.scenarios) == 1
        assert len(result.cells) == 2

    def test_single_country_filter(self) -> None:
        single_country_rows = [{"slug": "russia", "name": "Россия", "iso2": "RU"}]
        single_cells = [c for c in _CELL_ROWS if c["country_slug"] == "russia"]
        result = _run_matrix(
            country_slugs=["russia"],
            country_rows=single_country_rows,
            cell_rows=single_cells,
        )
        assert len(result.countries) == 1
        assert len(result.cells) == 5

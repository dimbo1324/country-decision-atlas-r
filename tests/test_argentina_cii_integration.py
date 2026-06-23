import pytest
from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.country_onboarding"
_MATRIX_SVC = "app.services.cii_matrix"
_CMP_SVC = "app.services.cii_comparison"

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def _make_connection() -> MagicMock:
    return MagicMock()


def _argentina_cii_ready_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "arg-id",
            "slug": "argentina",
            "name": "Argentina",
            "iso2": "AR",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 6,
        "count_published_evidence": 6,
        "count_published_legal_signals": 0,
        "count_timeline_events": 0,
        "count_timeline_events_with_traceability": 0,
        "check_localization_metadata": True,
    }


def _evaluate_argentina_cii_ready(**overrides: Any) -> Any:
    from app.services.country_onboarding import evaluate_country_onboarding

    defaults = _argentina_cii_ready_defaults()
    defaults.update(overrides)
    patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
    with patch.multiple(_REPO, **patchers):
        return evaluate_country_onboarding(_make_connection(), "argentina")


def _russia_pass_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "ru-id",
            "slug": "russia",
            "name": "Russia",
            "iso2": "RU",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 20,
        "count_published_evidence": 30,
        "count_published_legal_signals": 10,
        "count_timeline_events": 12,
        "count_timeline_events_with_traceability": 12,
        "check_localization_metadata": True,
    }


def _uruguay_pass_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "uy-id",
            "slug": "uruguay",
            "name": "Uruguay",
            "iso2": "UY",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 20,
        "count_published_evidence": 15,
        "count_published_legal_signals": 10,
        "count_timeline_events": 12,
        "count_timeline_events_with_traceability": 12,
        "check_localization_metadata": True,
    }


_METRIC_DEFS = [
    {
        "id": "a1",
        "slug": "rule_of_law",
        "name_en": "Rule of Law",
        "name_ru": "Верховенство права",
        "polarity": "positive",
        "display_order": 1,
    },
    {
        "id": "a2",
        "slug": "economic_freedom",
        "name_en": "Economic Freedom",
        "name_ru": "Экономическая свобода",
        "polarity": "positive",
        "display_order": 2,
    },
    {
        "id": "a3",
        "slug": "political_stability",
        "name_en": "Political Stability",
        "name_ru": "Политическая стабильность",
        "polarity": "positive",
        "display_order": 3,
    },
    {
        "id": "a4",
        "slug": "safety",
        "name_en": "Physical Safety",
        "name_ru": "Физическая безопасность",
        "polarity": "positive",
        "display_order": 4,
    },
    {
        "id": "a5",
        "slug": "corruption",
        "name_en": "Anti-Corruption",
        "name_ru": "Антикоррупционность",
        "polarity": "positive",
        "display_order": 5,
    },
    {
        "id": "a6",
        "slug": "digital_access",
        "name_en": "Digital Access",
        "name_ru": "Цифровой доступ",
        "polarity": "positive",
        "display_order": 6,
    },
]

_SCENARIO_WEIGHTS = [
    {"metric_slug": "rule_of_law", "weight": 0.2000},
    {"metric_slug": "economic_freedom", "weight": 0.1000},
    {"metric_slug": "political_stability", "weight": 0.2000},
    {"metric_slug": "safety", "weight": 0.2500},
    {"metric_slug": "corruption", "weight": 0.1500},
    {"metric_slug": "digital_access", "weight": 0.1000},
]

_MATRIX_COUNTRY_ROWS = [
    {"slug": "russia", "name": "Россия", "iso2": "RU"},
    {"slug": "uruguay", "name": "Уругвай", "iso2": "UY"},
    {"slug": "argentina", "name": "Аргентина", "iso2": "AR"},
]

_MATRIX_SCENARIO_ROWS = [
    {"slug": s, "name": s.replace("_", " ").title()} for s in MVP_SCENARIOS
]

_MATRIX_CELL_ROWS = [
    {
        "country_slug": c,
        "scenario_slug": s,
        "cii_score": score,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    }
    for c, score in [("russia", 25.0), ("uruguay", 68.0), ("argentina", 43.0)]
    for s in MVP_SCENARIOS
]


class TestArgentinaCiiOnboarding:
    def test_argentina_cii_section_ready_when_metrics_complete(self) -> None:
        result = _evaluate_argentina_cii_ready()
        assert result.sections["cii_metrics"].status == "ready"
        assert result.sections["cii_metrics"].actual == 6

    def test_argentina_scenario_scores_ready_when_complete(self) -> None:
        result = _evaluate_argentina_cii_ready()
        assert result.sections["scenario_scores"].status == "ready"
        assert result.sections["scenario_scores"].actual == 5

    def test_argentina_still_not_mvp_ready_without_legal(self) -> None:
        result = _evaluate_argentina_cii_ready()
        assert result.mvp_ready is False

    def test_argentina_legal_signals_still_missing(self) -> None:
        result = _evaluate_argentina_cii_ready()
        assert result.sections["legal_signals"].status == "missing"
        assert result.sections["legal_signals"].actual == 0

    def test_argentina_timeline_still_missing(self) -> None:
        result = _evaluate_argentina_cii_ready()
        assert result.sections["timeline"].status == "missing"
        assert result.sections["timeline"].actual == 0


_BASE_ROWS = {
    "russia": _russia_pass_defaults()["get_country_base"],
    "uruguay": _uruguay_pass_defaults()["get_country_base"],
    "argentina": _argentina_cii_ready_defaults()["get_country_base"],
}

_SOURCE_COUNTS = {"russia": 20, "uruguay": 20, "argentina": 10}
_EVIDENCE_COUNTS = {"russia": 30, "uruguay": 15, "argentina": 15}
_LEGAL_COUNTS = {"russia": 10, "uruguay": 10, "argentina": 6}
_TIMELINE_COUNTS = {"russia": 12, "uruguay": 12, "argentina": 6}


def _evaluate_all_mvp_with_argentina_cii() -> Any:
    from app.services.country_onboarding import evaluate_all_mvp_countries

    with (
        patch(
            f"{_REPO}.get_country_base",
            side_effect=lambda _, slug: _BASE_ROWS.get(slug),
        ),
        patch(f"{_REPO}.count_published_country_cards", return_value=2),
        patch(f"{_REPO}.count_active_cii_metrics", return_value=6),
        patch(
            f"{_REPO}.count_country_cii_metric_values", side_effect=lambda _, _slug: 6
        ),
        patch(
            f"{_REPO}.count_cii_scenario_scores", side_effect=lambda _, _slug, _sc: 5
        ),
        patch(
            f"{_REPO}.count_published_sources",
            side_effect=lambda _, slug: _SOURCE_COUNTS.get(slug, 6),
        ),
        patch(
            f"{_REPO}.count_published_evidence",
            side_effect=lambda _, slug: _EVIDENCE_COUNTS.get(slug, 6),
        ),
        patch(
            f"{_REPO}.count_published_legal_signals",
            side_effect=lambda _, slug: _LEGAL_COUNTS.get(slug, 0),
        ),
        patch(
            f"{_REPO}.count_timeline_events",
            side_effect=lambda _, slug: _TIMELINE_COUNTS.get(slug, 0),
        ),
        patch(
            f"{_REPO}.count_timeline_events_with_traceability",
            side_effect=lambda _, slug: _TIMELINE_COUNTS.get(slug, 0),
        ),
        patch(f"{_REPO}.check_localization_metadata", return_value=True),
    ):
        return evaluate_all_mvp_countries(_make_connection())


class TestAllMvpReadyWithArgentinaCiiReady:
    def test_all_mvp_ready_true_with_argentina_cii_ready(self) -> None:
        result = _evaluate_all_mvp_with_argentina_cii()
        assert result.all_mvp_ready is True

    def test_mvp_countries_include_argentina(self) -> None:
        result = _evaluate_all_mvp_with_argentina_cii()
        mvp_slugs = [r.country_slug for r in result.countries]
        assert "argentina" in mvp_slugs

    def test_onboarding_countries_is_empty(self) -> None:
        result = _evaluate_all_mvp_with_argentina_cii()
        assert len(result.onboarding_countries) == 0

    def test_russia_remains_mvp_ready(self) -> None:
        result = _evaluate_all_mvp_with_argentina_cii()
        russia = next(r for r in result.countries if r.country_slug == "russia")
        assert russia.mvp_ready is True

    def test_uruguay_remains_mvp_ready(self) -> None:
        result = _evaluate_all_mvp_with_argentina_cii()
        uruguay = next(r for r in result.countries if r.country_slug == "uruguay")
        assert uruguay.mvp_ready is True


class TestArgentinaCiiSlugInMatrix:
    def test_argentina_is_in_mvp_countries_list(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert "argentina" in MVP_COUNTRIES

    def test_matrix_has_three_countries_by_default(self) -> None:
        from app.services.cii_matrix import build_matrix_response

        with (
            patch(
                f"{_MATRIX_SVC}.list_matrix_countries",
                return_value=_MATRIX_COUNTRY_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.list_matrix_scenarios",
                return_value=_MATRIX_SCENARIO_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.get_cii_matrix_cells", return_value=_MATRIX_CELL_ROWS
            ),
        ):
            result = build_matrix_response(_make_connection(), None, None, "ru")

        slugs = [c.slug for c in result.countries]
        assert len(slugs) == 3
        assert "argentina" in slugs

    def test_matrix_has_fifteen_cells_by_default(self) -> None:
        from app.services.cii_matrix import build_matrix_response

        with (
            patch(
                f"{_MATRIX_SVC}.list_matrix_countries",
                return_value=_MATRIX_COUNTRY_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.list_matrix_scenarios",
                return_value=_MATRIX_SCENARIO_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.get_cii_matrix_cells", return_value=_MATRIX_CELL_ROWS
            ),
        ):
            result = build_matrix_response(_make_connection(), None, None, "ru")

        assert len(result.cells) == 15

    def test_argentina_cells_have_scores(self) -> None:
        from app.services.cii_matrix import build_matrix_response

        with (
            patch(
                f"{_MATRIX_SVC}.list_matrix_countries",
                return_value=_MATRIX_COUNTRY_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.list_matrix_scenarios",
                return_value=_MATRIX_SCENARIO_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.get_cii_matrix_cells", return_value=_MATRIX_CELL_ROWS
            ),
        ):
            result = build_matrix_response(_make_connection(), None, None, "ru")

        argentina_cells = [c for c in result.cells if c.country_slug == "argentina"]
        assert len(argentina_cells) == 5
        for cell in argentina_cells:
            assert cell.cii_score == pytest.approx(43.0)

    def test_argentina_matrix_scores_are_limited_range(self) -> None:
        from app.services.cii_matrix import build_matrix_response

        with (
            patch(
                f"{_MATRIX_SVC}.list_matrix_countries",
                return_value=_MATRIX_COUNTRY_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.list_matrix_scenarios",
                return_value=_MATRIX_SCENARIO_ROWS,
            ),
            patch(
                f"{_MATRIX_SVC}.get_cii_matrix_cells", return_value=_MATRIX_CELL_ROWS
            ),
        ):
            result = build_matrix_response(_make_connection(), None, None, "ru")

        argentina_cells = [c for c in result.cells if c.country_slug == "argentina"]
        for cell in argentina_cells:
            assert cell.score_label == "limited"


_METRIC_VALUES_BY_SLUG: dict[str, dict[str, float]] = {
    "argentina": {
        "rule_of_law": 38.0,
        "economic_freedom": 44.8,
        "political_stability": 30.0,
        "safety": 55.0,
        "corruption": 37.0,
        "digital_access": 68.0,
    },
    "uruguay": {
        "rule_of_law": 72.0,
        "economic_freedom": 68.1,
        "political_stability": 76.0,
        "safety": 63.0,
        "corruption": 73.0,
        "digital_access": 62.0,
    },
    "russia": {
        "rule_of_law": 20.0,
        "economic_freedom": 54.2,
        "political_stability": 13.0,
        "safety": 38.0,
        "corruption": 26.0,
        "digital_access": 21.0,
    },
}

_CII_SCORES_BY_SLUG: dict[str, float] = {
    "argentina": 42.67,
    "uruguay": 69.11,
    "russia": 24.88,
}

_ISO2_BY_SLUG: dict[str, str] = {"argentina": "AR", "uruguay": "UY", "russia": "RU"}


class TestArgentinaCiiComparison:
    def _run_comparison(
        self,
        country_slugs: list[str],
        scenario_slug: str = "relocation_residence",
    ) -> Any:
        from app.services.cii_comparison import build_cii_comparison

        scenario_row = {
            "slug": scenario_slug,
            "title": scenario_slug.replace("_", " ").title(),
        }
        cii_rows = [
            {
                "country_slug": slug,
                "country_name": slug.title(),
                "iso2": _ISO2_BY_SLUG.get(slug, "XX"),
                "cii_score": _CII_SCORES_BY_SLUG.get(slug, 50.0),
                "cii_confidence": "high",
                "country_drift": None,
                "formula_version": "cii-v1.0",
                "aggregation_method": "geometric",
            }
            for slug in country_slugs
        ]
        metric_values: list[dict[str, Any]] = []
        for slug in country_slugs:
            slug_metrics = _METRIC_VALUES_BY_SLUG.get(slug) or {}
            for m in _METRIC_DEFS:
                metric_key = str(m["slug"])
                metric_values.append(
                    {
                        "country_slug": slug,
                        "metric_slug": metric_key,
                        "value": slug_metrics.get(metric_key) or 50.0,
                        "polarity": m["polarity"],
                    }
                )

        with (
            patch(
                f"{_CMP_SVC}.get_scenario_for_cii_comparison",
                return_value=scenario_row,
            ),
            patch(
                f"{_CMP_SVC}.get_scenario_metric_weights",
                return_value=_SCENARIO_WEIGHTS,
            ),
            patch(f"{_CMP_SVC}.get_cii_for_countries", return_value=cii_rows),
            patch(
                f"{_CMP_SVC}.get_active_cii_metric_definitions",
                return_value=_METRIC_DEFS,
            ),
            patch(
                f"{_CMP_SVC}.get_cii_metric_values_for_countries",
                return_value=metric_values,
            ),
        ):
            return build_cii_comparison(
                _make_connection(), country_slugs, scenario_slug, "ru"
            )

    def test_compare_argentina_uruguay_returns_both(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        slugs = [c.slug for c in result.countries]
        assert "argentina" in slugs
        assert "uruguay" in slugs

    def test_compare_argentina_russia_returns_both(self) -> None:
        result = self._run_comparison(["argentina", "russia"])
        slugs = [c.slug for c in result.countries]
        assert "argentina" in slugs
        assert "russia" in slugs

    def test_compare_argentina_uruguay_has_six_metrics(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        assert len(result.metrics) == 6

    def test_compare_argentina_uruguay_has_winner(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        any_delta = any(m.delta is not None for m in result.metrics)
        assert any_delta

    def test_compare_argentina_uruguay_has_scores(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        for country in result.countries:
            assert country.cii_score is not None

    def test_compare_argentina_russia_argentina_scores_higher(self) -> None:
        result = self._run_comparison(["argentina", "russia"])
        ar = next(c for c in result.countries if c.slug == "argentina")
        ru = next(c for c in result.countries if c.slug == "russia")
        assert ar.cii_score is not None
        assert ru.cii_score is not None
        assert ar.cii_score > ru.cii_score

    def test_compare_result_has_formula_version(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        assert result.formula_version == "cii-v1.0"

    def test_compare_result_has_aggregation_method(self) -> None:
        result = self._run_comparison(["argentina", "uruguay"])
        assert result.aggregation_method == "geometric"


class TestArgentinaCiiSlugsArchitecture:
    def test_argentina_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "argentina" in MVP_COUNTRY_SLUGS

    def test_onboarding_country_slugs_is_empty(self) -> None:
        from app.repositories.data_quality import ONBOARDING_COUNTRY_SLUGS

        assert len(ONBOARDING_COUNTRY_SLUGS) == 0

    def test_argentina_in_matrix_mvp_countries(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert "argentina" in MVP_COUNTRIES

    def test_russia_still_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "russia" in MVP_COUNTRY_SLUGS

    def test_uruguay_still_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "uruguay" in MVP_COUNTRY_SLUGS

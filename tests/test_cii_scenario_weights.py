import pytest
from typing import Any
from unittest.mock import MagicMock, patch


_SVC_CMP = "app.services.cii_comparison"

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]

MVP_METRIC_SLUGS = [
    "rule_of_law",
    "economic_freedom",
    "political_stability",
    "safety",
    "corruption",
    "digital_access",
]

_WEIGHTS_BY_SCENARIO: dict[str, dict[str, float]] = {
    "relocation_residence": {
        "safety": 0.25,
        "political_stability": 0.20,
        "rule_of_law": 0.20,
        "corruption": 0.15,
        "economic_freedom": 0.10,
        "digital_access": 0.10,
    },
    "permanent_residence_citizenship": {
        "rule_of_law": 0.25,
        "political_stability": 0.25,
        "corruption": 0.20,
        "safety": 0.15,
        "economic_freedom": 0.10,
        "digital_access": 0.05,
    },
    "low_budget_living": {
        "economic_freedom": 0.20,
        "safety": 0.20,
        "corruption": 0.20,
        "rule_of_law": 0.15,
        "political_stability": 0.15,
        "digital_access": 0.10,
    },
    "business_self_employment": {
        "economic_freedom": 0.35,
        "rule_of_law": 0.25,
        "corruption": 0.15,
        "digital_access": 0.15,
        "political_stability": 0.07,
        "safety": 0.03,
    },
    "safety_political_risk": {
        "safety": 0.30,
        "political_stability": 0.30,
        "rule_of_law": 0.20,
        "corruption": 0.15,
        "economic_freedom": 0.03,
        "digital_access": 0.02,
    },
}


def _weights_rows(scenario_slug: str) -> list[dict[str, Any]]:
    return [
        {"metric_slug": ms, "weight": w}
        for ms, w in _WEIGHTS_BY_SCENARIO[scenario_slug].items()
    ]


_CII_ROWS = [
    {
        "country_slug": "russia",
        "country_name": "Russia",
        "iso2": "RU",
        "cii_score": 22.5,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "country_name": "Uruguay",
        "iso2": "UY",
        "cii_score": 69.0,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
]

_METRIC_DEFS = [
    {
        "id": "aa",
        "slug": "rule_of_law",
        "name_en": "Rule of Law",
        "name_ru": "Верховенство права",
        "polarity": "positive",
        "display_order": 1,
    },
    {
        "id": "bb",
        "slug": "economic_freedom",
        "name_en": "Economic Freedom",
        "name_ru": "Экономическая свобода",
        "polarity": "positive",
        "display_order": 2,
    },
    {
        "id": "cc",
        "slug": "political_stability",
        "name_en": "Political Stability",
        "name_ru": "Политическая стабильность",
        "polarity": "positive",
        "display_order": 3,
    },
    {
        "id": "dd",
        "slug": "safety",
        "name_en": "Physical Safety",
        "name_ru": "Физическая безопасность",
        "polarity": "positive",
        "display_order": 4,
    },
    {
        "id": "ee",
        "slug": "corruption",
        "name_en": "Anti-Corruption",
        "name_ru": "Антикоррупционность",
        "polarity": "positive",
        "display_order": 5,
    },
    {
        "id": "ff",
        "slug": "digital_access",
        "name_en": "Digital Access",
        "name_ru": "Цифровой доступ",
        "polarity": "positive",
        "display_order": 6,
    },
]

_METRIC_VALUES = [
    {
        "country_slug": "russia",
        "metric_slug": "rule_of_law",
        "value": 20.0,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "economic_freedom",
        "value": 54.2,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "political_stability",
        "value": 13.0,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "safety",
        "value": 38.0,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "corruption",
        "value": 26.0,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "digital_access",
        "value": 21.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "rule_of_law",
        "value": 72.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "economic_freedom",
        "value": 68.1,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "political_stability",
        "value": 76.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "safety",
        "value": 63.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "corruption",
        "value": 73.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "digital_access",
        "value": 62.0,
        "polarity": "positive",
    },
]

_SCENARIO_ROW = {"slug": "relocation_residence", "title": "Relocation and residence"}


def _make_connection() -> MagicMock:
    return MagicMock()


def _run_comparison(
    scenario_slug: str = "relocation_residence",
    locale: str = "en",
    weights_rows: list[dict[str, Any]] | None = None,
) -> Any:
    from app.services.cii_comparison import build_cii_comparison

    resolved_weights = (
        weights_rows if weights_rows is not None else _weights_rows(scenario_slug)
    )
    scenario_row = {
        "slug": scenario_slug,
        "title": scenario_slug.replace("_", " ").title(),
    }

    with (
        patch(f"{_SVC_CMP}.get_scenario_metric_weights", return_value=resolved_weights),
        patch(f"{_SVC_CMP}.get_cii_for_countries", return_value=_CII_ROWS),
        patch(
            f"{_SVC_CMP}.get_active_cii_metric_definitions", return_value=_METRIC_DEFS
        ),
        patch(
            f"{_SVC_CMP}.get_cii_metric_values_for_countries",
            return_value=_METRIC_VALUES,
        ),
        patch(f"{_SVC_CMP}.get_scenario_for_cii_comparison", return_value=scenario_row),
    ):
        return build_cii_comparison(
            _make_connection(), ["russia", "uruguay"], scenario_slug, locale
        )


class TestScenarioWeightSums:
    @pytest.mark.parametrize("scenario_slug", MVP_SCENARIOS)
    def test_weight_sum_within_tolerance(self, scenario_slug: str) -> None:
        weights = _WEIGHTS_BY_SCENARIO[scenario_slug]
        total = sum(weights.values())
        assert abs(total - 1.0) <= 0.001, f"{scenario_slug} weight sum = {total}"

    @pytest.mark.parametrize("scenario_slug", MVP_SCENARIOS)
    def test_all_6_metrics_have_weights(self, scenario_slug: str) -> None:
        weights = _WEIGHTS_BY_SCENARIO[scenario_slug]
        for metric in MVP_METRIC_SLUGS:
            assert metric in weights, f"{scenario_slug} missing weight for {metric}"

    @pytest.mark.parametrize("scenario_slug", MVP_SCENARIOS)
    def test_no_negative_weights(self, scenario_slug: str) -> None:
        weights = _WEIGHTS_BY_SCENARIO[scenario_slug]
        for metric, w in weights.items():
            assert w >= 0, f"{scenario_slug}.{metric} has negative weight {w}"

    @pytest.mark.parametrize("scenario_slug", MVP_SCENARIOS)
    def test_no_weight_exceeds_one(self, scenario_slug: str) -> None:
        weights = _WEIGHTS_BY_SCENARIO[scenario_slug]
        for metric, w in weights.items():
            assert w <= 1.0, f"{scenario_slug}.{metric} has weight > 1: {w}"


class TestBusinessVsSafetyWeighting:
    def test_business_weights_economic_freedom_more_than_safety_political_risk(
        self,
    ) -> None:
        biz = _WEIGHTS_BY_SCENARIO["business_self_employment"]
        spr = _WEIGHTS_BY_SCENARIO["safety_political_risk"]
        assert biz["economic_freedom"] > spr["economic_freedom"]

    def test_safety_political_risk_weights_safety_more_than_business(self) -> None:
        biz = _WEIGHTS_BY_SCENARIO["business_self_employment"]
        spr = _WEIGHTS_BY_SCENARIO["safety_political_risk"]
        assert spr["safety"] > biz["safety"]

    def test_safety_political_risk_weights_political_stability_more_than_business(
        self,
    ) -> None:
        biz = _WEIGHTS_BY_SCENARIO["business_self_employment"]
        spr = _WEIGHTS_BY_SCENARIO["safety_political_risk"]
        assert spr["political_stability"] > biz["political_stability"]


class TestComparisonWithScenarioWeights:
    def test_metric_weight_included_in_response(self) -> None:
        result = _run_comparison("relocation_residence")
        by_slug = {m.metric_slug: m for m in result.metrics}
        safety_metric = by_slug["safety"]
        assert safety_metric.weight == pytest.approx(0.25)

    def test_all_metrics_have_weight_for_scenario(self) -> None:
        result = _run_comparison("business_self_employment")
        for m in result.metrics:
            assert m.weight is not None, f"{m.metric_slug} weight is None"

    def test_weights_version_in_response(self) -> None:
        result = _run_comparison("relocation_residence")
        assert result.weights_version == "v1.0"

    def test_scenario_slug_in_response(self) -> None:
        result = _run_comparison("relocation_residence")
        assert result.scenario.slug == "relocation_residence"

    def test_business_economic_freedom_weight_higher_than_safety_scenario(self) -> None:
        biz = _run_comparison("business_self_employment")
        spr = _run_comparison("safety_political_risk")
        biz_by_slug = {m.metric_slug: m for m in biz.metrics}
        spr_by_slug = {m.metric_slug: m for m in spr.metrics}
        assert (biz_by_slug["economic_freedom"].weight or 0) > (
            spr_by_slug["economic_freedom"].weight or 0
        )

    def test_safety_scenario_safety_weight_higher_than_business(self) -> None:
        biz = _run_comparison("business_self_employment")
        spr = _run_comparison("safety_political_risk")
        biz_by_slug = {m.metric_slug: m for m in biz.metrics}
        spr_by_slug = {m.metric_slug: m for m in spr.metrics}
        assert (spr_by_slug["safety"].weight or 0) > (biz_by_slug["safety"].weight or 0)

    def test_no_weights_scenario_sets_weights_version_to_none(self) -> None:
        result = _run_comparison("relocation_residence", weights_rows=[])
        assert result.weights_version is None

    def test_formula_version_preserved(self) -> None:
        result = _run_comparison("relocation_residence")
        assert result.formula_version == "cii-v1.0"

    def test_aggregation_method_preserved(self) -> None:
        result = _run_comparison("relocation_residence")
        assert result.aggregation_method == "geometric"

    def test_scenario_cii_scores_used_from_country_rows(self) -> None:
        result = _run_comparison("relocation_residence")
        by_slug = {c.slug: c for c in result.countries}
        assert by_slug["russia"].cii_score == pytest.approx(22.5)
        assert by_slug["uruguay"].cii_score == pytest.approx(69.0)

    def test_winner_and_delta_still_computed(self) -> None:
        result = _run_comparison("relocation_residence")
        by_metric = {m.metric_slug: m for m in result.metrics}
        rol = by_metric["rule_of_law"]
        assert rol.delta == pytest.approx(52.0, abs=0.01)
        assert rol.winner_country_slug == "uruguay"

    def test_polarity_still_applied(self) -> None:
        result = _run_comparison("safety_political_risk")
        by_metric = {m.metric_slug: m for m in result.metrics}
        for m in by_metric.values():
            assert m.higher_is_better is True


class TestCiiScoreAggregatorWithScenarioWeights:
    def test_aggregator_uses_provided_weights(self) -> None:
        from app.services.cii import aggregate_cii_score

        business_metrics = [
            {
                "slug": "economic_freedom",
                "normalized_value": 54.2,
                "weight": 0.35,
                "polarity": "positive",
            },
            {
                "slug": "rule_of_law",
                "normalized_value": 20.0,
                "weight": 0.25,
                "polarity": "positive",
            },
            {
                "slug": "corruption",
                "normalized_value": 26.0,
                "weight": 0.15,
                "polarity": "positive",
            },
            {
                "slug": "digital_access",
                "normalized_value": 21.0,
                "weight": 0.15,
                "polarity": "positive",
            },
            {
                "slug": "political_stability",
                "normalized_value": 13.0,
                "weight": 0.07,
                "polarity": "positive",
            },
            {
                "slug": "safety",
                "normalized_value": 38.0,
                "weight": 0.03,
                "polarity": "positive",
            },
        ]
        safety_metrics = [
            {
                "slug": "safety",
                "normalized_value": 38.0,
                "weight": 0.30,
                "polarity": "positive",
            },
            {
                "slug": "political_stability",
                "normalized_value": 13.0,
                "weight": 0.30,
                "polarity": "positive",
            },
            {
                "slug": "rule_of_law",
                "normalized_value": 20.0,
                "weight": 0.20,
                "polarity": "positive",
            },
            {
                "slug": "corruption",
                "normalized_value": 26.0,
                "weight": 0.15,
                "polarity": "positive",
            },
            {
                "slug": "economic_freedom",
                "normalized_value": 54.2,
                "weight": 0.03,
                "polarity": "positive",
            },
            {
                "slug": "digital_access",
                "normalized_value": 21.0,
                "weight": 0.02,
                "polarity": "positive",
            },
        ]
        biz_result = aggregate_cii_score(business_metrics)
        spr_result = aggregate_cii_score(safety_metrics)
        assert biz_result["overall_score"] > spr_result["overall_score"]
        assert biz_result["aggregation_method"] == "geometric"
        assert biz_result["formula_version"] == "cii-v1.0"

    def test_different_scenarios_different_scores(self) -> None:
        from app.services.cii import aggregate_cii_score

        russia_values = {
            "rule_of_law": 20.0,
            "economic_freedom": 54.2,
            "political_stability": 13.0,
            "safety": 38.0,
            "corruption": 26.0,
            "digital_access": 21.0,
        }

        scores: dict[str, float] = {}
        for scenario_slug, weights in _WEIGHTS_BY_SCENARIO.items():
            metric_list = [
                {
                    "slug": slug,
                    "normalized_value": val,
                    "weight": weights[slug],
                    "polarity": "positive",
                }
                for slug, val in russia_values.items()
            ]
            result = aggregate_cii_score(metric_list)
            scores[scenario_slug] = result["overall_score"]

        unique_scores = {round(s, 1) for s in scores.values()}
        assert len(unique_scores) > 1, (
            "All scenario scores are identical — weights have no effect"
        )

    def test_geometric_aggregation_preserved(self) -> None:
        from app.services.cii import aggregate_cii_score
        import math

        metrics = [
            {
                "slug": "a",
                "normalized_value": 25.0,
                "weight": 0.5,
                "polarity": "positive",
            },
            {
                "slug": "b",
                "normalized_value": 100.0,
                "weight": 0.5,
                "polarity": "positive",
            },
        ]
        result = aggregate_cii_score(metrics)
        expected = math.exp(0.5 * math.log(25.0) + 0.5 * math.log(100.0))
        assert result["overall_score"] == pytest.approx(expected, abs=0.01)

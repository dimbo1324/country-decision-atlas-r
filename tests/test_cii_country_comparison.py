import pytest
from typing import Any
from unittest.mock import MagicMock, patch


_SVC_CMP = "app.services.cii_comparison"


_CII_ROWS = [
    {
        "country_slug": "russia",
        "country_name": "Russia",
        "iso2": "RU",
        "cii_score": 25.76,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "uruguay",
        "country_name": "Uruguay",
        "iso2": "UY",
        "cii_score": 68.82,
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
]

_METRIC_VALUES = [
    {
        "country_slug": "russia",
        "metric_slug": "rule_of_law",
        "value": 20.0,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "rule_of_law",
        "value": 72.0,
        "polarity": "positive",
    },
    {
        "country_slug": "russia",
        "metric_slug": "economic_freedom",
        "value": 54.2,
        "polarity": "positive",
    },
    {
        "country_slug": "uruguay",
        "metric_slug": "economic_freedom",
        "value": 68.1,
        "polarity": "positive",
    },
]

_SCENARIO_ROW = {"slug": "relocation_residence", "title": "Relocation and residence"}


def _make_connection() -> MagicMock:
    return MagicMock()


class TestBuildCiiComparison:
    def _run(
        self,
        country_slugs: list[str] | None = None,
        scenario_slug: str = "relocation_residence",
        locale: str = "en",
        cii_rows: list[dict[str, Any]] | None = None,
        metric_defs: list[dict[str, Any]] | None = None,
        metric_values: list[dict[str, Any]] | None = None,
        scenario_row: dict[str, Any] | None | bool = True,
    ) -> Any:
        from app.services.cii_comparison import build_cii_comparison

        if country_slugs is None:
            country_slugs = ["russia", "uruguay"]
        resolved_cii = cii_rows if cii_rows is not None else _CII_ROWS
        resolved_defs = metric_defs if metric_defs is not None else _METRIC_DEFS
        resolved_vals = metric_values if metric_values is not None else _METRIC_VALUES
        resolved_scenario = _SCENARIO_ROW if scenario_row is True else scenario_row

        with (
            patch(f"{_SVC_CMP}.get_cii_for_countries", return_value=resolved_cii),
            patch(
                f"{_SVC_CMP}.get_active_cii_metric_definitions",
                return_value=resolved_defs,
            ),
            patch(
                f"{_SVC_CMP}.get_cii_metric_values_for_countries",
                return_value=resolved_vals,
            ),
            patch(
                f"{_SVC_CMP}.get_scenario_for_cii_comparison",
                return_value=resolved_scenario,
            ),
        ):
            return build_cii_comparison(
                _make_connection(), country_slugs, scenario_slug, locale
            )

    def test_returns_two_countries(self) -> None:
        result = self._run()
        assert len(result.countries) == 2
        slugs = [c.slug for c in result.countries]
        assert "russia" in slugs
        assert "uruguay" in slugs

    def test_country_cii_scores_present(self) -> None:
        result = self._run()
        by_slug = {c.slug: c for c in result.countries}
        assert by_slug["russia"].cii_score == pytest.approx(25.76)
        assert by_slug["uruguay"].cii_score == pytest.approx(68.82)

    def test_metrics_sorted_by_display_order(self) -> None:
        result = self._run()
        orders = [m.display_order for m in result.metrics]
        assert orders == sorted(orders)

    def test_delta_is_correct(self) -> None:
        result = self._run()
        by_slug = {m.metric_slug: m for m in result.metrics}
        rol = by_slug["rule_of_law"]
        assert rol.delta == pytest.approx(abs(72.0 - 20.0), abs=0.01)

    def test_winner_is_higher_effective_value(self) -> None:
        result = self._run()
        by_slug = {m.metric_slug: m for m in result.metrics}
        assert by_slug["rule_of_law"].winner_country_slug == "uruguay"
        assert by_slug["economic_freedom"].winner_country_slug == "uruguay"

    def test_formula_version_and_aggregation_method_present(self) -> None:
        result = self._run()
        assert result.formula_version == "cii-v1.0"
        assert result.aggregation_method == "geometric"

    def test_scenario_title_used_from_row(self) -> None:
        result = self._run()
        assert result.scenario.title == "Relocation and residence"

    def test_scenario_slug_fallback_when_row_missing(self) -> None:
        result = self._run(scenario_row=None)
        assert result.scenario.title == "relocation_residence"

    def test_no_quality_warnings_when_data_complete(self) -> None:
        result = self._run()
        assert result.quality_warnings == []

    def test_missing_cii_adds_quality_warning(self) -> None:
        incomplete_rows = [
            {**_CII_ROWS[0], "cii_score": None},
            _CII_ROWS[1],
        ]
        result = self._run(cii_rows=incomplete_rows)
        assert any("russia" in w for w in result.quality_warnings)

    def test_missing_metric_value_adds_quality_warning(self) -> None:
        partial_vals = [
            v
            for v in _METRIC_VALUES
            if v["metric_slug"] != "rule_of_law" or v["country_slug"] != "russia"
        ]
        result = self._run(metric_values=partial_vals)
        assert any("russia" in w for w in result.quality_warnings)

    def test_unknown_country_adds_quality_warning(self) -> None:
        result = self._run(
            country_slugs=["russia", "unknown-country"],
            cii_rows=[_CII_ROWS[0]],
            metric_values=[v for v in _METRIC_VALUES if v["country_slug"] == "russia"],
        )
        assert any("unknown-country" in w for w in result.quality_warnings)

    def test_locale_ru_uses_russian_metric_names(self) -> None:
        result = self._run(locale="ru")
        names = [m.metric_name for m in result.metrics]
        assert "Верховенство права" in names

    def test_locale_en_uses_english_metric_names(self) -> None:
        result = self._run(locale="en")
        names = [m.metric_name for m in result.metrics]
        assert "Rule of Law" in names

    def test_higher_is_better_reflects_polarity(self) -> None:
        defs_with_negative = [
            {**_METRIC_DEFS[0], "polarity": "negative"},
            _METRIC_DEFS[1],
        ]
        result = self._run(metric_defs=defs_with_negative)
        by_slug = {m.metric_slug: m for m in result.metrics}
        assert by_slug["rule_of_law"].higher_is_better is False
        assert by_slug["economic_freedom"].higher_is_better is True

    def test_negative_polarity_inverts_effective_value(self) -> None:
        defs_with_negative = [
            {**_METRIC_DEFS[0], "polarity": "negative"},
        ]
        vals = [
            {
                "country_slug": "russia",
                "metric_slug": "rule_of_law",
                "value": 20.0,
                "polarity": "negative",
            },
            {
                "country_slug": "uruguay",
                "metric_slug": "rule_of_law",
                "value": 30.0,
                "polarity": "negative",
            },
        ]
        result = self._run(metric_defs=defs_with_negative, metric_values=vals)
        rol = result.metrics[0]
        for mv in rol.values:
            if mv.country_slug == "russia":
                assert mv.effective_value == pytest.approx(80.0)
            elif mv.country_slug == "uruguay":
                assert mv.effective_value == pytest.approx(70.0)

    def test_negative_polarity_winner_is_lower_raw(self) -> None:
        defs_with_negative = [
            {**_METRIC_DEFS[0], "polarity": "negative"},
        ]
        vals = [
            {
                "country_slug": "russia",
                "metric_slug": "rule_of_law",
                "value": 20.0,
                "polarity": "negative",
            },
            {
                "country_slug": "uruguay",
                "metric_slug": "rule_of_law",
                "value": 30.0,
                "polarity": "negative",
            },
        ]
        result = self._run(metric_defs=defs_with_negative, metric_values=vals)
        rol = result.metrics[0]
        assert rol.winner_country_slug == "russia"

    def test_tie_has_no_winner(self) -> None:
        vals = [
            {
                "country_slug": "russia",
                "metric_slug": "rule_of_law",
                "value": 50.0,
                "polarity": "positive",
            },
            {
                "country_slug": "uruguay",
                "metric_slug": "rule_of_law",
                "value": 50.0,
                "polarity": "positive",
            },
            {
                "country_slug": "russia",
                "metric_slug": "economic_freedom",
                "value": 60.0,
                "polarity": "positive",
            },
            {
                "country_slug": "uruguay",
                "metric_slug": "economic_freedom",
                "value": 60.0,
                "polarity": "positive",
            },
        ]
        result = self._run(metric_values=vals)
        by_slug = {m.metric_slug: m for m in result.metrics}
        assert by_slug["rule_of_law"].winner_country_slug is None
        assert by_slug["rule_of_law"].delta == pytest.approx(0.0)

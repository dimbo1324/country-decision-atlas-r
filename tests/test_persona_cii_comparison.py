"""Persona-adjusted CII comparisons reweight the overall score without changing per-metric winners."""

import pytest
from app.services import cii_comparison
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())


COUNTRIES = [
    {
        "country_slug": "alpha",
        "country_name": "Alpha",
        "iso2": "AA",
        "cii_score": 80.0,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
    {
        "country_slug": "beta",
        "country_name": "Beta",
        "iso2": "BB",
        "cii_score": 20.0,
        "cii_confidence": "high",
        "country_drift": None,
        "formula_version": "cii-v1.0",
        "aggregation_method": "geometric",
    },
]

METRIC_DEFS = [
    {
        "slug": "rule_of_law",
        "name_en": "Rule of Law",
        "name_ru": "Rule of Law",
        "polarity": "positive",
        "display_order": 1,
    },
    {
        "slug": "economic_freedom",
        "name_en": "Economic Freedom",
        "name_ru": "Economic Freedom",
        "polarity": "positive",
        "display_order": 2,
    },
]

METRIC_VALUES = [
    {
        "country_slug": "alpha",
        "metric_slug": "rule_of_law",
        "value": 100.0,
        "polarity": "positive",
    },
    {
        "country_slug": "alpha",
        "metric_slug": "economic_freedom",
        "value": 1.0,
        "polarity": "positive",
    },
    {
        "country_slug": "beta",
        "metric_slug": "rule_of_law",
        "value": 1.0,
        "polarity": "positive",
    },
    {
        "country_slug": "beta",
        "metric_slug": "economic_freedom",
        "value": 100.0,
        "polarity": "positive",
    },
]

PROFILE = {
    "persona": {
        "slug": "solo_founder",
        "name": "Solo founder",
        "description": None,
        "is_active": True,
        "display_order": 30,
    },
    "scenario_slug": "business_self_employment",
    "version": "v1.0",
    "weights": [
        {
            "metric_id": "m1",
            "metric_slug": "rule_of_law",
            "metric_name": "Rule of Law",
            "base_weight": 0.5,
            "modifier": -0.9,
            "adjusted_weight": 0.01,
        },
        {
            "metric_id": "m2",
            "metric_slug": "economic_freedom",
            "metric_name": "Economic Freedom",
            "base_weight": 0.5,
            "modifier": 0.9,
            "adjusted_weight": 0.99,
        },
    ],
    "weight_sum": 1.0,
}


def install_fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cii_comparison,
        "get_scenario_for_cii_comparison",
        lambda *_: {"slug": "business_self_employment", "title": "Business"},
    )
    monkeypatch.setattr(
        cii_comparison,
        "get_scenario_metric_weights",
        lambda *_: [
            {"metric_slug": "rule_of_law", "weight": 0.5},
            {"metric_slug": "economic_freedom", "weight": 0.5},
        ],
    )
    monkeypatch.setattr(
        cii_comparison,
        "get_cii_for_countries",
        lambda *_args, **_kwargs: COUNTRIES,
    )
    monkeypatch.setattr(
        cii_comparison,
        "get_active_cii_metric_definitions",
        lambda *_: METRIC_DEFS,
    )
    monkeypatch.setattr(
        cii_comparison,
        "get_cii_metric_values_for_countries",
        lambda *_: METRIC_VALUES,
    )


def test_compare_without_persona_uses_persisted_country_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fakes(monkeypatch)

    result = cii_comparison.build_cii_comparison(
        CONNECTION, ["alpha", "beta"], "business_self_employment", "en"
    )
    by_slug = {country.slug: country for country in result.countries}

    assert by_slug["alpha"].cii_score == 80.0
    assert by_slug["beta"].cii_score == 20.0
    assert result.applied_persona is None


def test_compare_with_persona_reweights_overall_score_but_not_metric_winners(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fakes(monkeypatch)
    monkeypatch.setattr(
        cii_comparison, "maybe_build_persona_weight_profile", lambda *_: PROFILE
    )

    result = cii_comparison.build_cii_comparison(
        CONNECTION,
        ["alpha", "beta"],
        "business_self_employment",
        "en",
        "solo_founder",
    )
    countries_by_slug = {country.slug: country for country in result.countries}
    metrics_by_slug = {metric.metric_slug: metric for metric in result.metrics}
    alpha_score = countries_by_slug["alpha"].cii_score
    beta_score = countries_by_slug["beta"].cii_score

    assert alpha_score is not None
    assert beta_score is not None
    assert beta_score > alpha_score
    assert metrics_by_slug["rule_of_law"].winner_country_slug == "alpha"
    assert metrics_by_slug["economic_freedom"].winner_country_slug == "beta"
    assert metrics_by_slug["economic_freedom"].base_weight == pytest.approx(0.5)
    assert metrics_by_slug["economic_freedom"].adjusted_weight == pytest.approx(
        0.99
    )
    assert result.applied_persona is not None
    assert result.applied_persona.slug == "solo_founder"

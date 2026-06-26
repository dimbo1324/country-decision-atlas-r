from app.api.v1 import countries as countries_route
from datetime import UTC, datetime
from psycopg import Connection
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())
NOW = datetime.now(UTC)


ROW = {
    "overall_score": 50.0,
    "confidence": "high",
    "drift": None,
    "version": "v1.0",
    "formula_version": "cii-v1.0",
    "aggregation_method": "geometric",
    "calculated_at": NOW,
    "metrics": [
        {
            "slug": "rule_of_law",
            "name_en": "Rule of Law",
            "name_ru": "Rule of Law",
            "score": 90.0,
            "weight": 0.5,
            "weighted_score": 45.0,
            "reliability": "high",
        },
        {
            "slug": "safety",
            "name_en": "Physical Safety",
            "name_ru": "Physical Safety",
            "score": 10.0,
            "weight": 0.5,
            "weighted_score": 5.0,
            "reliability": "high",
        },
    ],
}

PROFILE = {
    "persona": {
        "slug": "risk_averse_family",
        "name": "Risk-averse family",
        "description": "Safety-focused household.",
        "is_active": True,
        "display_order": 20,
    },
    "scenario_slug": "relocation_residence",
    "version": "v1.0",
    "weights": [
        {
            "metric_id": "m1",
            "metric_slug": "rule_of_law",
            "metric_name": "Rule of Law",
            "base_weight": 0.5,
            "modifier": -0.8,
            "adjusted_weight": 0.1,
        },
        {
            "metric_id": "m2",
            "metric_slug": "safety",
            "metric_name": "Physical Safety",
            "base_weight": 0.5,
            "modifier": 0.8,
            "adjusted_weight": 0.9,
        },
    ],
    "weight_sum": 1.0,
}


def test_country_cii_without_persona_preserves_persisted_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(countries_route, "get_country_cii", lambda *_: ROW)
    monkeypatch.setattr(
        countries_route,
        "get_scenario_metric_weights",
        lambda *_: [{"metric_slug": "rule_of_law", "weight": 0.5}],
    )

    result = countries_route.read_country_cii(
        "uruguay", CONNECTION, "en", "v1.0", "relocation_residence", None
    )

    assert result.overall_score == 50.0
    assert result.applied_persona is None
    assert result.persona_weight_profile is None


def test_country_cii_with_persona_uses_adjusted_runtime_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(countries_route, "get_country_cii", lambda *_: ROW)
    monkeypatch.setattr(
        countries_route,
        "get_scenario_metric_weights",
        lambda *_: [{"metric_slug": "rule_of_law", "weight": 0.5}],
    )
    monkeypatch.setattr(
        countries_route, "build_persona_weight_profile", lambda *_: PROFILE
    )
    monkeypatch.setattr(
        countries_route,
        "get_active_cii_metric_definitions",
        lambda *_: [
            {"slug": "rule_of_law", "polarity": "positive"},
            {"slug": "safety", "polarity": "positive"},
        ],
    )

    result = countries_route.read_country_cii(
        "uruguay",
        CONNECTION,
        "en",
        "v1.0",
        "relocation_residence",
        "risk_averse_family",
    )
    by_slug = {metric.slug: metric for metric in result.metrics}

    assert result.overall_score != 50.0
    assert result.applied_persona is not None
    assert result.applied_persona.slug == "risk_averse_family"
    assert by_slug["safety"].base_weight == pytest.approx(0.5)
    assert by_slug["safety"].modifier == pytest.approx(0.8)
    assert by_slug["safety"].adjusted_weight == pytest.approx(0.9)
    assert by_slug["safety"].weight == pytest.approx(0.9)

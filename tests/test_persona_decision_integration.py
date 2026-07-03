"""Decision runs with and without a persona: base vs. runtime-adjusted CII ranking."""

from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine
from psycopg import Connection
import pytest
from tests.test_decision_run import install_repository_fakes
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())


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
            "metric_slug": "economic_freedom",
            "metric_name": "Economic Freedom",
            "base_weight": 0.5,
            "modifier": 0.0,
            "adjusted_weight": 0.5,
        },
        {
            "metric_id": "m2",
            "metric_slug": "digital_access",
            "metric_name": "Digital Access",
            "base_weight": 0.5,
            "modifier": 0.0,
            "adjusted_weight": 0.5,
        },
    ],
    "weight_sum": 1.0,
}


def payload(persona: str | None = None) -> DecisionRunRequest:
    return DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="business_self_employment",
        locale="en",
        persona=persona,
    )


def test_decision_without_persona_keeps_base_ranking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())

    assert result.ranking_mode == "base"
    assert [item.country.slug for item in result.results] == ["uruguay", "russia"]
    assert all(item.persona_adjusted_score is None for item in result.results)


def test_decision_with_persona_ranks_by_runtime_adjusted_cii(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    monkeypatch.setattr(
        decision_engine, "build_persona_weight_profile", lambda *_: PROFILE
    )
    monkeypatch.setattr(
        decision_engine,
        "get_active_cii_metric_definitions",
        lambda *_: [
            {"slug": "economic_freedom", "polarity": "positive"},
            {"slug": "digital_access", "polarity": "positive"},
        ],
    )
    monkeypatch.setattr(
        decision_engine,
        "get_cii_metric_values_for_countries",
        lambda *_: [
            {
                "country_slug": "uruguay",
                "metric_slug": "economic_freedom",
                "value": 1.0,
                "polarity": "positive",
            },
            {
                "country_slug": "uruguay",
                "metric_slug": "digital_access",
                "value": 1.0,
                "polarity": "positive",
            },
            {
                "country_slug": "russia",
                "metric_slug": "economic_freedom",
                "value": 100.0,
                "polarity": "positive",
            },
            {
                "country_slug": "russia",
                "metric_slug": "digital_access",
                "value": 100.0,
                "polarity": "positive",
            },
        ],
    )

    result = decision_engine.run_decision(CONNECTION, payload("solo_founder"))
    by_slug = {item.country.slug: item for item in result.results}

    assert result.ranking_mode == "persona_adjusted"
    assert result.applied_persona is not None
    assert result.applied_persona.slug == "solo_founder"
    assert [item.country.slug for item in result.results] == ["russia", "uruguay"]
    assert by_slug["russia"].score == 42.0
    assert by_slug["russia"].persona_adjusted_score == pytest.approx(100.0)
    assert by_slug["russia"].persona_adjusted_rank == 1
    assert by_slug["russia"].persona_adjusted_label == "excellent"

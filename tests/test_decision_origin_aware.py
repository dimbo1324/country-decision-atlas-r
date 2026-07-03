"""Decision runs with an origin country: ranking is preserved and pair context is attached when available."""

from app.repositories import (
    country_pairs as country_pairs_repository,
    feature_flags as ff_repo,
)
from app.schemas.decision_engine import DecisionRunRequest
from app.schemas.decision_wizard import DecisionWizardAnswers
from app.services import decision_engine, decision_wizard
from app.services.decision_engine import helpers as decision_engine_helpers
from fastapi import HTTPException
from psycopg import Connection
import pytest
from tests.test_decision_run import install_repository_fakes, payload
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _payload_without_origin(
    scenario_slug: str = "relocation_residence",
) -> DecisionRunRequest:
    return DecisionRunRequest(
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug=scenario_slug,
        locale="en",
    )


def _install_personalization_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )


def test_decision_without_origin_preserves_previous_ranking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, _payload_without_origin())

    assert [item.country.slug for item in result.results] == ["uruguay", "russia"]
    assert [item.rank for item in result.results] == [1, 2]


def test_decision_without_origin_has_not_requested_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, _payload_without_origin())

    assert result.origin_context_status == "not_requested"
    assert result.origin_country is None
    assert all(item.country_pair_context is None for item in result.results)


def test_decision_with_origin_includes_origin_country(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())

    assert result.origin_country is not None
    assert result.origin_country.slug == "russia"


def test_decision_with_origin_includes_pair_context_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    monkeypatch.setattr(
        country_pairs_repository,
        "list_destination_compatibility",
        lambda *_: [
            {
                "id": "pair-1",
                "origin_slug": "russia",
                "destination_slug": "uruguay",
                "compatibility_label": "mixed",
                "confidence": "low",
                "freshness_status": "current",
                "practical_summary": "Practical summary",
                "visa_note": "Visa note",
                "banking_note": None,
                "tax_treaty_note": None,
                "flight_logistics_note": None,
                "timezone_note": None,
                "language_note": None,
                "migration_restriction_note": None,
            }
        ],
    )
    monkeypatch.setattr(
        country_pairs_repository,
        "list_pair_sources",
        lambda *_: [{"id": "source-1"}],
    )

    result = decision_engine.run_decision(CONNECTION, payload())
    by_slug = {item.country.slug: item for item in result.results}

    assert result.origin_context_status == "partial"
    assert by_slug["uruguay"].country_pair_context is not None
    assert by_slug["uruguay"].country_pair_context.compatibility_label == "mixed"
    assert by_slug["uruguay"].country_pair_context.source_ids == ["source-1"]
    assert by_slug["russia"].country_pair_context is None


def test_missing_pair_context_does_not_crash(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())

    assert result.origin_context_status == "not_available"
    assert all(item.country_pair_context is None for item in result.results)


def test_unknown_origin_returns_controlled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    request = DecisionRunRequest(
        origin_country_slug="unknown",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
    )

    with pytest.raises(HTTPException) as exc_info:
        decision_engine.run_decision(CONNECTION, request)

    assert exc_info.value.status_code == 404
    assert cast(dict[str, Any], exc_info.value.detail)["error"]["code"] == (
        "country_not_found"
    )


def test_persona_plus_origin_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    profile = {
        "persona": {
            "slug": "solo_founder",
            "name": "Solo founder",
            "description": None,
            "is_active": True,
            "display_order": 30,
        },
        "scenario_slug": "relocation_residence",
        "version": "v1.0",
        "weights": [
            {
                "metric_id": "m1",
                "metric_slug": "economic_freedom",
                "metric_name": "Economic Freedom",
                "base_weight": 1.0,
                "modifier": 0.0,
                "adjusted_weight": 1.0,
            }
        ],
        "weight_sum": 1.0,
    }
    monkeypatch.setattr(
        decision_engine_helpers, "build_persona_weight_profile", lambda *_: profile
    )
    monkeypatch.setattr(
        decision_engine_helpers,
        "get_active_cii_metric_definitions",
        lambda *_: [{"slug": "economic_freedom", "polarity": "positive"}],
    )
    monkeypatch.setattr(
        decision_engine_helpers,
        "get_cii_metric_values_for_countries",
        lambda *_: [
            {
                "country_slug": "uruguay",
                "metric_slug": "economic_freedom",
                "value": 80.0,
                "polarity": "positive",
            },
            {
                "country_slug": "russia",
                "metric_slug": "economic_freedom",
                "value": 20.0,
                "polarity": "positive",
            },
        ],
    )

    request = DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
        persona="solo_founder",
    )
    result = decision_engine.run_decision(CONNECTION, request)

    assert result.ranking_mode == "persona_adjusted"
    assert result.origin_country is not None
    assert result.origin_country.slug == "russia"
    assert result.origin_context_status == "not_available"


def test_custom_weights_plus_origin_works(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    request = DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
        custom_weights={
            "legalization_score": 1.0,
            "long_term_status_score": 0,
            "cost_of_living_score": 0,
            "safety_score": 0,
            "business_score": 0,
            "legal_stability_score": 0,
            "source_quality_score": 0,
        },
    )
    result = decision_engine.run_decision(CONNECTION, request)

    assert result.personalization.weight_mode == "custom"
    assert result.origin_country is not None
    assert result.origin_context_status == "not_available"


def test_wizard_with_origin_country_slug_does_not_crash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.repositories import (
        countries as countries_repository,
        decision_engine as decision_repository,
        personas as personas_repository,
    )

    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )
    monkeypatch.setattr(
        decision_repository,
        "get_decision_scenario",
        lambda *_: {"slug": "relocation_residence", "title": "Relocation"},
    )
    monkeypatch.setattr(
        personas_repository, "list_active_persona_slugs", lambda *_: ["family"]
    )
    monkeypatch.setattr(
        countries_repository,
        "list_active_country_slugs",
        lambda *_: ["russia", "uruguay"],
    )

    answers = DecisionWizardAnswers(
        primary_goal="residence",
        origin_country_slug="russia",
        family_status="family_with_children",
    )
    recommendation = decision_wizard.resolve_wizard_recommendation(CONNECTION, answers)

    assert recommendation.recommended_scenario_slug == "relocation_residence"
    assert "russia" in recommendation.candidate_country_slugs


def test_score_unchanged_with_origin_compared_to_without(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    with_origin = decision_engine.run_decision(CONNECTION, payload())
    without_origin = decision_engine.run_decision(CONNECTION, _payload_without_origin())

    scores_with = {item.country.slug: item.score for item in with_origin.results}
    scores_without = {item.country.slug: item.score for item in without_origin.results}
    assert scores_with == scores_without


def test_rank_unchanged_with_origin_compared_to_without(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    with_origin = decision_engine.run_decision(CONNECTION, payload())
    without_origin = decision_engine.run_decision(CONNECTION, _payload_without_origin())

    ranks_with = {item.country.slug: item.rank for item in with_origin.results}
    ranks_without = {item.country.slug: item.rank for item in without_origin.results}
    assert ranks_with == ranks_without

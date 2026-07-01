from app.repositories import (
    countries as countries_repository,
    decision_engine as decision_repository,
    feature_flags as ff_repo,
    personas as personas_repository,
)
from app.schemas.decision_wizard import DecisionWizardAnswers
from app.services import decision_wizard
from fastapi import HTTPException
from pydantic import ValidationError
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


ACTIVE_PERSONAS = [
    "digital_nomad",
    "family",
    "student",
    "entrepreneur",
    "low_budget_migrant",
    "investor",
    "skilled_worker",
]

ACTIVE_COUNTRIES = ["argentina", "russia", "uruguay"]


def _install_wizard_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
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


def _install_wizard_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "disabled",
            "access_tier": "public",
            "default_enabled": False,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": False}],
    )


def _install_repository_fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        decision_repository,
        "get_decision_scenario",
        lambda _conn, slug, _locale: {"slug": slug, "is_active": True},
    )
    monkeypatch.setattr(
        personas_repository,
        "list_active_persona_slugs",
        lambda _conn: list(ACTIVE_PERSONAS),
    )
    monkeypatch.setattr(
        countries_repository,
        "list_active_country_slugs",
        lambda _conn: list(ACTIVE_COUNTRIES),
    )


def _answers(**overrides: Any) -> DecisionWizardAnswers:
    base = {
        "primary_goal": "residence",
        "budget_level": "medium",
        "family_status": "solo",
        "work_priority": "medium",
        "safety_priority": "medium",
        "citizenship_priority": "medium",
        "business_priority": "medium",
        "timeframe": "unknown",
    }
    base.update(overrides)
    return DecisionWizardAnswers(**base)


CONNECTION = cast(Any, MagicMock())


def test_residence_goal_maps_to_relocation_residence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="residence")
    )
    assert result.recommended_scenario_slug == "relocation_residence"


def test_citizenship_goal_maps_to_permanent_residence_citizenship(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="citizenship")
    )
    assert result.recommended_scenario_slug == "permanent_residence_citizenship"


def test_business_goal_maps_to_business_self_employment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="business")
    )
    assert result.recommended_scenario_slug == "business_self_employment"


def test_low_budget_goal_maps_to_low_budget_living(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="low_budget")
    )
    assert result.recommended_scenario_slug == "low_budget_living"


def test_safety_goal_maps_to_safety_political_risk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="safety")
    )
    assert result.recommended_scenario_slug == "safety_political_risk"


def test_family_with_children_maps_to_family_persona(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(family_status="family_with_children")
    )
    assert result.recommended_persona_slug == "family"
    assert result.confidence == "high"


def test_business_answers_map_to_entrepreneur_persona(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="business", business_priority="high")
    )
    assert result.recommended_persona_slug == "entrepreneur"


def test_remote_work_answers_map_to_digital_nomad_persona(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(primary_goal="remote_work")
    )
    assert result.recommended_persona_slug == "digital_nomad"


def test_nonexistent_persona_mapping_returns_null_with_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    monkeypatch.setattr(
        personas_repository,
        "list_active_persona_slugs",
        lambda _conn: [],
    )
    result = decision_wizard.resolve_wizard_recommendation(
        CONNECTION, _answers(family_status="family_with_children")
    )
    assert result.recommended_persona_slug is None
    assert "recommended_persona_unavailable" in result.warnings


def test_initial_weights_include_all_expected_criteria(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(CONNECTION, _answers())
    assert set(result.initial_custom_weights) == {
        "legalization_score",
        "long_term_status_score",
        "cost_of_living_score",
        "safety_score",
        "business_score",
        "legal_stability_score",
        "source_quality_score",
    }
    assert sum(result.initial_custom_weights.values()) == pytest.approx(100.0)


def test_initial_weights_are_suitable_for_decision_run_custom_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(CONNECTION, _answers())
    for value in result.initial_custom_weights.values():
        assert 0 <= value <= 100


def test_same_input_gives_same_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    answers = _answers(primary_goal="business", business_priority="high")
    first = decision_wizard.resolve_wizard_recommendation(CONNECTION, answers)
    second = decision_wizard.resolve_wizard_recommendation(CONNECTION, answers)
    assert first.model_dump() == second.model_dump()


def test_invalid_answer_fails_validation() -> None:
    with pytest.raises(ValidationError):
        DecisionWizardAnswers(primary_goal="not_a_real_goal")


def test_wizard_disabled_returns_422(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_wizard_disabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    with pytest.raises(HTTPException) as exc:
        decision_wizard.resolve_wizard_recommendation(CONNECTION, _answers())
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "decision_wizard_disabled"


def test_candidate_countries_come_from_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_wizard_enabled(monkeypatch)
    _install_repository_fakes(monkeypatch)
    result = decision_wizard.resolve_wizard_recommendation(CONNECTION, _answers())
    assert result.candidate_country_slugs == ACTIVE_COUNTRIES

"""Analytics events emitted for custom-weight decision requests, and failure isolation."""

import pytest
from app.repositories import (
    analytics as analytics_repository,
    countries as countries_repository,
    decision_engine as decision_repository,
    feature_flags as ff_repo,
    personas as personas_repository,
)
from app.schemas.decision_engine import DecisionRunRequest
from app.schemas.decision_wizard import DecisionWizardAnswers
from app.services import decision_engine, decision_wizard
from tests.test_decision_run import install_repository_fakes, payload
from typing import Any, cast
from unittest.mock import MagicMock
from uuid import uuid4


CONNECTION = cast(Any, object())
ALL_CRITERIA = (
    "legalization_score",
    "long_term_status_score",
    "cost_of_living_score",
    "safety_score",
    "business_score",
    "legal_stability_score",
    "source_quality_score",
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


def _install_wizard_fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        decision_repository,
        "get_decision_scenario",
        lambda _conn, slug, _locale: {"slug": slug, "is_active": True},
    )
    monkeypatch.setattr(
        personas_repository,
        "list_active_persona_slugs",
        lambda _conn: ["family", "entrepreneur", "skilled_worker"],
    )
    monkeypatch.setattr(
        countries_repository,
        "list_active_country_slugs",
        lambda _conn: ["russia", "uruguay", "argentina"],
    )


def _capture_events(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []

    def fake_insert(_conn: Any, **kwargs: Any) -> Any:
        captured.append(kwargs)
        return uuid4()

    monkeypatch.setattr(
        analytics_repository, "insert_analytics_event", fake_insert
    )
    return captured


def _payload_with_weights(weights: dict[str, float]) -> DecisionRunRequest:
    return DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
        custom_weights=weights,
    )


def _wizard_answers(**overrides: Any) -> DecisionWizardAnswers:
    base = {
        "primary_goal": "business",
        "budget_level": "medium",
        "family_status": "solo",
        "work_priority": "high",
        "safety_priority": "medium",
        "citizenship_priority": "low",
        "business_priority": "high",
        "timeframe": "medium",
    }
    base.update(overrides)
    return DecisionWizardAnswers(**base)


def test_custom_weights_request_writes_analytics_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)
    captured = _capture_events(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    decision_engine.run_decision(
        CONNECTION,
        _payload_with_weights(weights),
        session_id="session-abcdefgh",
    )

    events = [
        e for e in captured if e["event_type"] == "decision_custom_weights_used"
    ]
    assert len(events) == 1
    assert events[0]["scenario_slug"] == "relocation_residence"
    assert events[0]["metadata"]["candidate_count"] == 2
    assert events[0]["metadata"]["criteria_count"] == 7
    assert events[0]["metadata"]["weight_mode"] == "custom"


def test_no_custom_weights_does_not_write_custom_weights_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    captured = _capture_events(monkeypatch)

    decision_engine.run_decision(
        CONNECTION, payload(), session_id="session-abcdefgh"
    )

    events = [
        e for e in captured if e["event_type"] == "decision_custom_weights_used"
    ]
    assert len(events) == 0


def test_missing_session_does_not_write_event_and_decision_still_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)
    captured = _capture_events(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    result = decision_engine.run_decision(
        CONNECTION, _payload_with_weights(weights), session_id=None
    )

    assert result.personalization.custom_weights_applied is True
    assert len(captured) == 0


def test_analytics_failure_does_not_break_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    def _boom(*_a: Any, **_kw: Any) -> Any:
        raise RuntimeError("analytics backend unavailable")

    monkeypatch.setattr(analytics_repository, "insert_analytics_event", _boom)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    result = decision_engine.run_decision(
        CONNECTION,
        _payload_with_weights(weights),
        session_id="session-abcdefgh",
    )
    assert result.personalization.custom_weights_applied is True


def test_wizard_resolve_writes_wizard_completed_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_personalization_enabled(monkeypatch)
    _install_wizard_fakes(monkeypatch)
    captured = _capture_events(monkeypatch)

    decision_wizard.resolve_wizard_recommendation(
        cast(Any, MagicMock()),
        _wizard_answers(),
        session_id="session-abcdefgh",
    )

    events = [
        e for e in captured if e["event_type"] == "decision_wizard_completed"
    ]
    assert len(events) == 1
    assert events[0]["metadata"]["primary_goal"] == "business"
    assert events[0]["metadata"]["recommended_scenario_slug"] == (
        "business_self_employment"
    )
    assert events[0]["metadata"]["confidence"] == "medium"


def test_analytics_failure_does_not_break_wizard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_personalization_enabled(monkeypatch)
    _install_wizard_fakes(monkeypatch)

    def _boom(*_a: Any, **_kw: Any) -> Any:
        raise RuntimeError("analytics backend unavailable")

    monkeypatch.setattr(analytics_repository, "insert_analytics_event", _boom)

    result = decision_wizard.resolve_wizard_recommendation(
        cast(Any, MagicMock()),
        _wizard_answers(),
        session_id="session-abcdefgh",
    )
    assert result.recommended_scenario_slug == "business_self_employment"


def test_metadata_does_not_contain_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)
    captured = _capture_events(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    decision_engine.run_decision(
        CONNECTION,
        _payload_with_weights(weights),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "ip" not in event["metadata"]


def test_metadata_does_not_contain_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)
    captured = _capture_events(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    decision_engine.run_decision(
        CONNECTION,
        _payload_with_weights(weights),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "user_agent" not in event["metadata"]


def test_metadata_does_not_contain_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_personalization_enabled(monkeypatch)
    _install_wizard_fakes(monkeypatch)
    captured = _capture_events(monkeypatch)

    decision_wizard.resolve_wizard_recommendation(
        cast(Any, MagicMock()),
        _wizard_answers(),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "email" not in event["metadata"]


def test_metadata_does_not_contain_telegram_user_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_personalization_enabled(monkeypatch)
    _install_wizard_fakes(monkeypatch)
    captured = _capture_events(monkeypatch)

    decision_wizard.resolve_wizard_recommendation(
        cast(Any, MagicMock()),
        _wizard_answers(),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "telegram_user_id" not in event["metadata"]


def test_metadata_does_not_contain_raw_custom_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)
    captured = _capture_events(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    decision_engine.run_decision(
        CONNECTION,
        _payload_with_weights(weights),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "custom_weights" not in event["metadata"]
        assert "safety_score" not in event["metadata"]


def test_metadata_does_not_contain_free_text_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_personalization_enabled(monkeypatch)
    _install_wizard_fakes(monkeypatch)
    captured = _capture_events(monkeypatch)

    decision_wizard.resolve_wizard_recommendation(
        cast(Any, MagicMock()),
        _wizard_answers(),
        session_id="session-abcdefgh",
    )

    for event in captured:
        assert "origin_country_slug" not in event["metadata"]
        assert "answers" not in event["metadata"]

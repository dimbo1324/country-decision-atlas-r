"""Decision runs with custom criterion weights: effective-weight recalculation without touching persisted scores."""

from app.repositories import (
    decision_engine as decision_repository,
    feature_flags as ff_repo,
)
from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine
from fastapi import HTTPException
import pytest
from tests.test_decision_run import install_repository_fakes, payload
from typing import Any, cast


ALL_CRITERIA = (
    "legalization_score",
    "long_term_status_score",
    "cost_of_living_score",
    "safety_score",
    "business_score",
    "legal_stability_score",
    "source_quality_score",
)

CONNECTION = cast(Any, object())


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


def _install_personalization_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
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


def _payload_with_weights(weights: dict[str, float]) -> DecisionRunRequest:
    return DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
        custom_weights=weights,
    )


def test_run_decision_without_custom_weights_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())
    body = result.model_dump(mode="json")

    assert body["personalization"]["weight_mode"] == "base"
    assert body["personalization"]["custom_weights_applied"] is False
    assert [item["country"]["slug"] for item in body["results"]] == [
        "uruguay",
        "russia",
    ]
    assert body["results"][0]["score"] == pytest.approx(78.0)
    assert body["results"][1]["score"] == pytest.approx(42.0)


def test_personalization_field_present_on_every_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())
    assert result.personalization is not None
    assert len(result.personalization.base_weights) == 7


def test_custom_weights_recalculate_effective_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    result = decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    body = result.model_dump(mode="json")

    assert body["personalization"]["custom_weights_applied"] is True
    assert body["personalization"]["weight_mode"] == "custom"
    effective = {
        item["criterion"]: item["weight"]
        for item in body["personalization"]["effective_weights"]
    }
    assert effective["safety_score"] == pytest.approx(1.0)


def test_custom_weights_change_runtime_score_without_touching_persisted_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    result = decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))

    uruguay_result = next(
        item for item in result.results if item.country.slug == "uruguay"
    )
    russia_result = next(
        item for item in result.results if item.country.slug == "russia"
    )
    assert uruguay_result.score == pytest.approx(72.0)
    assert russia_result.score == pytest.approx(34.0)
    assert uruguay_result.score != pytest.approx(78.0)
    assert russia_result.score != pytest.approx(42.0)


def test_custom_weights_do_not_mutate_persisted_breakdown_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    original_breakdowns = decision_repository.list_decision_score_breakdowns(
        CONNECTION, ["uruguay-relocation_residence-score"]
    )
    original_weights = [row["weight"] for row in original_breakdowns]

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["safety_score"] = 100.0
    decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))

    replayed_breakdowns = decision_repository.list_decision_score_breakdowns(
        CONNECTION, ["uruguay-relocation_residence-score"]
    )
    assert [row["weight"] for row in replayed_breakdowns] == original_weights


def test_incomplete_custom_weights_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 10.0)
    del weights["safety_score"]

    with pytest.raises(HTTPException) as exc:
        decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "custom_weights_incomplete"


def test_all_zero_custom_weights_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)

    with pytest.raises(HTTPException) as exc:
        decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "custom_weights_sum_zero"


def test_unknown_criterion_in_custom_weights_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 10.0)
    weights["unknown_score"] = 10.0

    with pytest.raises(HTTPException) as exc:
        decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "unknown_custom_weight_criterion"


def test_out_of_range_custom_weight_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 10.0)
    weights["safety_score"] = 101.0

    with pytest.raises(HTTPException) as exc:
        decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "custom_weight_out_of_range"


def test_custom_weights_rejected_when_feature_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_disabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 10.0)

    with pytest.raises(HTTPException) as exc:
        decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))
    detail = cast(dict[str, Any], exc.value.detail)
    assert exc.value.status_code == 422
    assert detail["error"]["code"] == "decision_personalization_disabled"


def test_request_without_custom_weights_ignores_disabled_feature_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_disabled(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())
    assert result.personalization.weight_mode == "base"


def test_custom_weights_do_not_change_persona_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    _install_personalization_enabled(monkeypatch)

    weights = dict.fromkeys(ALL_CRITERIA, 0.0)
    weights["cost_of_living_score"] = 100.0
    result = decision_engine.run_decision(CONNECTION, _payload_with_weights(weights))

    assert result.applied_persona is None
    assert result.persona_weight_profile is None
    assert result.ranking_mode == "base"
    for item in result.results:
        assert item.persona_adjusted_score is None
        assert item.persona_adjusted_label is None
        assert item.persona_adjusted_rank is None

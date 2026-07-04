"""Custom-weight validation, normalization, and effective-weight application for decision personalization."""

import pytest
from app.services.decision_personalization import (
    apply_effective_weights_to_breakdown,
    build_personalization_summary,
    normalize_custom_weights,
    resolve_weight_mode,
    validate_custom_weights,
)
from decimal import Decimal
from fastapi import HTTPException
from typing import Any, cast


ALLOWED_CRITERIA = (
    "legalization_score",
    "long_term_status_score",
    "cost_of_living_score",
    "safety_score",
    "business_score",
    "legal_stability_score",
    "source_quality_score",
)

_FULL_WEIGHTS: dict[str, Any] = {
    "legalization_score": 20,
    "long_term_status_score": 15,
    "cost_of_living_score": 10,
    "safety_score": 35,
    "business_score": 5,
    "legal_stability_score": 10,
    "source_quality_score": 5,
}


def _error_code(exc: HTTPException) -> str:
    detail = cast(dict[str, Any], exc.detail)
    return str(detail["error"]["code"])


class TestValidateCustomWeights:
    def test_full_weights_pass(self) -> None:
        validate_custom_weights(_FULL_WEIGHTS, ALLOWED_CRITERIA)

    def test_zero_individual_weight_allowed(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        weights["source_quality_score"] = 0
        validate_custom_weights(weights, ALLOWED_CRITERIA)

    def test_all_zero_weights_rejected(self) -> None:
        weights = dict.fromkeys(ALLOWED_CRITERIA, 0)
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "custom_weights_sum_zero"

    def test_unknown_criterion_rejected(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        weights["unknown_score"] = 10
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "unknown_custom_weight_criterion"

    def test_missing_criterion_rejected(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        del weights["safety_score"]
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "custom_weights_incomplete"

    def test_negative_weight_rejected(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        weights["safety_score"] = -1
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "custom_weight_out_of_range"

    def test_weight_above_100_rejected(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        weights["safety_score"] = 101
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "custom_weight_out_of_range"

    def test_non_numeric_weight_rejected(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        weights["safety_score"] = "not-a-number"
        with pytest.raises(HTTPException) as exc:
            validate_custom_weights(weights, ALLOWED_CRITERIA)
        assert exc.value.status_code == 422
        assert _error_code(exc.value) == "custom_weight_invalid"


class TestNormalizeCustomWeights:
    def test_none_returns_none(self) -> None:
        assert normalize_custom_weights(None, ALLOWED_CRITERIA) is None

    def test_normalized_sum_is_one(self) -> None:
        normalized = normalize_custom_weights(_FULL_WEIGHTS, ALLOWED_CRITERIA)
        assert normalized is not None
        assert sum(normalized.values()) == Decimal("1")

    def test_normalized_values_match_expected_ratios(self) -> None:
        normalized = normalize_custom_weights(_FULL_WEIGHTS, ALLOWED_CRITERIA)
        assert normalized is not None
        assert normalized["safety_score"] == Decimal("0.35")
        assert normalized["source_quality_score"] == Decimal("0.05")

    def test_deterministic_across_calls(self) -> None:
        first = normalize_custom_weights(_FULL_WEIGHTS, ALLOWED_CRITERIA)
        second = normalize_custom_weights(_FULL_WEIGHTS, ALLOWED_CRITERIA)
        assert first == second

    def test_invalid_input_raises(self) -> None:
        weights = dict(_FULL_WEIGHTS)
        del weights["safety_score"]
        with pytest.raises(HTTPException):
            normalize_custom_weights(weights, ALLOWED_CRITERIA)


class TestApplyEffectiveWeightsToBreakdown:
    def test_recalculates_weighted_score(self) -> None:
        breakdown = [
            {
                "criterion": "safety_score",
                "score": 80.0,
                "weight": 0.2,
                "weighted_score": 16.0,
            }
        ]
        effective = {"safety_score": Decimal("0.5")}
        result = apply_effective_weights_to_breakdown(breakdown, effective)
        assert result[0]["weight"] == 0.5
        assert result[0]["weighted_score"] == 40.0

    def test_does_not_mutate_input_breakdown(self) -> None:
        breakdown = [
            {
                "criterion": "safety_score",
                "score": 80.0,
                "weight": 0.2,
                "weighted_score": 16.0,
            }
        ]
        snapshot = [dict(item) for item in breakdown]
        apply_effective_weights_to_breakdown(
            breakdown, {"safety_score": Decimal("0.5")}
        )
        assert breakdown == snapshot

    def test_unmatched_criterion_left_unchanged(self) -> None:
        breakdown = [
            {
                "criterion": "safety_score",
                "score": 80.0,
                "weight": 0.2,
                "weighted_score": 16.0,
            }
        ]
        result = apply_effective_weights_to_breakdown(breakdown, {})
        assert result[0]["weight"] == 0.2
        assert result[0]["weighted_score"] == 16.0


class TestResolveWeightMode:
    def test_base(self) -> None:
        assert resolve_weight_mode(None, None) == "base"

    def test_persona(self) -> None:
        assert resolve_weight_mode("family", None) == "persona"

    def test_custom(self) -> None:
        assert (
            resolve_weight_mode(None, {"safety_score": Decimal("1")})
            == "custom"
        )

    def test_persona_custom(self) -> None:
        assert (
            resolve_weight_mode("family", {"safety_score": Decimal("1")})
            == "persona_custom"
        )


class TestBuildPersonalizationSummary:
    def test_base_summary(self) -> None:
        summary = build_personalization_summary(
            persona_slug=None,
            custom_weights_applied=False,
            base_weights={"safety_score": Decimal("0.5")},
            effective_weights={"safety_score": Decimal("0.5")},
        )
        assert summary["weight_mode"] == "base"
        assert summary["custom_weights_applied"] is False
        assert summary["base_weights"] == [
            {"criterion": "safety_score", "weight": 0.5}
        ]

    def test_persona_custom_summary(self) -> None:
        summary = build_personalization_summary(
            persona_slug="family",
            custom_weights_applied=True,
            base_weights={"safety_score": Decimal("0.5")},
            effective_weights={"safety_score": Decimal("0.8")},
        )
        assert summary["weight_mode"] == "persona_custom"
        assert summary["persona_slug"] == "family"
        assert summary["effective_weights"] == [
            {"criterion": "safety_score", "weight": 0.8}
        ]

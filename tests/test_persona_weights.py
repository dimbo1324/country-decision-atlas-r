"""Persona weight-profile algorithm: adjusted-weight building, modifier coverage validation, and normalization."""

import pytest
from app.repositories import personas as personas_repository
from decimal import Decimal
from fastapi import HTTPException
from typing import Any, cast
from unittest.mock import MagicMock


def _make_rows(
    modifiers: list[float],
    base_weights: list[float] | None = None,
) -> list[dict[str, Any]]:
    slugs = [
        "rule_of_law",
        "economic_freedom",
        "political_stability",
        "safety",
        "corruption",
        "digital_access",
    ]
    names = [
        "Rule of Law",
        "Economic Freedom",
        "Political Stability",
        "Physical Safety",
        "Anti-Corruption",
        "Digital Access",
    ]
    bw = base_weights or [1.0 / 6] * 6
    return [
        {
            "metric_id": f"uuid-{i}",
            "metric_slug": slugs[i],
            "metric_name": names[i],
            "base_weight": bw[i],
            "modifier": modifiers[i],
        }
        for i in range(6)
    ]


def _equal_rows() -> list[dict[str, Any]]:
    return _make_rows([0.0] * 6)


class TestBuildAdjustedWeightsAlgorithm:
    def test_zero_modifiers_preserve_base_weight_proportions(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([0.0] * 6, [0.10, 0.20, 0.15, 0.25, 0.15, 0.15])
        result = build_adjusted_weights(rows)

        by_slug = {r["metric_slug"]: r for r in result}
        ratio_safety = (
            by_slug["safety"]["adjusted_weight"]
            / by_slug["rule_of_law"]["adjusted_weight"]
        )
        assert ratio_safety == pytest.approx(2.5, abs=0.001)

    def test_positive_modifier_increases_relative_share(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([0.0, 0.0, 0.0, 0.5, 0.0, 0.0])
        result = build_adjusted_weights(rows)

        safety_adj = next(
            r["adjusted_weight"] for r in result if r["metric_slug"] == "safety"
        )
        others = [
            r["adjusted_weight"] for r in result if r["metric_slug"] != "safety"
        ]
        assert safety_adj > max(others)

    def test_negative_modifier_decreases_relative_share(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([0.0, -0.3, 0.0, 0.0, 0.0, 0.0])
        result = build_adjusted_weights(rows)

        ef = next(
            r["adjusted_weight"]
            for r in result
            if r["metric_slug"] == "economic_freedom"
        )
        rl = next(
            r["adjusted_weight"]
            for r in result
            if r["metric_slug"] == "rule_of_law"
        )
        assert ef < rl

    def test_adjusted_weights_are_non_negative(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([-0.5, -0.5, 0.0, 0.0, 0.0, 0.5])
        result = build_adjusted_weights(rows)

        for r in result:
            assert r["adjusted_weight"] >= 0.0

    def test_adjusted_weights_sum_to_1(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([0.1, -0.05, 0.05, 0.15, 0.0, 0.25])
        result = build_adjusted_weights(rows)

        total = sum(r["adjusted_weight"] for r in result)
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_input_rows_are_not_mutated(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = _make_rows([0.1, 0.0, 0.0, 0.15, 0.0, 0.25])
        original_keys = set(rows[0].keys())
        original_bw = rows[0]["base_weight"]

        build_adjusted_weights(rows)

        assert set(rows[0].keys()) == original_keys
        assert rows[0]["base_weight"] == original_bw
        assert "adjusted_weight" not in rows[0]

    def test_base_weights_not_rounded_before_normalization(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        bw = [float(Decimal("1") / Decimal("3"))] * 3
        rows = [
            {
                "metric_id": f"u{i}",
                "metric_slug": f"m{i}",
                "metric_name": f"M{i}",
                "base_weight": bw[i],
                "modifier": 0.0,
            }
            for i in range(3)
        ]
        result = build_adjusted_weights(rows)
        total = sum(r["adjusted_weight"] for r in result)
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_all_adjusted_clamped_to_zero_raises_degenerate(self) -> None:
        from app.services.persona_weights import build_adjusted_weights

        rows = [
            {
                "metric_id": "u1",
                "metric_slug": "a",
                "metric_name": "A",
                "base_weight": 0.5,
                "modifier": -1.0,
            },
            {
                "metric_id": "u2",
                "metric_slug": "b",
                "metric_name": "B",
                "base_weight": 0.5,
                "modifier": -1.0,
            },
        ]
        with pytest.raises(HTTPException) as exc_info:
            build_adjusted_weights(rows)
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert exc_info.value.status_code == 422
        assert detail["error"]["code"] == "persona_weights_degenerate"


class TestValidateModifierCoverage:
    def test_missing_modifier_raises_persona_modifier_incomplete(self) -> None:
        from app.services.persona_weights import validate_modifier_coverage

        rows: list[dict[str, Any]] = _make_rows(
            [0.1, 0.0, 0.0, 0.15, 0.0, 0.25]
        )
        rows[1] = {**rows[1], "modifier": None}
        with pytest.raises(HTTPException) as exc_info:
            validate_modifier_coverage(rows)
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert exc_info.value.status_code == 422
        assert detail["error"]["code"] == "persona_modifier_incomplete"
        assert (
            "economic_freedom"
            in detail["error"]["details"]["missing_metric_slugs"]
        )

    def test_empty_rows_raises_degenerate(self) -> None:
        from app.services.persona_weights import validate_modifier_coverage

        with pytest.raises(HTTPException) as exc_info:
            validate_modifier_coverage([])
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert exc_info.value.status_code == 422
        assert detail["error"]["code"] == "persona_weights_degenerate"

    def test_all_modifiers_present_passes(self) -> None:
        from app.services.persona_weights import validate_modifier_coverage

        rows = _equal_rows()
        validate_modifier_coverage(rows)


class TestEnsureAdjustedWeightsValid:
    def test_valid_weights_pass(self) -> None:
        from app.services.persona_weights import ensure_adjusted_weights_valid

        rows: list[dict[str, Any]] = [
            {"adjusted_weight": 0.5, "metric_slug": "a"},
            {"adjusted_weight": 0.5, "metric_slug": "b"},
        ]
        ensure_adjusted_weights_valid(rows)

    def test_negative_adjusted_weight_raises(self) -> None:
        from app.services.persona_weights import ensure_adjusted_weights_valid

        rows: list[dict[str, Any]] = [
            {"adjusted_weight": -0.1, "metric_slug": "a"},
            {"adjusted_weight": 1.1, "metric_slug": "b"},
        ]
        with pytest.raises(HTTPException) as exc_info:
            ensure_adjusted_weights_valid(rows)
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "persona_adjusted_weights_invalid"

    def test_sum_not_1_raises(self) -> None:
        from app.services.persona_weights import ensure_adjusted_weights_valid

        rows: list[dict[str, Any]] = [
            {"adjusted_weight": 0.4, "metric_slug": "a"},
            {"adjusted_weight": 0.4, "metric_slug": "b"},
        ]
        with pytest.raises(HTTPException) as exc_info:
            ensure_adjusted_weights_valid(rows)
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "persona_adjusted_weights_invalid"


_PERSONA_ROW = {
    "id": "persona-id-1",
    "slug": "digital_nomad",
    "name": "Digital nomad",
    "description": "Remote worker.",
    "is_active": True,
    "display_order": 10,
}

_WEIGHT_INPUT_ROWS: list[dict[str, Any]] = [
    {
        "metric_id": "m1",
        "metric_slug": "rule_of_law",
        "metric_name": "Rule of Law",
        "base_weight": 0.20,
        "modifier": 0.05,
    },
    {
        "metric_id": "m2",
        "metric_slug": "economic_freedom",
        "metric_name": "Economic Freedom",
        "base_weight": 0.10,
        "modifier": 0.05,
    },
    {
        "metric_id": "m3",
        "metric_slug": "political_stability",
        "metric_name": "Political Stability",
        "base_weight": 0.20,
        "modifier": 0.05,
    },
    {
        "metric_id": "m4",
        "metric_slug": "safety",
        "metric_name": "Physical Safety",
        "base_weight": 0.25,
        "modifier": 0.15,
    },
    {
        "metric_id": "m5",
        "metric_slug": "corruption",
        "metric_name": "Anti-Corruption",
        "base_weight": 0.15,
        "modifier": 0.00,
    },
    {
        "metric_id": "m6",
        "metric_slug": "digital_access",
        "metric_name": "Digital Access",
        "base_weight": 0.10,
        "modifier": 0.25,
    },
]


class TestBuildPersonaWeightProfile:
    def test_returns_profile_with_persona_metadata(
        self, monkeypatch: Any
    ) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert result["persona"]["slug"] == "digital_nomad"
        assert result["persona"]["name"] == "Digital nomad"

    def test_returns_profile_with_version(self, monkeypatch: Any) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert result["version"] == "v1.0"

    def test_returns_profile_with_adjusted_weights(
        self, monkeypatch: Any
    ) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert "weights" in result
        assert len(result["weights"]) == 6
        for w in result["weights"]:
            assert "adjusted_weight" in w

    def test_adjusted_weights_sum_to_1(self, monkeypatch: Any) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        total = sum(w["adjusted_weight"] for w in result["weights"])
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_unknown_persona_raises_persona_not_found(
        self, monkeypatch: Any
    ) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository, "get_persona_by_slug", lambda *_a, **_k: None
        )

        with pytest.raises(HTTPException) as exc_info:
            build_persona_weight_profile(
                MagicMock(), "relocation_residence", "nonexistent"
            )
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "persona_not_found"

    def test_no_scenario_weights_raises_scenario_not_found(
        self, monkeypatch: Any
    ) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: [],
        )

        with pytest.raises(HTTPException) as exc_info:
            build_persona_weight_profile(
                MagicMock(), "nonexistent_scenario", "digital_nomad"
            )
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "scenario_not_found"

    def test_profile_includes_scenario_slug(self, monkeypatch: Any) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert result["scenario_slug"] == "relocation_residence"

    def test_profile_weight_sum_field(self, monkeypatch: Any) -> None:
        from app.services.persona_weights import build_persona_weight_profile

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert result["weight_sum"] == pytest.approx(1.0, abs=1e-9)


class TestMaybeBuildPersonaWeightProfile:
    def test_none_persona_slug_returns_none(self) -> None:
        from app.services.persona_weights import (
            maybe_build_persona_weight_profile,
        )

        result = maybe_build_persona_weight_profile(
            MagicMock(), "relocation_residence", None
        )
        assert result is None

    def test_empty_string_persona_slug_returns_none(self) -> None:
        from app.services.persona_weights import (
            maybe_build_persona_weight_profile,
        )

        result = maybe_build_persona_weight_profile(
            MagicMock(), "relocation_residence", ""
        )
        assert result is None

    def test_valid_slug_returns_profile(self, monkeypatch: Any) -> None:
        from app.services.persona_weights import (
            maybe_build_persona_weight_profile,
        )

        monkeypatch.setattr(
            personas_repository,
            "get_persona_by_slug",
            lambda *_a, **_k: _PERSONA_ROW,
        )
        monkeypatch.setattr(
            personas_repository,
            "list_persona_weight_inputs",
            lambda *_a, **_k: _WEIGHT_INPUT_ROWS,
        )

        result = maybe_build_persona_weight_profile(
            MagicMock(), "relocation_residence", "digital_nomad"
        )

        assert result is not None
        assert result["persona"]["slug"] == "digital_nomad"

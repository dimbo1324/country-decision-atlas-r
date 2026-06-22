import math
import pytest
from typing import Any


def _mv(
    slug: str,
    normalized_value: float,
    weight: float,
    polarity: str = "positive",
    reliability: str = "high",
) -> dict[str, Any]:
    return {
        "slug": slug,
        "normalized_value": normalized_value,
        "weight": weight,
        "polarity": polarity,
        "reliability": reliability,
    }


class TestAggregateGeometric:
    def test_single_metric_equal_to_value(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 50.0, 1.0)])
        assert result["overall_score"] == pytest.approx(50.0, abs=0.1)

    def test_uniform_metrics_equal_to_value(self) -> None:
        from app.services.cii import aggregate_cii_score

        metrics = [_mv(f"m{i}", 60.0, 1.0) for i in range(6)]
        result = aggregate_cii_score(metrics)
        assert result["overall_score"] == pytest.approx(60.0, abs=0.1)

    def test_geometric_differs_from_linear_on_skewed_data(self) -> None:
        from app.services.cii import aggregate_cii_score

        metrics = [
            _mv("high", 90.0, 1.0),
            _mv("high2", 90.0, 1.0),
            _mv("high3", 90.0, 1.0),
            _mv("high4", 90.0, 1.0),
            _mv("high5", 90.0, 1.0),
            _mv("low", 5.0, 1.0),
        ]
        result = aggregate_cii_score(metrics)
        linear_avg = (90.0 * 5 + 5.0) / 6
        assert result["overall_score"] < linear_avg

    def test_one_very_low_metric_pulls_score_down(self) -> None:
        from app.services.cii import aggregate_cii_score

        metrics = [_mv(f"m{i}", 80.0, 1.0) for i in range(5)]
        metrics.append(_mv("low", 2.0, 1.0))
        result = aggregate_cii_score(metrics)
        assert result["overall_score"] < 50.0

    def test_aggregation_method_is_geometric(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 50.0, 1.0)])
        assert result["aggregation_method"] == "geometric"

    def test_formula_version_is_set(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 50.0, 1.0)])
        assert result["formula_version"] == "cii-v1.0"

    def test_score_clamped_to_100(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 100.0, 1.0)])
        assert result["overall_score"] <= 100.0

    def test_score_clamped_to_zero(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 0.0, 1.0)])
        assert result["overall_score"] >= 0.0

    def test_empty_metrics_returns_zero(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([])
        assert result["overall_score"] == 0.0
        assert len(result["warnings"]) > 0

    def test_no_valid_metrics_returns_zero(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score(
            [
                {
                    "slug": "x",
                    "normalized_value": None,
                    "weight": None,
                    "polarity": "positive",
                }
            ]
        )
        assert result["overall_score"] == 0.0

    def test_zero_value_protected_score(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score([_mv("m1", 0.0, 1.0), _mv("m2", 80.0, 1.0)])
        assert result["overall_score"] > 0.0

    def test_weighted_aggregation_matches_formula(self) -> None:
        from app.services.cii import aggregate_cii_score

        w1, w2 = 0.3, 0.7
        v1, v2 = 40.0, 80.0
        metrics = [_mv("m1", v1, w1), _mv("m2", v2, w2)]
        result = aggregate_cii_score(metrics)
        expected = math.exp(
            (w1 * math.log(max(v1, 1.0)) + w2 * math.log(max(v2, 1.0))) / (w1 + w2)
        )
        assert result["overall_score"] == pytest.approx(round(expected, 2), abs=0.01)

    def test_missing_normalized_value_yields_warning(self) -> None:
        from app.services.cii import aggregate_cii_score

        result = aggregate_cii_score(
            [
                {
                    "slug": "bad",
                    "normalized_value": None,
                    "weight": 0.5,
                    "polarity": "positive",
                }
            ]
        )
        assert any("missing normalized_value" in w for w in result["warnings"])


class TestPolarity:
    def test_positive_polarity_passes_through(self) -> None:
        from app.services.cii import _effective_value

        assert _effective_value(70.0, "positive") == pytest.approx(70.0)

    def test_negative_polarity_inverts(self) -> None:
        from app.services.cii import _effective_value

        assert _effective_value(70.0, "negative") == pytest.approx(30.0)

    def test_negative_polarity_zero_becomes_100(self) -> None:
        from app.services.cii import _effective_value

        assert _effective_value(0.0, "negative") == pytest.approx(100.0)

    def test_negative_polarity_100_becomes_0(self) -> None:
        from app.services.cii import _effective_value

        assert _effective_value(100.0, "negative") == pytest.approx(0.0)

    def test_negative_polarity_lowers_score(self) -> None:
        from app.services.cii import aggregate_cii_score

        high_cost = _mv("cost", 80.0, 1.0, polarity="negative")
        result = aggregate_cii_score([high_cost])
        assert result["overall_score"] < 50.0

    def test_aggregation_with_mixed_polarity(self) -> None:
        from app.services.cii import aggregate_cii_score

        metrics = [
            _mv("good", 80.0, 1.0, polarity="positive"),
            _mv("bad_thing_high_is_bad", 80.0, 1.0, polarity="negative"),
        ]
        result = aggregate_cii_score(metrics)
        pure_positive = aggregate_cii_score(
            [_mv("good", 80.0, 1.0), _mv("same", 80.0, 1.0)]
        )
        assert result["overall_score"] < pure_positive["overall_score"]


class TestProtectedScore:
    def test_zero_maps_to_one(self) -> None:
        from app.services.cii import _protected_score

        assert _protected_score(0.0) == pytest.approx(1.0)

    def test_positive_value_unchanged(self) -> None:
        from app.services.cii import _protected_score

        assert _protected_score(50.0) == pytest.approx(50.0)

    def test_small_positive_value_unchanged(self) -> None:
        from app.services.cii import _protected_score

        assert _protected_score(1.5) == pytest.approx(1.5)

    def test_value_less_than_one_maps_to_one(self) -> None:
        from app.services.cii import _protected_score

        assert _protected_score(0.5) == pytest.approx(1.0)


class TestComputeConfidence:
    def test_all_high_reliability_returns_high(self) -> None:
        from app.services.cii import compute_confidence

        metrics = [_mv(f"m{i}", 50.0, 1.0, reliability="high") for i in range(6)]
        assert compute_confidence(metrics) == "high"

    def test_all_low_reliability_returns_low(self) -> None:
        from app.services.cii import compute_confidence

        metrics = [_mv(f"m{i}", 50.0, 1.0, reliability="low") for i in range(6)]
        assert compute_confidence(metrics) == "low"

    def test_empty_returns_low(self) -> None:
        from app.services.cii import compute_confidence

        assert compute_confidence([]) == "low"

    def test_mixed_reliability_not_high(self) -> None:
        from app.services.cii import compute_confidence

        metrics = [
            _mv("m1", 50.0, 1.0, reliability="high"),
            _mv("m2", 50.0, 1.0, reliability="low"),
        ]
        result = compute_confidence(metrics)
        assert result in ("medium", "low")

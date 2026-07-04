"""Country drift methodology: impact weighting, net score computation, and label/confidence derivation."""

import pytest
from app.services.country_drift_methodology import (
    METHODOLOGY_VERSION,
    build_drift_input_summary,
    compute_net_score,
    confidence_for_drift,
    impact_level_weight,
    label_for_drift,
)
from decimal import Decimal


class TestImpactLevelWeight:
    def test_low(self) -> None:
        assert impact_level_weight("low") == Decimal("1")

    def test_medium(self) -> None:
        assert impact_level_weight("medium") == Decimal("2")

    def test_high(self) -> None:
        assert impact_level_weight("high") == Decimal("3")

    def test_critical(self) -> None:
        assert impact_level_weight("critical") == Decimal("4")

    def test_unknown_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="unknown impact_level"):
            impact_level_weight("catastrophic")


class TestComputeNetScore:
    def test_zero_total_weight_returns_none(self) -> None:
        assert (
            compute_net_score(
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
            )
            is None
        )

    def test_mixed_example(self) -> None:
        result = compute_net_score(
            Decimal("8"), Decimal("4"), Decimal("2"), Decimal("0"), Decimal("0")
        )
        assert result == Decimal("28.57")

    def test_fully_positive(self) -> None:
        result = compute_net_score(
            Decimal("10"),
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
        )
        assert result == Decimal("100.00")

    def test_fully_negative(self) -> None:
        result = compute_net_score(
            Decimal("0"),
            Decimal("10"),
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
        )
        assert result == Decimal("-100.00")

    def test_range_bounds(self) -> None:
        result = compute_net_score(
            Decimal("1"),
            Decimal("1"),
            Decimal("50"),
            Decimal("0"),
            Decimal("0"),
        )
        assert result is not None
        assert Decimal("-100") <= result <= Decimal("100")


class TestLabelForDrift:
    def test_event_count_below_minimum_gives_insufficient_data(self) -> None:
        assert label_for_drift(2, Decimal("50")) == "insufficient_data"

    def test_none_net_score_gives_insufficient_data(self) -> None:
        assert label_for_drift(10, None) == "insufficient_data"

    def test_net_score_at_negative_threshold_gives_negative(self) -> None:
        assert label_for_drift(5, Decimal("-15")) == "negative"

    def test_net_score_below_negative_threshold_gives_negative(self) -> None:
        assert label_for_drift(5, Decimal("-50")) == "negative"

    def test_net_score_just_above_negative_threshold_gives_stable(self) -> None:
        assert label_for_drift(5, Decimal("-14.99")) == "stable"

    def test_net_score_zero_gives_stable(self) -> None:
        assert label_for_drift(5, Decimal("0")) == "stable"

    def test_net_score_just_below_mildly_positive_threshold_gives_stable(
        self,
    ) -> None:
        assert label_for_drift(5, Decimal("14.99")) == "stable"

    def test_net_score_at_mildly_positive_threshold_gives_mildly_positive(
        self,
    ) -> None:
        assert label_for_drift(5, Decimal("15")) == "mildly_positive"

    def test_net_score_just_below_positive_threshold_gives_mildly_positive(
        self,
    ) -> None:
        assert label_for_drift(5, Decimal("39.99")) == "mildly_positive"

    def test_net_score_at_positive_threshold_gives_positive(self) -> None:
        assert label_for_drift(5, Decimal("40")) == "positive"

    def test_net_score_above_positive_threshold_gives_positive(self) -> None:
        assert label_for_drift(5, Decimal("100")) == "positive"


class TestConfidenceForDrift:
    def test_zero_events_gives_low(self) -> None:
        assert confidence_for_drift(0, 0, 0) == "low"

    def test_two_events_gives_low(self) -> None:
        assert confidence_for_drift(2, 0, 0) == "low"

    def test_four_events_gives_low(self) -> None:
        assert confidence_for_drift(4, 0, 0) == "low"

    def test_five_events_gives_medium(self) -> None:
        assert confidence_for_drift(5, 0, 0) == "medium"

    def test_seven_events_gives_medium(self) -> None:
        assert confidence_for_drift(7, 0, 0) == "medium"

    def test_eight_events_gives_high(self) -> None:
        assert confidence_for_drift(8, 0, 0) == "high"

    def test_many_events_gives_high(self) -> None:
        assert confidence_for_drift(20, 0, 0) == "high"

    def test_high_downgraded_to_medium_when_ratio_exceeded(self) -> None:
        assert confidence_for_drift(8, 3, 2) == "medium"

    def test_medium_downgraded_to_low_when_ratio_exceeded(self) -> None:
        assert confidence_for_drift(5, 2, 1) == "low"

    def test_low_stays_low_when_ratio_exceeded(self) -> None:
        assert confidence_for_drift(4, 2, 1) == "low"

    def test_ratio_exactly_at_forty_percent_does_not_downgrade(self) -> None:
        assert confidence_for_drift(10, 2, 2) == "high"

    def test_ratio_just_above_forty_percent_downgrades(self) -> None:
        assert confidence_for_drift(10, 3, 2) == "medium"


class TestBuildDriftInputSummary:
    def test_default_shape(self) -> None:
        summary = build_drift_input_summary()
        assert summary["methodology_version"] == METHODOLOGY_VERSION
        assert summary["window_days"] == 180
        assert summary["event_ids"] == []
        assert summary["legal_signal_ids"] == []

    def test_thresholds_present(self) -> None:
        summary = build_drift_input_summary()
        assert summary["label_thresholds"]["negative"] == "<= -15"
        assert summary["label_thresholds"]["stable"] == "-15..15"
        assert summary["label_thresholds"]["mildly_positive"] == "15..40"
        assert summary["label_thresholds"]["positive"] == ">= 40"

    def test_impact_level_weights_present(self) -> None:
        summary = build_drift_input_summary()
        assert summary["impact_level_weights"] == {
            "low": 1.0,
            "medium": 2.0,
            "high": 3.0,
            "critical": 4.0,
        }

    def test_custom_window_and_ids(self) -> None:
        summary = build_drift_input_summary(
            window_days=90,
            event_ids=["event-1"],
            legal_signal_ids=["signal-1"],
        )
        assert summary["window_days"] == 90
        assert summary["event_ids"] == ["event-1"]
        assert summary["legal_signal_ids"] == ["signal-1"]

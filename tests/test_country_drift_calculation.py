"""Country drift calculation: insufficient data, label outcomes, direction accumulation, confidence downgrade."""

from app.services.country_drift import calculate_country_drift
from decimal import Decimal
import pytest
from typing import Any


def _event(
    impact_direction: str,
    impact_level: str,
    event_id: str | None = None,
    legal_signal_id: str | None = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "legal_signal_id": legal_signal_id,
        "impact_direction": impact_direction,
        "impact_level": impact_level,
    }


class TestInsufficientData:
    def test_no_events_gives_insufficient_data_and_low_confidence(self) -> None:
        result = calculate_country_drift([])
        assert result.label == "insufficient_data"
        assert result.confidence == "low"
        assert result.net_score is None
        assert result.event_count == 0

    def test_one_event_gives_insufficient_data(self) -> None:
        result = calculate_country_drift([_event("positive", "high")])
        assert result.label == "insufficient_data"

    def test_two_events_gives_insufficient_data(self) -> None:
        result = calculate_country_drift(
            [_event("positive", "high"), _event("positive", "medium")]
        )
        assert result.label == "insufficient_data"


class TestLabelOutcomes:
    def test_three_negative_high_events_gives_negative(self) -> None:
        events = [_event("negative", "high") for _ in range(3)]
        result = calculate_country_drift(events)
        assert result.label == "negative"
        assert result.net_score == Decimal("-100.00")

    def test_balanced_positive_negative_gives_stable(self) -> None:
        events = [
            _event("positive", "medium"),
            _event("negative", "medium"),
            _event("neutral", "low"),
        ]
        result = calculate_country_drift(events)
        assert result.label == "stable"

    def test_moderate_positive_net_score_gives_mildly_positive(self) -> None:
        events = [
            _event("positive", "high"),
            _event("positive", "medium"),
            _event("negative", "medium"),
            _event("neutral", "low"),
        ]
        result = calculate_country_drift(events)
        assert result.net_score is not None
        assert Decimal("15") <= result.net_score < Decimal("40")
        assert result.label == "mildly_positive"

    def test_strong_positive_net_score_gives_positive(self) -> None:
        events = [_event("positive", "critical") for _ in range(5)]
        result = calculate_country_drift(events)
        assert result.net_score == Decimal("100.00")
        assert result.label == "positive"


class TestDirectionAccumulation:
    def test_neutral_events_increase_total_weight_but_not_positive_or_negative(
        self,
    ) -> None:
        events = [
            _event("positive", "medium"),
            _event("neutral", "high"),
            _event("neutral", "high"),
        ]
        result = calculate_country_drift(events)
        assert result.positive_weight == Decimal("2")
        assert result.negative_weight == Decimal("0")
        assert result.neutral_weight == Decimal("6")
        assert result.total_weight == Decimal("8")

    def test_mixed_events_increase_mixed_weight_and_count(self) -> None:
        events = [
            _event("positive", "low"),
            _event("mixed", "medium"),
            _event("mixed", "high"),
        ]
        result = calculate_country_drift(events)
        assert result.mixed_weight == Decimal("5")
        assert result.mixed_count == 2
        assert result.positive_weight == Decimal("1")
        assert result.negative_weight == Decimal("0")

    def test_uncertain_events_increase_uncertain_weight_and_count(self) -> None:
        events = [
            _event("positive", "low"),
            _event("uncertain", "medium"),
            _event("uncertain", "high"),
        ]
        result = calculate_country_drift(events)
        assert result.uncertain_weight == Decimal("5")
        assert result.uncertain_count == 2


class TestConfidenceDowngrade:
    def test_mixed_and_uncertain_downgrade_confidence(self) -> None:
        events = (
            [_event("positive", "low") for _ in range(4)]
            + [_event("mixed", "low") for _ in range(2)]
            + [_event("uncertain", "low") for _ in range(2)]
        )
        result = calculate_country_drift(events)
        assert result.event_count == 8
        assert result.mixed_count + result.uncertain_count == 4
        assert result.confidence == "medium"

    def test_high_confidence_without_downgrade(self) -> None:
        events = [_event("positive", "medium") for _ in range(8)]
        result = calculate_country_drift(events)
        assert result.confidence == "high"


class TestInvalidInputs:
    def test_invalid_impact_level_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="unknown impact_level"):
            calculate_country_drift([_event("positive", "catastrophic")])

    def test_invalid_impact_direction_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="unknown impact_direction"):
            calculate_country_drift([_event("bullish", "medium")])


class TestInputSummary:
    def test_input_summary_contains_event_ids(self) -> None:
        events = [
            _event("positive", "medium", event_id="event-1"),
            _event("negative", "low", event_id="event-2"),
            _event("neutral", "low", event_id="event-3"),
        ]
        result = calculate_country_drift(events)
        assert result.input_summary["event_ids"] == ["event-1", "event-2", "event-3"]

    def test_input_summary_contains_legal_signal_ids(self) -> None:
        events = [
            _event("positive", "medium", legal_signal_id="signal-1"),
            _event("negative", "low", legal_signal_id="signal-2"),
            _event("neutral", "low", legal_signal_id=None),
        ]
        result = calculate_country_drift(events)
        assert result.input_summary["legal_signal_ids"] == ["signal-1", "signal-2"]

    def test_input_summary_contains_direction_counts(self) -> None:
        events = [
            _event("positive", "medium"),
            _event("positive", "low"),
            _event("negative", "low"),
        ]
        result = calculate_country_drift(events)
        assert result.input_summary["direction_counts"] == {
            "positive": 2,
            "negative": 1,
            "neutral": 0,
            "mixed": 0,
            "uncertain": 0,
        }

    def test_input_summary_contains_methodology_version(self) -> None:
        result = calculate_country_drift([_event("positive", "low")] * 3)
        assert result.input_summary["methodology_version"] == "v1.0"


class TestNetScoreBoundaries:
    def test_net_score_at_negative_boundary_is_negative(self) -> None:
        events = [
            _event("positive", "low"),
            _event("negative", "critical"),
            _event("neutral", "low"),
        ]
        result = calculate_country_drift(events)
        assert result.net_score is not None
        assert result.net_score <= Decimal("-15")
        assert result.label == "negative"

    def test_total_weight_zero_cannot_happen_with_events(self) -> None:
        events = [_event("positive", "low") for _ in range(3)]
        result = calculate_country_drift(events)
        assert result.total_weight > Decimal("0")

    def test_no_events_gives_none_net_score(self) -> None:
        result = calculate_country_drift([])
        assert result.net_score is None
        assert result.total_weight == Decimal("0")


class TestDeterminism:
    def test_same_events_return_same_result(self) -> None:
        events = [
            _event("positive", "medium", event_id="event-1"),
            _event("negative", "low", event_id="event-2"),
            _event("mixed", "high", event_id="event-3"),
        ]
        first = calculate_country_drift(events)
        second = calculate_country_drift(events)
        assert first == second

    def test_input_rows_are_not_mutated(self) -> None:
        event = _event("positive", "medium", event_id="event-1")
        snapshot = dict(event)
        calculate_country_drift([event])
        assert event == snapshot

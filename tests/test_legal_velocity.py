"""Legal velocity scoring: insufficient-data thresholds and event-count-driven value bands."""

from app.services.legal_velocity import compute_legal_velocity_index
from copy import deepcopy
from datetime import date, timedelta


def event(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "event_id": "event-1",
        "event_date": date.today() - timedelta(days=20),
        "impact_direction": "positive",
        "impact_level": "medium",
        "source_id": "source-1",
        "evidence_item_id": "evidence-1",
    }
    row.update(overrides)
    return row


def test_no_events_is_insufficient_data() -> None:
    result = compute_legal_velocity_index([])
    assert result.value is None
    assert result.label == "insufficient_data"
    assert result.freshness_status == "unknown"


def test_one_event_is_insufficient_data() -> None:
    result = compute_legal_velocity_index([event()])
    assert result.value is None


def test_two_events_are_insufficient_data() -> None:
    result = compute_legal_velocity_index([event(event_id="1"), event(event_id="2")])
    assert result.value is None


def test_three_low_events_produce_low_or_moderate_value() -> None:
    result = compute_legal_velocity_index(
        [
            event(event_id="1", impact_level="low"),
            event(event_id="2", impact_level="low"),
            event(event_id="3", impact_level="low"),
        ]
    )
    assert result.value is not None
    assert result.label in {"low", "moderate"}


def test_high_and_critical_events_increase_value() -> None:
    low = compute_legal_velocity_index(
        [
            event(event_id="1", impact_level="low"),
            event(event_id="2", impact_level="low"),
            event(event_id="3", impact_level="low"),
        ]
    )
    high = compute_legal_velocity_index(
        [
            event(event_id="1", impact_level="critical"),
            event(event_id="2", impact_level="high"),
            event(event_id="3", impact_level="high"),
        ]
    )
    assert high.value is not None and low.value is not None
    assert high.value > low.value


def test_neutral_and_uncertain_events_contribute_less() -> None:
    directional = compute_legal_velocity_index(
        [
            event(event_id="1", impact_direction="positive"),
            event(event_id="2", impact_direction="negative"),
            event(event_id="3", impact_direction="positive"),
        ]
    )
    soft = compute_legal_velocity_index(
        [
            event(event_id="1", impact_direction="neutral"),
            event(event_id="2", impact_direction="uncertain"),
            event(event_id="3", impact_direction="neutral"),
        ]
    )
    assert directional.value is not None and soft.value is not None
    assert soft.value < directional.value


def test_mixed_contributes_less_than_positive_or_negative() -> None:
    mixed = compute_legal_velocity_index(
        [
            event(event_id="1", impact_direction="mixed"),
            event(event_id="2", impact_direction="mixed"),
            event(event_id="3", impact_direction="mixed"),
        ]
    )
    direct = compute_legal_velocity_index(
        [
            event(event_id="1", impact_direction="positive"),
            event(event_id="2", impact_direction="negative"),
            event(event_id="3", impact_direction="positive"),
        ]
    )
    assert mixed.value is not None and direct.value is not None
    assert mixed.value < direct.value


def test_value_capped_at_100() -> None:
    result = compute_legal_velocity_index(
        [event(event_id=str(index), impact_level="critical") for index in range(1, 10)]
    )
    assert result.value is not None
    assert result.value == 100


def test_label_boundaries_correct() -> None:
    assert (
        compute_legal_velocity_index(
            [
                event(event_id="1", impact_level="low"),
                event(event_id="2", impact_level="low"),
                event(event_id="3", impact_level="low"),
            ]
        ).label
        == "moderate"
    )
    assert (
        compute_legal_velocity_index(
            [
                event(event_id="1", impact_level="critical"),
                event(event_id="2", impact_level="critical"),
                event(event_id="3", impact_level="critical"),
            ]
        ).label
        == "critical"
    )


def test_confidence_low_medium_high_correct() -> None:
    low = compute_legal_velocity_index(
        [event(event_id=str(index)) for index in range(3)]
    )
    medium = compute_legal_velocity_index(
        [
            event(event_id=str(index), evidence_item_id=f"evidence-{index}")
            for index in range(4)
        ]
    )
    high = compute_legal_velocity_index(
        [
            event(event_id=str(index), evidence_item_id=f"evidence-{index}")
            for index in range(8)
        ]
    )
    assert low.confidence == "low"
    assert medium.confidence == "medium"
    assert high.confidence == "high"


def test_freshness_fresh_stale_unknown_correct() -> None:
    fresh = compute_legal_velocity_index(
        [event(event_id=str(index)) for index in range(3)]
    )
    stale = compute_legal_velocity_index(
        [
            event(event_id=str(index), event_date=date.today() - timedelta(days=180))
            for index in range(3)
        ]
    )
    unknown = compute_legal_velocity_index(
        [event(event_id=str(index), event_date=None) for index in range(3)]
    )
    assert fresh.freshness_status == "fresh"
    assert stale.freshness_status == "stale"
    assert unknown.freshness_status == "unknown"


def test_input_summary_includes_raw_points_and_counts() -> None:
    result = compute_legal_velocity_index(
        [event(event_id=str(index)) for index in range(3)]
    )
    assert result.input_summary["raw_points"] > 0
    assert result.input_summary["event_count"] == 3
    assert result.input_summary["source_count"] == 1
    assert result.input_summary["evidence_count"] == 1


def test_deterministic_for_same_input() -> None:
    rows = [event(event_id=str(index)) for index in range(3)]
    assert compute_legal_velocity_index(rows) == compute_legal_velocity_index(rows)


def test_input_events_are_not_mutated() -> None:
    rows = [event(event_id=str(index)) for index in range(3)]
    original = deepcopy(rows)
    compute_legal_velocity_index(rows)
    assert rows == original

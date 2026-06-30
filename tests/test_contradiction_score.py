from app.services.contradiction_score import compute_contradiction_score
from copy import deepcopy


def row(**overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "signal_id": "signal-1",
        "event_id": "event-1",
        "signal_type": "migration",
        "affected_groups": ["migrants"],
        "impact_direction": "positive",
        "impact_level": "medium",
        "source_type": "official",
        "source_id": "source-1",
        "evidence_item_id": "evidence-1",
        "confidence": "high",
    }
    item.update(overrides)
    return item


def test_no_inputs_is_insufficient_data() -> None:
    result = compute_contradiction_score([])
    assert result.value is None
    assert result.label == "insufficient_data"


def test_too_little_data_is_insufficient_data() -> None:
    result = compute_contradiction_score([row(), row(signal_id="2", event_id="2")])
    assert result.value is None


def test_same_direction_signals_are_low_contradiction() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", affected_groups=["migrants"]),
            row(signal_id="2", event_id="2", affected_groups=["families"]),
            row(signal_id="3", event_id="3", affected_groups=["tax"]),
        ]
    )
    assert result.value is not None
    assert result.label == "low"


def test_positive_negative_same_topic_increases_score() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_direction="positive"),
            row(signal_id="2", event_id="2", impact_direction="negative"),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    assert result.value is not None
    assert result.value >= 48


def test_positive_mixed_same_topic_increases_score_moderately() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_direction="positive"),
            row(signal_id="2", event_id="2", impact_direction="mixed"),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    assert result.value is not None
    assert 20 <= result.value < 48


def test_official_vs_non_official_disagreement_increases_score() -> None:
    result = compute_contradiction_score(
        [
            row(
                signal_id="1",
                event_id="1",
                source_type="official",
                impact_direction="positive",
            ),
            row(
                signal_id="2",
                event_id="2",
                source_type="media",
                impact_direction="negative",
            ),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    assert result.value is not None
    assert result.value >= 84


def test_high_impact_low_confidence_increases_score() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_level="critical", confidence="low"),
            row(signal_id="2", event_id="2", affected_groups=["families"]),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    assert result.value is not None
    assert result.value >= 24


def test_multiple_topic_contradictions_increase_score() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_direction="positive"),
            row(signal_id="2", event_id="2", impact_direction="negative"),
            row(
                signal_id="3",
                event_id="3",
                signal_type="tax",
                affected_groups=["tax"],
                impact_direction="positive",
            ),
            row(
                signal_id="4",
                event_id="4",
                signal_type="tax",
                affected_groups=["tax"],
                impact_direction="negative",
            ),
        ]
    )
    assert result.value is not None
    assert result.value >= 96


def test_value_capped_at_100() -> None:
    result = compute_contradiction_score(
        [
            row(
                signal_id=str(index),
                event_id=str(index),
                signal_type="migration" if index < 6 else "tax",
                affected_groups=["migrants"] if index < 6 else ["tax"],
                impact_direction="positive" if index % 2 else "negative",
                impact_level="critical",
                confidence="low",
                source_type="official" if index % 3 else "media",
            )
            for index in range(12)
        ]
    )
    assert result.value == 100


def test_confidence_cannot_be_high_with_small_sample() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", affected_groups=["migrants"]),
            row(signal_id="2", event_id="2", affected_groups=["families"]),
            row(signal_id="3", event_id="3", affected_groups=["tax"]),
        ]
    )
    assert result.confidence == "low"


def test_label_boundaries_correct() -> None:
    moderate = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_direction="positive"),
            row(signal_id="2", event_id="2", impact_direction="mixed"),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    critical = compute_contradiction_score(
        [
            row(
                signal_id=str(index),
                event_id=str(index),
                signal_type="migration" if index < 6 else "tax",
                affected_groups=["migrants"] if index < 6 else ["tax"],
                impact_direction="positive" if index % 2 else "negative",
                impact_level="critical",
                confidence="low",
                source_type="official" if index % 3 else "media",
            )
            for index in range(12)
        ]
    )
    assert moderate.label == "moderate"
    assert critical.label == "critical"


def test_input_summary_includes_topic_counts() -> None:
    result = compute_contradiction_score(
        [
            row(signal_id="1", event_id="1", impact_direction="positive"),
            row(signal_id="2", event_id="2", impact_direction="negative"),
            row(
                signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]
            ),
        ]
    )
    assert result.input_summary["topic_count"] == 2
    assert result.input_summary["signal_count"] == 3


def test_deterministic_output() -> None:
    rows = [
        row(signal_id="1", event_id="1", impact_direction="positive"),
        row(signal_id="2", event_id="2", impact_direction="negative"),
        row(signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]),
    ]
    assert compute_contradiction_score(rows) == compute_contradiction_score(rows)


def test_input_rows_are_not_mutated() -> None:
    rows = [
        row(signal_id="1", event_id="1", impact_direction="positive"),
        row(signal_id="2", event_id="2", impact_direction="negative"),
        row(signal_id="3", event_id="3", signal_type="tax", affected_groups=["tax"]),
    ]
    original = deepcopy(rows)
    compute_contradiction_score(rows)
    assert rows == original

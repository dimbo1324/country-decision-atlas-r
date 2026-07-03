"""Scenario risk scoring: insufficient-data thresholds and positive/negative signal impact."""

from app.services.scenario_risk import (
    SCENARIO_RELEVANCE,
    compute_scenario_specific_risk_score,
)
from copy import deepcopy
from datetime import date, timedelta


def signal(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "signal_id": "signal-1",
        "event_id": "event-1",
        "event_date": date.today() - timedelta(days=30),
        "signal_type": "migration",
        "impact_direction": "negative",
        "impact_level": "high",
        "affected_groups": ["migrants"],
        "source_id": "source-1",
        "evidence_item_id": "evidence-1",
    }
    row.update(overrides)
    return row


def test_no_relevant_signals_is_insufficient_data() -> None:
    result = compute_scenario_specific_risk_score(
        [signal(signal_type="education", affected_groups=["students"])],
        "business_self_employment",
    )
    assert result.value is None
    assert result.label == "insufficient_data"


def test_one_relevant_signal_is_insufficient_data() -> None:
    result = compute_scenario_specific_risk_score([signal()], "relocation_residence")
    assert result.value is None


def test_negative_high_signal_increases_risk() -> None:
    result = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "relocation_residence",
    )
    assert result.value is not None
    assert result.value > 35


def test_positive_high_signal_decreases_risk() -> None:
    positive = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", impact_direction="positive"),
            signal(signal_id="2", event_id="2", impact_direction="positive"),
        ],
        "relocation_residence",
    )
    negative = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "relocation_residence",
    )
    assert positive.value is not None and negative.value is not None
    assert positive.value < negative.value


def test_mixed_signal_moderately_increases_risk() -> None:
    mixed = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", impact_direction="mixed"),
            signal(signal_id="2", event_id="2", impact_direction="mixed"),
        ],
        "relocation_residence",
    )
    assert mixed.value is not None
    assert 35 < mixed.value < 60


def test_uncertain_signal_moderately_increases_risk() -> None:
    uncertain = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", impact_direction="uncertain"),
            signal(signal_id="2", event_id="2", impact_direction="uncertain"),
        ],
        "relocation_residence",
    )
    assert uncertain.value is not None
    assert 35 < uncertain.value < 60


def test_older_signal_contributes_less() -> None:
    fresh = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "relocation_residence",
    )
    old = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", event_date=date.today() - timedelta(days=600)),
            signal(
                signal_id="2",
                event_id="2",
                event_date=date.today() - timedelta(days=600),
            ),
        ],
        "relocation_residence",
    )
    assert fresh.value is not None and old.value is not None
    assert old.value < fresh.value


def test_irrelevant_signal_ignored() -> None:
    result = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1"),
            signal(signal_id="2", event_id="2"),
            signal(
                signal_id="3",
                event_id="3",
                signal_type="education",
                affected_groups=["students"],
            ),
        ],
        "relocation_residence",
    )
    assert result.input_summary["ignored_signal_count"] == 1


def test_weakly_relevant_signal_has_lower_contribution() -> None:
    direct = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "relocation_residence",
    )
    weak = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", signal_type="migration_policy", affected_groups=[]),
            signal(
                signal_id="2",
                event_id="2",
                signal_type="migration_policy",
                affected_groups=[],
            ),
        ],
        "relocation_residence",
    )
    assert direct.value is not None and weak.value is not None
    assert weak.value < direct.value


def test_value_clamped_to_zero() -> None:
    result = compute_scenario_specific_risk_score(
        [
            signal(
                signal_id=str(index),
                event_id=str(index),
                impact_direction="positive",
                impact_level="critical",
            )
            for index in range(8)
        ],
        "relocation_residence",
    )
    assert result.value == 0


def test_value_clamped_to_100() -> None:
    result = compute_scenario_specific_risk_score(
        [
            signal(signal_id=str(index), event_id=str(index), impact_level="critical")
            for index in range(8)
        ],
        "relocation_residence",
    )
    assert result.value == 100


def test_label_boundaries_correct() -> None:
    low = compute_scenario_specific_risk_score(
        [
            signal(signal_id="1", impact_direction="positive"),
            signal(signal_id="2", event_id="2", impact_direction="positive"),
        ],
        "relocation_residence",
    )
    critical = compute_scenario_specific_risk_score(
        [
            signal(signal_id=str(index), event_id=str(index), impact_level="critical")
            for index in range(8)
        ],
        "relocation_residence",
    )
    assert low.label == "low"
    assert critical.label == "critical"


def test_confidence_low_medium_high_correct() -> None:
    low = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "relocation_residence",
    )
    medium = compute_scenario_specific_risk_score(
        [
            signal(
                signal_id=str(index),
                event_id=str(index),
                evidence_item_id=f"evidence-{index}",
            )
            for index in range(3)
        ],
        "relocation_residence",
    )
    high = compute_scenario_specific_risk_score(
        [
            signal(
                signal_id=str(index),
                event_id=str(index),
                evidence_item_id=f"evidence-{index}",
            )
            for index in range(6)
        ],
        "relocation_residence",
    )
    assert low.confidence == "low"
    assert medium.confidence == "medium"
    assert high.confidence == "high"


def test_each_active_mvp_scenario_can_be_evaluated() -> None:
    for scenario_slug in SCENARIO_RELEVANCE:
        scenario = SCENARIO_RELEVANCE[scenario_slug]
        signal_type = sorted(scenario["signal_types"])[0]
        result = compute_scenario_specific_risk_score(
            [
                signal(signal_id="1", signal_type=signal_type),
                signal(signal_id="2", event_id="2", signal_type=signal_type),
            ],
            scenario_slug,
        )
        assert result.scenario_slug == scenario_slug


def test_unknown_scenario_returns_insufficient_data() -> None:
    result = compute_scenario_specific_risk_score(
        [signal(signal_id="1"), signal(signal_id="2", event_id="2")],
        "unknown",
    )
    assert result.value is None
    assert result.confidence == "low"


def test_deterministic_output() -> None:
    rows = [signal(signal_id="1"), signal(signal_id="2", event_id="2")]
    assert compute_scenario_specific_risk_score(
        rows, "relocation_residence"
    ) == compute_scenario_specific_risk_score(rows, "relocation_residence")


def test_input_rows_are_not_mutated() -> None:
    rows = [signal(signal_id="1"), signal(signal_id="2", event_id="2")]
    original = deepcopy(rows)
    compute_scenario_specific_risk_score(rows, "relocation_residence")
    assert rows == original

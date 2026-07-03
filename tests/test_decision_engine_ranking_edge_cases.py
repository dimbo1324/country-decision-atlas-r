"""Edge cases for decision ranking: confidence aggregation, tie-breaking, score-label and strength/weakness boundaries."""

from app.schemas.decision_engine import DecisionCountryRef, DecisionCountryResult
from app.services import decision_engine as service
from typing import Any


def _result(
    slug: str,
    score: float,
    confidence: str = "medium",
    persona_adjusted_score: float | None = None,
) -> DecisionCountryResult:
    return DecisionCountryResult(
        rank=0,
        country=DecisionCountryRef(
            id=slug, slug=slug, name=slug.title(), iso_code=None
        ),
        score=score,
        score_label=service._score_label_literal(score),
        summary="summary",
        strengths=[],
        weaknesses=[],
        risk_warnings=[],
        confidence=confidence,
        breakdown=[],
        sources=[],
        persona_adjusted_score=persona_adjusted_score,
    )


class TestAggregateConfidence:
    def test_empty_input_defaults_to_low(self) -> None:
        assert service.aggregate_confidence([]) == "low"

    def test_all_none_defaults_to_low(self) -> None:
        assert service.aggregate_confidence([None, None]) == "low"

    def test_unknown_strings_are_ignored_not_counted(self) -> None:
        assert service.aggregate_confidence(["not_a_level", None]) == "low"

    def test_all_high_is_high(self) -> None:
        assert service.aggregate_confidence(["high", "high", "high"]) == "high"

    def test_all_low_is_low(self) -> None:
        assert service.aggregate_confidence(["low", "low"]) == "low"

    def test_average_exactly_at_high_boundary_is_high(self) -> None:
        assert service.aggregate_confidence(["high", "medium"]) == "high"

    def test_average_just_below_high_boundary_is_medium(self) -> None:
        assert service.aggregate_confidence(["medium", "medium", "high"]) == "medium"

    def test_average_at_medium_boundary_is_medium(self) -> None:
        assert service.aggregate_confidence(["low", "medium", "medium", "medium"]) == (
            "medium"
        )

    def test_average_just_below_medium_boundary_is_low(self) -> None:
        assert service.aggregate_confidence(["low", "low", "high"]) == "low"

    def test_mixed_none_and_valid_values_ignores_none(self) -> None:
        assert service.aggregate_confidence([None, "high", None]) == "high"


class TestRankResultsTieBreaking:
    def test_higher_score_ranks_first(self) -> None:
        results = [_result("uruguay", 60.0), _result("argentina", 80.0)]
        ranked = service._rank_results(results)
        assert [r.country.slug for r in ranked] == ["argentina", "uruguay"]
        assert ranked[0].rank == 1
        assert ranked[1].rank == 2

    def test_exact_score_tie_broken_by_confidence(self) -> None:
        results = [
            _result("uruguay", 70.0, confidence="low"),
            _result("argentina", 70.0, confidence="high"),
        ]
        ranked = service._rank_results(results)
        assert ranked[0].country.slug == "argentina"
        assert ranked[0].rank == 1
        assert ranked[1].country.slug == "uruguay"

    def test_score_and_confidence_tie_broken_alphabetically_by_slug(self) -> None:
        results = [
            _result("uruguay", 70.0, confidence="medium"),
            _result("argentina", 70.0, confidence="medium"),
        ]
        ranked = service._rank_results(results)
        assert [r.country.slug for r in ranked] == ["argentina", "uruguay"]

    def test_full_three_way_tie_is_deterministic_and_stable_on_rerun(self) -> None:
        results = [
            _result("uruguay", 70.0, confidence="medium"),
            _result("argentina", 70.0, confidence="medium"),
            _result("georgia", 70.0, confidence="medium"),
        ]
        ranked_once = [r.country.slug for r in service._rank_results(list(results))]
        ranked_twice = [r.country.slug for r in service._rank_results(list(results))]
        assert ranked_once == ranked_twice == ["argentina", "georgia", "uruguay"]

    def test_ranks_are_reassigned_from_one_regardless_of_input_order(self) -> None:
        results = [_result("a", 10.0), _result("b", 90.0), _result("c", 50.0)]
        ranked = service._rank_results(results)
        assert [r.rank for r in ranked] == [1, 2, 3]
        assert [r.country.slug for r in ranked] == ["b", "c", "a"]


class TestPersonaAdjustedRanking:
    def test_missing_persona_score_treated_as_zero_and_ranks_last(self) -> None:
        results = [
            _result("uruguay", 70.0, persona_adjusted_score=None),
            _result("argentina", 70.0, persona_adjusted_score=55.0),
        ]
        ranked = service._rank_persona_adjusted_results(results)
        assert ranked[0].country.slug == "argentina"
        assert ranked[0].persona_adjusted_rank == 1
        assert ranked[1].country.slug == "uruguay"
        assert ranked[1].persona_adjusted_rank == 2

    def test_tie_on_persona_score_broken_by_confidence_then_slug(self) -> None:
        results = [
            _result("uruguay", 0, confidence="high", persona_adjusted_score=40.0),
            _result("argentina", 0, confidence="high", persona_adjusted_score=40.0),
        ]
        ranked = service._rank_persona_adjusted_results(results)
        assert [r.country.slug for r in ranked] == ["argentina", "uruguay"]


class TestStrengthWeaknessBoundaries:
    def test_score_of_exactly_seventy_counts_as_strength(self) -> None:
        breakdowns = [{"criterion": "safety_score", "score": 70, "source_ids": []}]
        strengths = service._build_strengths(breakdowns, "en")
        assert len(strengths) == 1

    def test_score_of_sixty_nine_is_not_a_strength(self) -> None:
        breakdowns = [{"criterion": "safety_score", "score": 69, "source_ids": []}]
        assert service._build_strengths(breakdowns, "en") == []

    def test_score_of_exactly_fifty_counts_as_weakness(self) -> None:
        breakdowns = [{"criterion": "safety_score", "score": 50, "source_ids": []}]
        weaknesses = service._build_weaknesses(breakdowns, "en")
        assert len(weaknesses) == 1

    def test_score_of_fifty_one_is_not_a_weakness(self) -> None:
        breakdowns = [{"criterion": "safety_score", "score": 51, "source_ids": []}]
        assert service._build_weaknesses(breakdowns, "en") == []

    def test_mid_range_score_is_neither_strength_nor_weakness(self) -> None:
        breakdowns = [{"criterion": "safety_score", "score": 60, "source_ids": []}]
        assert service._build_strengths(breakdowns, "en") == []
        assert service._build_weaknesses(breakdowns, "en") == []


class TestScoreLabelThresholds:
    def test_boundary_values_map_to_expected_labels(self) -> None:
        assert service._score_label_literal(29.99) == "weak"
        assert service._score_label_literal(30) == "limited"
        assert service._score_label_literal(49.99) == "limited"
        assert service._score_label_literal(50) == "moderate"
        assert service._score_label_literal(69.99) == "moderate"
        assert service._score_label_literal(70) == "strong"
        assert service._score_label_literal(84.99) == "strong"
        assert service._score_label_literal(85) == "excellent"
        assert service._score_label_literal(100) == "excellent"
        assert service._score_label_literal(0) == "weak"


class TestSourceIdHelpers:
    def test_source_ids_returns_empty_for_non_sequence_values(self) -> None:
        assert service._source_ids(None) == []
        assert service._source_ids("not-a-list") == []
        assert service._source_ids(42) == []

    def test_source_ids_stringifies_list_items(self) -> None:
        assert service._source_ids([1, "two", 3]) == ["1", "two", "3"]

    def test_collect_source_ids_dedupes_and_sorts(self) -> None:
        breakdowns: list[dict[str, Any]] = [
            {"source_ids": ["b", "a"]},
            {"source_ids": ["a"]},
        ]
        legal_signals: list[dict[str, Any]] = [
            {"source_id": "c"},
            {"source_id": None},
        ]
        result = service._collect_source_ids(breakdowns, legal_signals)
        assert result == ["a", "b", "c"]

    def test_collect_source_ids_empty_when_nothing_present(self) -> None:
        assert service._collect_source_ids([], []) == []


class TestGroupBy:
    def test_group_by_partitions_rows_by_key(self) -> None:
        rows = [
            {"country_slug": "uruguay", "id": 1},
            {"country_slug": "uruguay", "id": 2},
            {"country_slug": "argentina", "id": 3},
        ]
        grouped = service._group_by(rows, "country_slug")
        assert len(grouped["uruguay"]) == 2
        assert len(grouped["argentina"]) == 1

    def test_group_by_empty_rows_returns_empty_dict(self) -> None:
        assert service._group_by([], "country_slug") == {}

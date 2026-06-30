from app.services.trust_score import (
    METHODOLOGY_VERSION,
    compute_confidence,
    compute_contradiction_component,
    compute_evidence_depth_score,
    compute_freshness_score,
    compute_review_coverage_score,
    compute_source_quality_score,
    compute_trust_label,
    compute_trust_score_from_inputs,
    has_sufficient_data,
)
from datetime import UTC, datetime
import pytest


_NOW = datetime(2025, 1, 1, tzinfo=UTC)


class TestSourceQualityScore:
    def test_zero_sources(self) -> None:
        assert compute_source_quality_score(0) == 0

    def test_one_source(self) -> None:
        assert compute_source_quality_score(1) == 35

    def test_four_sources(self) -> None:
        assert compute_source_quality_score(4) == 35

    def test_five_sources(self) -> None:
        assert compute_source_quality_score(5) == 55

    def test_ten_sources(self) -> None:
        assert compute_source_quality_score(10) == 75

    def test_fifteen_sources(self) -> None:
        assert compute_source_quality_score(15) == 100

    def test_twenty_sources(self) -> None:
        assert compute_source_quality_score(20) == 100


class TestEvidenceDepthScore:
    def test_zero_evidence(self) -> None:
        assert compute_evidence_depth_score(0) == 0

    def test_one_evidence(self) -> None:
        assert compute_evidence_depth_score(1) == 30

    def test_five_evidence(self) -> None:
        assert compute_evidence_depth_score(5) == 50

    def test_ten_evidence(self) -> None:
        assert compute_evidence_depth_score(10) == 75

    def test_twenty_evidence(self) -> None:
        assert compute_evidence_depth_score(20) == 100


class TestFreshnessScore:
    def test_none_last_verified(self) -> None:
        score, status = compute_freshness_score(None, _NOW)
        assert score == 35
        assert status == "unknown"

    def test_fresh_within_180_days(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=90)
        score, status = compute_freshness_score(last, _NOW)
        assert score == 100
        assert status == "fresh"

    def test_aging_between_180_and_365(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=200)
        score, status = compute_freshness_score(last, _NOW)
        assert score == 70
        assert status == "aging"

    def test_stale_over_365(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=400)
        score, status = compute_freshness_score(last, _NOW)
        assert score == 40
        assert status == "stale"

    def test_exactly_180_days(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=180)
        score, status = compute_freshness_score(last, _NOW)
        assert score == 100
        assert status == "fresh"


class TestReviewCoverageScore:
    def test_all_zero(self) -> None:
        assert compute_review_coverage_score(0, 0, 0, 0) == 0

    def test_small_coverage(self) -> None:
        assert compute_review_coverage_score(1, 1, 1, 0) == 30

    def test_medium_coverage(self) -> None:
        assert compute_review_coverage_score(5, 5, 2, 2) == 55

    def test_large_coverage(self) -> None:
        assert compute_review_coverage_score(10, 10, 5, 5) == 88

    def test_high_coverage(self) -> None:
        assert compute_review_coverage_score(15, 15, 8, 5) == 88

    def test_maximum_coverage(self) -> None:
        assert compute_review_coverage_score(20, 20, 10, 10) == 100


class TestContradictionComponent:
    def test_none_contradiction_score(self) -> None:
        score, missing = compute_contradiction_component(None)
        assert score == 50.0
        assert missing is True

    def test_zero_contradiction(self) -> None:
        score, missing = compute_contradiction_component(0.0)
        assert score == 100.0
        assert missing is False

    def test_full_contradiction(self) -> None:
        score, missing = compute_contradiction_component(100.0)
        assert score == 0.0
        assert missing is False

    def test_partial_contradiction(self) -> None:
        score, missing = compute_contradiction_component(40.0)
        assert score == pytest.approx(60.0)
        assert missing is False


class TestTrustLabel:
    def test_none_score(self) -> None:
        assert compute_trust_label(None) == "insufficient_data"

    def test_very_high(self) -> None:
        assert compute_trust_label(90.0) == "very_high"

    def test_high(self) -> None:
        assert compute_trust_label(75.0) == "high"

    def test_medium(self) -> None:
        assert compute_trust_label(55.0) == "medium"

    def test_low(self) -> None:
        assert compute_trust_label(35.0) == "low"

    def test_very_low(self) -> None:
        assert compute_trust_label(20.0) == "very_low"

    def test_boundary_85(self) -> None:
        assert compute_trust_label(85.0) == "very_high"

    def test_boundary_70(self) -> None:
        assert compute_trust_label(70.0) == "high"


class TestComputeConfidence:
    def test_high_confidence(self) -> None:
        assert compute_confidence(15, 20, 8, "fresh") == "high"

    def test_high_confidence_aging(self) -> None:
        assert compute_confidence(15, 20, 8, "aging") == "high"

    def test_medium_confidence(self) -> None:
        assert compute_confidence(10, 10, 5, "stale") == "medium"

    def test_low_confidence_insufficient(self) -> None:
        assert compute_confidence(3, 3, 2, "stale") == "low"

    def test_high_requires_fresh_or_aging(self) -> None:
        assert compute_confidence(15, 20, 8, "stale") == "medium"


class TestHasSufficientData:
    def test_sufficient(self) -> None:
        assert has_sufficient_data(5, 5, 3) is True

    def test_insufficient_sources(self) -> None:
        assert has_sufficient_data(4, 5, 3) is False

    def test_insufficient_evidence(self) -> None:
        assert has_sufficient_data(5, 4, 3) is False

    def test_insufficient_legal(self) -> None:
        assert has_sufficient_data(5, 5, 2) is False


class TestComputeTrustScoreFromInputs:
    def _inputs(
        self,
        source_count: int = 10,
        evidence_count: int = 15,
        legal_signal_count: int = 5,
        route_count: int = 3,
        platform_metric_count: int = 2,
        last_verified_at: datetime | None = None,
        contradiction_score_value: float | None = None,
    ) -> dict[str, object]:
        return {
            "country_id": "test-country-uuid",
            "source_count": source_count,
            "evidence_count": evidence_count,
            "legal_signal_count": legal_signal_count,
            "route_count": route_count,
            "platform_metric_count": platform_metric_count,
            "last_verified_at": last_verified_at,
            "contradiction_score_value": contradiction_score_value,
        }

    def test_returns_methodology_version(self) -> None:
        result = compute_trust_score_from_inputs(self._inputs(), _NOW)
        assert result["methodology_version"] == METHODOLOGY_VERSION

    def test_insufficient_data_returns_none_score(self) -> None:
        inputs = self._inputs(source_count=2, evidence_count=2, legal_signal_count=1)
        result = compute_trust_score_from_inputs(inputs, _NOW)
        assert result["trust_score"] is None
        assert result["trust_label"] == "insufficient_data"

    def test_downside_cap_applied(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=400)
        inputs = self._inputs(
            source_count=15,
            evidence_count=20,
            last_verified_at=last,
            contradiction_score_value=None,
        )
        result = compute_trust_score_from_inputs(inputs, _NOW)
        if result["trust_score"] is not None:
            freshness_score = 40.0
            assert result["trust_score"] <= freshness_score + 20.0

    def test_input_summary_has_components(self) -> None:
        result = compute_trust_score_from_inputs(self._inputs(), _NOW)
        assert "input_summary" in result
        summary = result["input_summary"]
        assert "components" in summary

    def test_with_fresh_data_and_no_contradiction(self) -> None:
        from datetime import timedelta

        last = _NOW - timedelta(days=10)
        inputs = self._inputs(
            source_count=15,
            evidence_count=20,
            legal_signal_count=8,
            last_verified_at=last,
            contradiction_score_value=0.0,
        )
        result = compute_trust_score_from_inputs(inputs, _NOW)
        assert result["trust_score"] is not None
        assert result["trust_score"] > 50.0

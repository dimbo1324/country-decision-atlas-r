"""Reusable methodology configuration fixtures for unit tests."""

from app.services.methodology_config import (
    BoardLimits,
    ConfidenceThresholds,
    DecisionThresholds,
    MethodologyConfig,
    RecommendationThresholds,
    ScoreLabelThresholds,
    TripWarningThresholds,
)


def methodology_config() -> MethodologyConfig:
    return MethodologyConfig(
        version="v1.0",
        parameters={},
        score_labels=score_label_thresholds(),
        decision=DecisionThresholds(
            strength_min_score=70.0,
            weakness_max_score=50.0,
            confidence=ConfidenceThresholds(
                high_min_average=2.5,
                medium_min_average=1.7,
            ),
            recommendation=RecommendationThresholds(
                tie_delta_below=3.0,
                medium_confidence_delta_below=10.0,
            ),
        ),
        board=BoardLimits(
            max_active_posts=5,
            max_contact_requests_per_day=20,
            max_reports_per_day=20,
        ),
        flows_k_anonymity=20,
        trip_warnings=TripWarningThresholds(
            high_impact_min_rank=3,
            restrictive_pair_severity_rank=3,
            missing_pair_severity_rank=2,
        ),
    )


def score_label_thresholds() -> ScoreLabelThresholds:
    return ScoreLabelThresholds(
        weak_below=30.0,
        limited_below=50.0,
        moderate_below=70.0,
        strong_below=85.0,
    )

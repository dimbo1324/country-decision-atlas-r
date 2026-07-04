from app.services.methodology_config import ScoreLabelThresholds
from typing import Literal


ScoreLabel = Literal["weak", "limited", "moderate", "strong", "excellent"]


def score_label(score: float, thresholds: ScoreLabelThresholds) -> ScoreLabel:
    if score < thresholds.weak_below:
        return "weak"
    if score < thresholds.limited_below:
        return "limited"
    if score < thresholds.moderate_below:
        return "moderate"
    if score < thresholds.strong_below:
        return "strong"
    return "excellent"


def optional_score_label(
    score: float | None,
    thresholds: ScoreLabelThresholds,
) -> ScoreLabel | Literal["missing"]:
    if score is None:
        return "missing"
    return score_label(score, thresholds)

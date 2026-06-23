from typing import Literal


ScoreLabel = Literal["weak", "limited", "moderate", "strong", "excellent"]


def score_label(score: float) -> ScoreLabel:
    if score < 30:
        return "weak"
    if score < 50:
        return "limited"
    if score < 70:
        return "moderate"
    if score < 85:
        return "strong"
    return "excellent"


def optional_score_label(score: float | None) -> ScoreLabel | Literal["missing"]:
    if score is None:
        return "missing"
    return score_label(score)

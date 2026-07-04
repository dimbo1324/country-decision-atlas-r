from app.schemas.community import ConsensusSummary, VoteSummary
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


SOURCE_BACKED_BONUS = 5.0
FRESHNESS_BONUS = 1.0
FRESHNESS_WINDOW_DAYS = 30
CONTROVERSIAL_SCORE_GAP = 2.0
CONTROVERSIAL_HELPFUL_THRESHOLD = 3
CONTROVERSIAL_OUTDATED_THRESHOLD = 3


@dataclass(frozen=True)
class AnswerVoteInput:
    answer_id: str
    up_votes: int
    down_votes: int
    helpful_votes: int
    outdated_votes: int
    source_backed: bool
    created_at: datetime | None


def score_answer(item: AnswerVoteInput) -> float:
    score = (
        item.up_votes * 2.0
        + item.helpful_votes * 3.0
        - item.down_votes * 2.0
        - item.outdated_votes * 3.0
    )
    if item.source_backed:
        score += SOURCE_BACKED_BONUS
    if _is_recent(item.created_at):
        score += FRESHNESS_BONUS
    return score


def _is_recent(created_at: datetime | None) -> bool:
    if created_at is None:
        return False
    reference = created_at
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=UTC)
    return datetime.now(UTC) - reference <= timedelta(
        days=FRESHNESS_WINDOW_DAYS
    )


def _own_controversial(item: AnswerVoteInput) -> bool:
    return (
        item.helpful_votes >= CONTROVERSIAL_HELPFUL_THRESHOLD
        and item.outdated_votes >= CONTROVERSIAL_OUTDATED_THRESHOLD
    )


def build_consensus_summaries(
    items: list[AnswerVoteInput],
) -> list[ConsensusSummary]:
    scored = [(item, score_answer(item)) for item in items]
    ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
    top_two_ids: set[str] = {pair[0].answer_id for pair in ranked[:2]}
    spread_controversial = False
    if len(ranked) >= 2:
        spread_controversial = (
            ranked[0][1] - ranked[1][1]
        ) <= CONTROVERSIAL_SCORE_GAP
    summaries: list[ConsensusSummary] = []
    for item, score in scored:
        controversial = _own_controversial(item) or (
            spread_controversial and item.answer_id in top_two_ids
        )
        summaries.append(
            ConsensusSummary(
                answer_id=item.answer_id,
                score=score,
                source_backed=item.source_backed,
                controversial=controversial,
                votes=VoteSummary(
                    up_votes=item.up_votes,
                    down_votes=item.down_votes,
                    helpful_votes=item.helpful_votes,
                    outdated_votes=item.outdated_votes,
                ),
            )
        )
    return summaries


def build_single_consensus_summary(item: AnswerVoteInput) -> ConsensusSummary:
    return build_consensus_summaries([item])[0]

from app.services.consensus import (
    AnswerVoteInput,
    build_consensus_summaries,
    build_single_consensus_summary,
    score_answer,
)


def _item(
    answer_id: str = "a1",
    up: int = 0,
    down: int = 0,
    helpful: int = 0,
    outdated: int = 0,
    source_backed: bool = False,
) -> AnswerVoteInput:
    return AnswerVoteInput(
        answer_id=answer_id,
        up_votes=up,
        down_votes=down,
        helpful_votes=helpful,
        outdated_votes=outdated,
        source_backed=source_backed,
        created_at=None,
    )


def test_score_answer_applies_weighted_formula() -> None:
    item = _item(up=2, down=1, helpful=1)
    score = score_answer(item)

    assert score == (2 * 2 + 1 * 3 - 1 * 2)


def test_score_answer_adds_source_backed_bonus() -> None:
    unsourced = score_answer(_item(up=1))
    sourced = score_answer(_item(up=1, source_backed=True))

    assert sourced == unsourced + 5.0


def test_source_backed_answer_scores_higher_than_unsourced() -> None:
    unsourced = _item(answer_id="a1", up=3)
    sourced = _item(answer_id="a2", up=3, source_backed=True)

    summaries = {
        s.answer_id: s for s in build_consensus_summaries([unsourced, sourced])
    }

    assert summaries["a2"].score > summaries["a1"].score
    assert summaries["a2"].source_backed is True
    assert summaries["a1"].source_backed is False


def test_controversial_when_scores_are_close() -> None:
    best = _item(answer_id="best", up=5)
    second = _item(answer_id="second", up=4)

    summaries = {s.answer_id: s for s in build_consensus_summaries([best, second])}

    assert summaries["best"].controversial is True
    assert summaries["second"].controversial is True


def test_not_controversial_when_scores_are_far_apart() -> None:
    best = _item(answer_id="best", up=20)
    second = _item(answer_id="second", up=1)

    summaries = {s.answer_id: s for s in build_consensus_summaries([best, second])}

    assert summaries["best"].controversial is False
    assert summaries["second"].controversial is False


def test_controversial_when_helpful_and_outdated_both_high() -> None:
    item = _item(helpful=3, outdated=3)

    summary = build_single_consensus_summary(item)

    assert summary.controversial is True


def test_consensus_is_not_official_truth_field_name() -> None:
    summary = build_single_consensus_summary(_item())

    assert hasattr(summary, "score")
    assert not hasattr(summary, "official_answer")

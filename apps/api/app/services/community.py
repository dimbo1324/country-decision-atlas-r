from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import (
    community as repository,
    feature_flags as feature_repository,
)
from app.repositories.domain_events import insert_domain_event
from app.schemas.community import (
    CommunityAnswerCreate,
    CommunityQuestionCreate,
    CommunityVoteCreate,
    ConsensusSummary,
)
from app.schemas.feature_flags import FeatureAccessTier
from app.services import (
    consensus as consensus_service,
    feature_flags as feature_service,
)
from psycopg import Connection
from typing import Any


def ensure_feature_enabled(
    connection: Connection[Any], settings: Settings, feature_key: str
) -> None:
    context = feature_service.default_access_context(settings, FeatureAccessTier.public)
    feature = feature_repository.get_feature_flag(connection, feature_key)
    rules = feature_repository.list_feature_access_rules(connection, feature_key)
    decision = feature_service.can_access(context, feature, rules, feature_key)
    if not decision.is_enabled:
        raise api_error(
            403,
            "feature_disabled",
            "This community feature is disabled.",
            {"feature_key": feature_key, "reason": decision.reason},
        )


def submit_question(
    connection: Connection[Any],
    settings: Settings,
    payload: CommunityQuestionCreate,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, settings, "community_enabled")
    ensure_feature_enabled(connection, settings, "community_qna_enabled")
    row = repository.insert_question(
        connection,
        country_slug=payload.country_slug,
        route_id=payload.route_id,
        legal_signal_id=payload.legal_signal_id,
        topic=payload.topic,
        title=payload.title,
        body=payload.body,
        created_by_identity_type=payload.created_by_identity_type,
        created_by_identity_id=payload.created_by_identity_id,
    )
    insert_domain_event(
        connection,
        event_key=f"qna_question:{row['id']}:community_question.submitted",
        event_type="community_question.submitted",
        aggregate_type="qna_question",
        aggregate_id=row["id"],
        country_slug=row.get("country_slug"),
        payload={"topic": row["topic"], "status": row["status"]},
        status="pending",
        notifiable=False,
    )
    return row


def list_public_questions(
    connection: Connection[Any],
    *,
    country_slug: str | None,
    topic: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    return repository.list_published_questions(
        connection, country_slug=country_slug, topic=topic, limit=limit
    )


def get_public_question(
    connection: Connection[Any], question_id: str
) -> dict[str, Any]:
    row = repository.get_question(connection, question_id, public_only=True)
    if row is None:
        raise api_error(404, "question_not_found", f"Question not found: {question_id}")
    return row


def list_public_answers(
    connection: Connection[Any], question_id: str
) -> list[dict[str, Any]]:
    get_public_question(connection, question_id)
    return repository.list_published_answers(connection, question_id)


def submit_answer(
    connection: Connection[Any],
    settings: Settings,
    question_id: str,
    payload: CommunityAnswerCreate,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, settings, "community_enabled")
    ensure_feature_enabled(connection, settings, "community_qna_enabled")
    question = repository.get_question(connection, question_id, public_only=False)
    if question is None:
        raise api_error(404, "question_not_found", f"Question not found: {question_id}")
    row = repository.insert_answer(
        connection,
        question_id=question_id,
        body=payload.body,
        source_ids=list(payload.source_ids),
        evidence_item_ids=list(payload.evidence_item_ids),
        created_by_identity_type=payload.created_by_identity_type,
        created_by_identity_id=payload.created_by_identity_id,
    )
    insert_domain_event(
        connection,
        event_key=f"qna_answer:{row['id']}:community_answer.submitted",
        event_type="community_answer.submitted",
        aggregate_type="qna_answer",
        aggregate_id=row["id"],
        country_slug=question.get("country_slug"),
        payload={"question_id": str(question_id), "status": row["status"]},
        status="pending",
        notifiable=False,
    )
    return row


def submit_vote(
    connection: Connection[Any],
    settings: Settings,
    answer_id: str,
    payload: CommunityVoteCreate,
) -> ConsensusSummary:
    ensure_feature_enabled(connection, settings, "community_enabled")
    ensure_feature_enabled(connection, settings, "community_qna_enabled")
    answer = repository.get_answer(connection, answer_id, public_only=True)
    if answer is None:
        raise api_error(404, "answer_not_found", f"Answer not found: {answer_id}")
    repository.insert_vote(
        connection,
        answer_id=answer_id,
        vote_type=payload.vote_type,
        identity_type=payload.identity_type,
        identity_id=payload.identity_id,
    )
    return get_answer_consensus(connection, answer)


def get_answer_consensus(
    connection: Connection[Any], answer: dict[str, Any]
) -> ConsensusSummary:
    votes = repository.get_vote_summary(connection, str(answer["id"]))
    source_backed = bool(answer.get("source_ids")) or bool(
        answer.get("evidence_item_ids")
    )
    item = consensus_service.AnswerVoteInput(
        answer_id=str(answer["id"]),
        up_votes=int(votes["up_votes"]),
        down_votes=int(votes["down_votes"]),
        helpful_votes=int(votes["helpful_votes"]),
        outdated_votes=int(votes["outdated_votes"]),
        source_backed=source_backed,
        created_at=answer.get("created_at"),
    )
    return consensus_service.build_single_consensus_summary(item)


def list_questions_for_admin(
    connection: Connection[Any], *, status: str | None, limit: int
) -> list[dict[str, Any]]:
    return repository.list_questions_for_admin(connection, status=status, limit=limit)


def update_question_status(
    connection: Connection[Any],
    question_id: str,
    status: str,
    moderated_by: str | None,
) -> dict[str, Any]:
    row = repository.update_question_status(
        connection, question_id, status, moderated_by=moderated_by
    )
    if row is None:
        raise api_error(404, "question_not_found", f"Question not found: {question_id}")
    return row


def list_answers_for_admin(
    connection: Connection[Any], *, status: str | None, limit: int
) -> list[dict[str, Any]]:
    return repository.list_answers_for_admin(connection, status=status, limit=limit)


def update_answer_status(
    connection: Connection[Any],
    answer_id: str,
    status: str,
    moderated_by: str | None,
) -> dict[str, Any]:
    row = repository.update_answer_status(
        connection, answer_id, status, moderated_by=moderated_by
    )
    if row is None:
        raise api_error(404, "answer_not_found", f"Answer not found: {answer_id}")
    return row

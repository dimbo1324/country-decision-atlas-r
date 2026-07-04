from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


QUESTION_FIELDS = """
    id,
    country_slug,
    route_id,
    legal_signal_id,
    topic,
    title,
    body,
    status,
    created_by_identity_type,
    created_by_identity_id,
    created_at,
    updated_at,
    moderated_at,
    moderated_by
"""

ANSWER_FIELDS = """
    id,
    question_id,
    body,
    status,
    source_ids,
    evidence_item_ids,
    created_by_identity_type,
    created_by_identity_id,
    created_at,
    updated_at,
    moderated_at,
    moderated_by
"""


def insert_question(
    conn: Connection[Any],
    *,
    country_slug: str | None,
    route_id: str | None,
    legal_signal_id: str | None,
    topic: str,
    title: str,
    body: str,
    created_by_identity_type: str,
    created_by_identity_id: str,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO qna_questions (
            country_slug,
            route_id,
            legal_signal_id,
            topic,
            title,
            body,
            created_by_identity_type,
            created_by_identity_id
        )
        VALUES (%s, %s::uuid, %s::uuid, %s, %s, %s, %s, %s)
        RETURNING {QUESTION_FIELDS}
        """,
        (
            country_slug,
            route_id,
            legal_signal_id,
            topic,
            title,
            body,
            created_by_identity_type,
            created_by_identity_id,
        ),
    )
    if row is None:
        raise RuntimeError("Expected qna_questions insert to return a row.")
    return row


def list_published_questions(
    conn: Connection[Any],
    *,
    country_slug: str | None = None,
    topic: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {QUESTION_FIELDS}
        FROM qna_questions
        WHERE status = 'published'
          AND (%s::text IS NULL OR country_slug = %s)
          AND (%s::text IS NULL OR topic = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (country_slug, country_slug, topic, topic, limit),
    )


def list_questions_for_admin(
    conn: Connection[Any],
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {QUESTION_FIELDS}
        FROM qna_questions
        WHERE (%s::text IS NULL OR status = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, limit),
    )


def get_question(
    conn: Connection[Any], question_id: str, public_only: bool = True
) -> dict[str, Any] | None:
    if public_only:
        return fetch_one(
            conn,
            f"""
            SELECT {QUESTION_FIELDS}
            FROM qna_questions
            WHERE id = %s::uuid AND status = 'published'
            """,
            (question_id,),
        )
    return fetch_one(
        conn,
        f"""
        SELECT {QUESTION_FIELDS}
        FROM qna_questions
        WHERE id = %s::uuid
        """,
        (question_id,),
    )


def update_question_status(
    conn: Connection[Any],
    question_id: str,
    status: str,
    moderated_by: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE qna_questions
        SET
            status = %s,
            moderated_by = COALESCE(%s, moderated_by),
            moderated_at = NOW(),
            updated_at = NOW()
        WHERE id = %s::uuid
        RETURNING {QUESTION_FIELDS}
        """,
        (status, moderated_by, question_id),
    )


def insert_answer(
    conn: Connection[Any],
    *,
    question_id: str,
    body: str,
    source_ids: list[Any],
    evidence_item_ids: list[Any],
    created_by_identity_type: str,
    created_by_identity_id: str,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO qna_answers (
            question_id,
            body,
            source_ids,
            evidence_item_ids,
            created_by_identity_type,
            created_by_identity_id
        )
        VALUES (%s::uuid, %s, %s, %s, %s, %s)
        RETURNING {ANSWER_FIELDS}
        """,
        (
            question_id,
            body,
            Jsonb(list(source_ids)),
            Jsonb(list(evidence_item_ids)),
            created_by_identity_type,
            created_by_identity_id,
        ),
    )
    if row is None:
        raise RuntimeError("Expected qna_answers insert to return a row.")
    return row


def list_published_answers(
    conn: Connection[Any], question_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {ANSWER_FIELDS}
        FROM qna_answers
        WHERE question_id = %s::uuid AND status = 'published'
        ORDER BY created_at ASC
        """,
        (question_id,),
    )


def list_answers_for_admin(
    conn: Connection[Any],
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {ANSWER_FIELDS}
        FROM qna_answers
        WHERE (%s::text IS NULL OR status = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, limit),
    )


def get_answer(
    conn: Connection[Any], answer_id: str, public_only: bool = True
) -> dict[str, Any] | None:
    if public_only:
        return fetch_one(
            conn,
            f"""
            SELECT {ANSWER_FIELDS}
            FROM qna_answers
            WHERE id = %s::uuid AND status = 'published'
            """,
            (answer_id,),
        )
    return fetch_one(
        conn,
        f"""
        SELECT {ANSWER_FIELDS}
        FROM qna_answers
        WHERE id = %s::uuid
        """,
        (answer_id,),
    )


def update_answer_status(
    conn: Connection[Any],
    answer_id: str,
    status: str,
    moderated_by: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE qna_answers
        SET
            status = %s,
            moderated_by = COALESCE(%s, moderated_by),
            moderated_at = NOW(),
            updated_at = NOW()
        WHERE id = %s::uuid
        RETURNING {ANSWER_FIELDS}
        """,
        (status, moderated_by, answer_id),
    )


def insert_vote(
    conn: Connection[Any],
    *,
    answer_id: str,
    vote_type: str,
    identity_type: str,
    identity_id: str,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        INSERT INTO qna_votes (
            answer_id,
            vote_type,
            identity_type,
            identity_id
        )
        VALUES (%s::uuid, %s, %s, %s)
        ON CONFLICT (answer_id, vote_type, identity_type, identity_id) DO NOTHING
        RETURNING id, answer_id, vote_type, identity_type, identity_id, created_at
        """,
        (answer_id, vote_type, identity_type, identity_id),
    )


def get_vote_summary(conn: Connection[Any], answer_id: str) -> dict[str, Any]:
    row = fetch_one(
        conn,
        """
        SELECT
            COUNT(*) FILTER (WHERE vote_type = 'up') AS up_votes,
            COUNT(*) FILTER (WHERE vote_type = 'down') AS down_votes,
            COUNT(*) FILTER (WHERE vote_type = 'helpful') AS helpful_votes,
            COUNT(*) FILTER (WHERE vote_type = 'outdated') AS outdated_votes
        FROM qna_votes
        WHERE answer_id = %s::uuid
        """,
        (answer_id,),
    )
    if row is None:
        return {
            "up_votes": 0,
            "down_votes": 0,
            "helpful_votes": 0,
            "outdated_votes": 0,
        }
    return row

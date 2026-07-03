from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


USER_STORY_RATING_FIELDS = """
    id,
    user_story_id,
    country_slug,
    route_id,
    official_expectation_score,
    real_experience_score,
    bureaucracy_score,
    cost_surprise_score,
    banking_difficulty_score,
    safety_feeling_score,
    comment,
    status,
    created_by_identity_type,
    created_by_identity_id,
    created_at,
    reviewed_at,
    reviewed_by
"""


def insert_user_story_rating(
    conn: Connection[Any],
    *,
    user_story_id: str | None,
    country_slug: str | None,
    route_id: str | None,
    official_expectation_score: int | None,
    real_experience_score: int | None,
    bureaucracy_score: int | None,
    cost_surprise_score: int | None,
    banking_difficulty_score: int | None,
    safety_feeling_score: int | None,
    comment: str | None,
    created_by_identity_type: str | None,
    created_by_identity_id: str | None,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO user_story_ratings (
            user_story_id,
            country_slug,
            route_id,
            official_expectation_score,
            real_experience_score,
            bureaucracy_score,
            cost_surprise_score,
            banking_difficulty_score,
            safety_feeling_score,
            comment,
            created_by_identity_type,
            created_by_identity_id
        )
        VALUES (
            %s::uuid, %s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING {USER_STORY_RATING_FIELDS}
        """,
        (
            user_story_id,
            country_slug,
            route_id,
            official_expectation_score,
            real_experience_score,
            bureaucracy_score,
            cost_surprise_score,
            banking_difficulty_score,
            safety_feeling_score,
            comment,
            created_by_identity_type,
            created_by_identity_id,
        ),
    )
    if row is None:
        raise RuntimeError("Expected user_story_ratings insert to return a row.")
    return row


def get_user_story_rating(
    conn: Connection[Any], rating_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        SELECT {USER_STORY_RATING_FIELDS}
        FROM user_story_ratings
        WHERE id = %s::uuid
        """,
        (rating_id,),
    )


def list_user_story_ratings(
    conn: Connection[Any],
    *,
    public_only: bool = True,
    country_slug: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if public_only:
        return fetch_all(
            conn,
            f"""
            SELECT {USER_STORY_RATING_FIELDS}
            FROM user_story_ratings
            WHERE status = 'published'
              AND (%s::text IS NULL OR country_slug = %s)
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (country_slug, country_slug, limit),
        )
    return fetch_all(
        conn,
        f"""
        SELECT {USER_STORY_RATING_FIELDS}
        FROM user_story_ratings
        WHERE (%s::text IS NULL OR status = %s)
          AND (%s::text IS NULL OR country_slug = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, country_slug, country_slug, limit),
    )


def update_user_story_rating_status(
    conn: Connection[Any],
    rating_id: str,
    status: str,
    reviewed_by: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE user_story_ratings
        SET
            status = %s,
            reviewed_by = COALESCE(%s, reviewed_by),
            reviewed_at = NOW()
        WHERE id = %s::uuid
        RETURNING {USER_STORY_RATING_FIELDS}
        """,
        (status, reviewed_by, rating_id),
    )


def count_user_story_ratings(conn: Connection[Any], status: str | None = None) -> int:
    row = fetch_one(
        conn,
        """
        SELECT COUNT(*) AS total
        FROM user_story_ratings
        WHERE (%s::text IS NULL OR status = %s)
        """,
        (status, status),
    )
    return int(row["total"]) if row else 0

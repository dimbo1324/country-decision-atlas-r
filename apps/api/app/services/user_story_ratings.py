from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import user_story_ratings as repository
from app.schemas.user_story_ratings import UserStoryRatingCreate
from app.services.community import ensure_feature_enabled
from psycopg import Connection
from typing import Any


def submit_user_story_rating(
    connection: Connection[Any],
    settings: Settings,
    payload: UserStoryRatingCreate,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, settings, "community_enabled")
    ensure_feature_enabled(connection, settings, "community_story_ratings_enabled")
    return repository.insert_user_story_rating(
        connection,
        user_story_id=payload.user_story_id,
        country_slug=payload.country_slug,
        route_id=payload.route_id,
        official_expectation_score=payload.official_expectation_score,
        real_experience_score=payload.real_experience_score,
        bureaucracy_score=payload.bureaucracy_score,
        cost_surprise_score=payload.cost_surprise_score,
        banking_difficulty_score=payload.banking_difficulty_score,
        safety_feeling_score=payload.safety_feeling_score,
        comment=payload.comment,
        created_by_identity_type=payload.created_by_identity_type,
        created_by_identity_id=payload.created_by_identity_id,
    )


def list_user_story_ratings_for_admin(
    connection: Connection[Any], *, status: str | None, limit: int
) -> list[dict[str, Any]]:
    return repository.list_user_story_ratings(
        connection, public_only=False, status=status, limit=limit
    )


def update_user_story_rating_status(
    connection: Connection[Any],
    rating_id: str,
    status: str,
    reviewed_by: str | None,
) -> dict[str, Any]:
    row = repository.update_user_story_rating_status(
        connection, rating_id, status, reviewed_by=reviewed_by
    )
    if row is None:
        raise api_error(
            404, "user_story_rating_not_found", f"Rating not found: {rating_id}"
        )
    return row

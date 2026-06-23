from app.core.database import get_connection
from app.schemas.decision_engine import (
    UserStoryCreate,
    UserStoryListResponse,
    UserStoryResponse,
)
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any, Literal


router = APIRouter(prefix="/user-stories", tags=["user_stories"])


@router.get("", response_model=UserStoryListResponse)
def read_user_stories(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    origin_country_slug: str | None = None,
    destination_country_slug: str | None = None,
    scenario: str | None = None,
    verification_status: str | None = None,
    is_synthetic: bool | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal["created_at", "year", "satisfaction_score"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserStoryListResponse:
    return decision_engine.list_user_stories(
        connection,
        limit,
        offset,
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
        sort,
        order,
    )


@router.get("/{story_id}", response_model=UserStoryResponse)
def read_user_story(
    story_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> UserStoryResponse:
    return decision_engine.get_user_story(connection, story_id)


@router.post("", response_model=UserStoryResponse, status_code=201)
def create_user_story(
    payload: UserStoryCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> UserStoryResponse:
    return decision_engine.create_user_story(connection, payload)

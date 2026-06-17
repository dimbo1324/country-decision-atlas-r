from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.core.database import get_connection
from app.schemas.decision_engine import UserStoryCreate, UserStoryListResponse, UserStoryResponse
from app.services import decision_engine

router = APIRouter(prefix="/user-stories", tags=["user_stories"])


@router.get("", response_model=UserStoryListResponse)
async def read_user_stories(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserStoryListResponse:
    return decision_engine.list_user_stories(connection, limit, offset)


@router.get("/{story_id}", response_model=UserStoryResponse)
async def read_user_story(
    story_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> UserStoryResponse:
    return decision_engine.get_user_story(connection, story_id)


@router.post("", response_model=UserStoryResponse, status_code=201)
async def create_user_story(
    payload: UserStoryCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> UserStoryResponse:
    return decision_engine.create_user_story(connection, payload)

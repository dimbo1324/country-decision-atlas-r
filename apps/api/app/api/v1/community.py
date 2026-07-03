from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.schemas.community import (
    CommunityAnswer,
    CommunityAnswerCreate,
    CommunityQuestion,
    CommunityQuestionCreate,
    CommunityQuestionListResponse,
    CommunityVoteCreate,
    ConsensusSummary,
)
from app.schemas.data_error_reports import DataErrorReport, DataErrorReportCreate
from app.schemas.user_story_ratings import UserStoryRating, UserStoryRatingCreate
from app.services import (
    community as community_service,
    data_error_reports as data_error_reports_service,
    user_story_ratings as user_story_ratings_service,
)
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/community", tags=["community"])


@router.get("/questions", response_model=CommunityQuestionListResponse)
def list_questions(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    country_slug: str | None = Query(None),
    topic: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> CommunityQuestionListResponse:
    items = community_service.list_public_questions(
        connection, country_slug=country_slug, topic=topic, limit=limit
    )
    return CommunityQuestionListResponse(items=items, total=len(items))


@router.get(
    "/questions/{question_id}",
    response_model=CommunityQuestion,
    responses={404: {"description": "Not found"}},
)
def get_question(
    question_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> dict[str, Any]:
    return community_service.get_public_question(connection, question_id)


@router.post("/questions", response_model=CommunityQuestion, status_code=201)
def create_question(
    payload: CommunityQuestionCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    row = community_service.submit_question(connection, settings, payload)
    connection.commit()
    return row


@router.get(
    "/questions/{question_id}/answers",
    response_model=list[CommunityAnswer],
)
def list_answers(
    question_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> list[dict[str, Any]]:
    return community_service.list_public_answers(connection, question_id)


@router.post(
    "/questions/{question_id}/answers",
    response_model=CommunityAnswer,
    status_code=201,
    responses={404: {"description": "Not found"}},
)
def create_answer(
    question_id: str,
    payload: CommunityAnswerCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    row = community_service.submit_answer(connection, settings, question_id, payload)
    connection.commit()
    return row


@router.post(
    "/answers/{answer_id}/votes",
    response_model=ConsensusSummary,
    responses={404: {"description": "Not found"}},
)
def create_vote(
    answer_id: str,
    payload: CommunityVoteCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConsensusSummary:
    result = community_service.submit_vote(connection, settings, answer_id, payload)
    connection.commit()
    return result


@router.post("/data-error-reports", response_model=DataErrorReport, status_code=201)
def create_data_error_report(
    payload: DataErrorReportCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    row = data_error_reports_service.submit_data_error_report(
        connection, settings, payload
    )
    connection.commit()
    return row


@router.post("/user-story-ratings", response_model=UserStoryRating, status_code=201)
def create_user_story_rating(
    payload: UserStoryRatingCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    row = user_story_ratings_service.submit_user_story_rating(
        connection, settings, payload
    )
    connection.commit()
    return row

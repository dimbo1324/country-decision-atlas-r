from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import (
    ADMIN,
    EDITOR,
    OWNER,
    require_capability,
    require_capability_or_roles,
)
from app.schemas.common import ErrorResponse
from app.schemas.community import (
    CommunityAnswer,
    CommunityQuestion,
    CommunityStatusUpdateRequest,
)
from app.schemas.data_error_reports import (
    DataErrorReport,
    DataErrorReportStatusUpdateRequest,
)
from app.schemas.user_story_ratings import (
    UserStoryRating,
    UserStoryRatingStatusUpdateRequest,
)
from app.services import (
    community as community_service,
    data_error_reports as data_error_reports_service,
    user_story_ratings as user_story_ratings_service,
)
from app.services.capabilities import MODERATOR_COMMUNITY
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin/community", tags=["admin-community"])

_RESPONSES: dict[int | str, dict[str, Any]] = {401: {"model": ErrorResponse}}

require_moderator = require_capability(MODERATOR_COMMUNITY)
require_moderator_or_editor = require_capability_or_roles(
    MODERATOR_COMMUNITY, EDITOR, ADMIN, OWNER
)


@router.get(
    "/questions", response_model=list[CommunityQuestion], responses=_RESPONSES
)
def list_questions_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    return community_service.list_questions_for_admin(
        connection, status=status, limit=limit
    )


@router.patch(
    "/questions/{question_id}/status",
    response_model=CommunityQuestion,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_question_status(
    question_id: str,
    payload: CommunityStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    row = community_service.update_question_status(
        connection, question_id, payload.status, payload.moderated_by
    )
    connection.commit()
    return row


@router.get(
    "/answers", response_model=list[CommunityAnswer], responses=_RESPONSES
)
def list_answers_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    return community_service.list_answers_for_admin(
        connection, status=status, limit=limit
    )


@router.patch(
    "/answers/{answer_id}/status",
    response_model=CommunityAnswer,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_answer_status(
    answer_id: str,
    payload: CommunityStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    row = community_service.update_answer_status(
        connection, answer_id, payload.status, payload.moderated_by
    )
    connection.commit()
    return row


@router.get(
    "/data-error-reports",
    response_model=list[DataErrorReport],
    responses=_RESPONSES,
)
def list_data_error_reports_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator_or_editor)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    return data_error_reports_service.list_data_error_reports_for_admin(
        connection, status=status, limit=limit
    )


@router.patch(
    "/data-error-reports/{report_id}/status",
    response_model=DataErrorReport,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_data_error_report_status(
    report_id: str,
    payload: DataErrorReportStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator_or_editor)],
) -> dict[str, Any]:
    row = data_error_reports_service.update_data_error_report_status(
        connection,
        report_id,
        payload.status,
        payload.reviewed_by,
        payload.resolution_note,
    )
    connection.commit()
    return row


@router.get(
    "/user-story-ratings",
    response_model=list[UserStoryRating],
    responses=_RESPONSES,
)
def list_user_story_ratings_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    return user_story_ratings_service.list_user_story_ratings_for_admin(
        connection, status=status, limit=limit
    )


@router.patch(
    "/user-story-ratings/{rating_id}/status",
    response_model=UserStoryRating,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_user_story_rating_status(
    rating_id: str,
    payload: UserStoryRatingStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    row = user_story_ratings_service.update_user_story_rating_status(
        connection, rating_id, payload.status, payload.reviewed_by
    )
    connection.commit()
    return row

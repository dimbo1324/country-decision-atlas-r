from app.core.auth import CurrentUser, bearer_scheme
from app.core.database import get_connection
from app.core.rbac import require_user
from app.schemas.migration_board import (
    ArchiveMigrationBoardPostResponse,
    BlockedUserListResponse,
    BlockedUserResponse,
    BlockUserRequest,
    CompanionMatchesResponse,
    ContactRequestActionRequest,
    ContactRequestActionResponse,
    ContactRequestListResponse,
    ContactRequestResponse,
    CreateContactRequestRequest,
    CreateMigrationBoardPostRequest,
    CreateMigrationBoardReportRequest,
    MigrationBoardPostDetail,
    MigrationBoardPostListResponse,
    MigrationBoardReportResponse,
    MyMigrationBoardPost,
    MyMigrationBoardPostListResponse,
    SubmitMigrationBoardPostResponse,
    UpdateMigrationBoardPostRequest,
)
from app.services import auth as auth_service, migration_board as service
from fastapi import APIRouter, Depends, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["migration-board"])


def optional_current_user(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ],
) -> CurrentUser | None:
    if credentials is None or not credentials.credentials:
        return None
    result = auth_service.validate_session_token(
        connection, credentials.credentials
    )
    user = result["user"]
    return CurrentUser(
        id=user["id"],
        email=user["email"],
        display_name=user["display_name"],
        role=user["role"],
        status=user["status"],
    )


@router.get(
    "/migration-board/posts", response_model=MigrationBoardPostListResponse
)
def list_board_posts(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser | None, Depends(optional_current_user)],
    destination_country: str | None = Query(None),
    origin_country: str | None = Query(None),
    route_id: str | None = Query(None),
    scenario: str | None = Query(None),
    persona: str | None = Query(None),
    timeline_window: str | None = Query(None),
    migration_stage: str | None = Query(None),
    companion_goal: str | None = Query(None),
    household_type: str | None = Query(None),
    preferred_language: str | None = Query(None),
    tag: str | None = Query(None),
    visibility: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_public_posts(
        connection,
        current_user=current_user,
        filters={
            "destination_country_slug": destination_country,
            "origin_country_slug": origin_country,
            "route_id": route_id,
            "scenario_slug": scenario,
            "persona_slug": persona,
            "timeline_window": timeline_window,
            "migration_stage": migration_stage,
            "companion_goal": companion_goal,
            "household_type": household_type,
            "preferred_language": preferred_language,
            "tag": tag,
            "visibility": visibility,
        },
        limit=limit,
        offset=offset,
    )


@router.get(
    "/migration-board/posts/{post_id}", response_model=MigrationBoardPostDetail
)
def get_board_post(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser | None, Depends(optional_current_user)],
) -> dict[str, Any]:
    return service.get_public_post(
        connection, post_id=post_id, current_user=current_user
    )


@router.get(
    "/me/migration-board/posts",
    response_model=MyMigrationBoardPostListResponse,
)
def list_my_board_posts(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.list_my_posts(connection, current_user)


@router.post(
    "/me/migration-board/posts",
    response_model=MyMigrationBoardPost,
    status_code=status.HTTP_201_CREATED,
)
def create_my_board_post(
    payload: CreateMigrationBoardPostRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    post = service.create_user_post(
        connection, current_user=current_user, payload=payload
    )
    connection.commit()
    return post


@router.get(
    "/me/migration-board/posts/{post_id}",
    response_model=MyMigrationBoardPost,
)
def get_my_board_post(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.get_my_post(
        connection, current_user=current_user, post_id=post_id
    )


@router.patch(
    "/me/migration-board/posts/{post_id}",
    response_model=MyMigrationBoardPost,
)
def update_my_board_post(
    post_id: str,
    payload: UpdateMigrationBoardPostRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    post = service.update_user_post(
        connection, current_user=current_user, post_id=post_id, payload=payload
    )
    connection.commit()
    return post


@router.post(
    "/me/migration-board/posts/{post_id}/submit",
    response_model=SubmitMigrationBoardPostResponse,
)
def submit_my_board_post(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    post = service.submit_user_post(
        connection, current_user=current_user, post_id=post_id
    )
    connection.commit()
    return {"post": post}


@router.post(
    "/me/migration-board/posts/{post_id}/archive",
    response_model=ArchiveMigrationBoardPostResponse,
)
def archive_my_board_post(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    post = service.archive_user_post(
        connection, current_user=current_user, post_id=post_id
    )
    connection.commit()
    return {"post": post}


@router.get(
    "/me/migration-board/matches",
    response_model=CompanionMatchesResponse,
)
def list_my_board_matches(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    return service.list_companion_matches(
        connection, current_user=current_user, post_id=None, limit=limit
    )


@router.get(
    "/me/migration-board/posts/{post_id}/matches",
    response_model=CompanionMatchesResponse,
)
def list_post_board_matches(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    return service.list_companion_matches(
        connection, current_user=current_user, post_id=post_id, limit=limit
    )


@router.post(
    "/migration-board/posts/{post_id}/contact-requests",
    response_model=ContactRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_board_contact_request(
    post_id: str,
    payload: CreateContactRequestRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    request = service.create_contact_request(
        connection,
        current_user=current_user,
        post_id=post_id,
        message=payload.message,
    )
    connection.commit()
    return request


@router.get(
    "/me/migration-board/contact-requests/incoming",
    response_model=ContactRequestListResponse,
)
def list_incoming_contact_requests(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.list_incoming_requests(connection, current_user)


@router.get(
    "/me/migration-board/contact-requests/outgoing",
    response_model=ContactRequestListResponse,
)
def list_outgoing_contact_requests(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.list_outgoing_requests(connection, current_user)


@router.post(
    "/me/migration-board/contact-requests/{request_id}/accept",
    response_model=ContactRequestActionResponse,
)
def accept_contact_request(
    request_id: str,
    payload: ContactRequestActionRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    request = service.accept_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        response_note=payload.response_note,
    )
    connection.commit()
    return {"request": request}


@router.post(
    "/me/migration-board/contact-requests/{request_id}/decline",
    response_model=ContactRequestActionResponse,
)
def decline_contact_request(
    request_id: str,
    payload: ContactRequestActionRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    request = service.decline_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        response_note=payload.response_note,
    )
    connection.commit()
    return {"request": request}


@router.post(
    "/me/migration-board/contact-requests/{request_id}/cancel",
    response_model=ContactRequestActionResponse,
)
def cancel_contact_request(
    request_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    request = service.cancel_contact_request(
        connection, current_user=current_user, request_id=request_id
    )
    connection.commit()
    return {"request": request}


@router.post(
    "/migration-board/posts/{post_id}/report",
    response_model=MigrationBoardReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_board_post(
    post_id: str,
    payload: CreateMigrationBoardReportRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    report = service.report_post(
        connection,
        current_user=current_user,
        post_id=post_id,
        reason=payload.reason,
        details=payload.details,
    )
    connection.commit()
    return report


@router.post(
    "/me/migration-board/contact-requests/{request_id}/report",
    response_model=MigrationBoardReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_board_contact_request(
    request_id: str,
    payload: CreateMigrationBoardReportRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    report = service.report_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        reason=payload.reason,
        details=payload.details,
    )
    connection.commit()
    return report


@router.post(
    "/me/migration-board/blocks/{user_id}",
    response_model=BlockedUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def block_board_user(
    user_id: str,
    payload: BlockUserRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    row = service.block_user(
        connection,
        current_user=current_user,
        blocked_user_id=user_id,
        reason=payload.reason,
    )
    connection.commit()
    return row


@router.delete("/me/migration-board/blocks/{user_id}", status_code=204)
def unblock_board_user(
    user_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> None:
    service.unblock_user(
        connection, current_user=current_user, blocked_user_id=user_id
    )
    connection.commit()


@router.get(
    "/me/migration-board/blocks",
    response_model=BlockedUserListResponse,
)
def list_board_blocks(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_user)],
) -> dict[str, Any]:
    return service.list_blocked_users(connection, current_user)

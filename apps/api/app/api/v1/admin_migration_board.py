from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_moderator
from app.schemas.migration_board import (
    AdminMigrationBoardPost,
    AdminMigrationBoardPostListResponse,
    MigrationBoardReportListResponse,
    ModerateMigrationBoardPostRequest,
    ModerateMigrationBoardPostResponse,
    ReviewMigrationBoardReportRequest,
    ReviewMigrationBoardReportResponse,
)
from app.services import migration_board as service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin/migration-board", tags=["admin-migration-board"])


@router.get("/posts", response_model=AdminMigrationBoardPostListResponse)
def list_migration_board_posts_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_posts_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )


@router.get("/posts/{post_id}", response_model=AdminMigrationBoardPost)
def get_migration_board_post_for_admin(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    return service.get_post_for_moderation(connection, post_id)


@router.post(
    "/posts/{post_id}/approve",
    response_model=ModerateMigrationBoardPostResponse,
)
def approve_migration_board_post(
    post_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    post = service.approve_post(connection, current_user=current_user, post_id=post_id)
    connection.commit()
    return {"post": post}


@router.post(
    "/posts/{post_id}/reject",
    response_model=ModerateMigrationBoardPostResponse,
)
def reject_migration_board_post(
    post_id: str,
    payload: ModerateMigrationBoardPostRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    post = service.reject_post(
        connection,
        current_user=current_user,
        post_id=post_id,
        reason=payload.moderation_reason,
    )
    connection.commit()
    return {"post": post}


@router.post(
    "/posts/{post_id}/hide",
    response_model=ModerateMigrationBoardPostResponse,
)
def hide_migration_board_post(
    post_id: str,
    payload: ModerateMigrationBoardPostRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    post = service.hide_post(
        connection,
        current_user=current_user,
        post_id=post_id,
        reason=payload.moderation_reason,
    )
    connection.commit()
    return {"post": post}


@router.get("/reports", response_model=MigrationBoardReportListResponse)
def list_migration_board_reports_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_moderator)],
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_reports_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )


@router.post(
    "/reports/{report_id}/resolve",
    response_model=ReviewMigrationBoardReportResponse,
)
def resolve_migration_board_report(
    report_id: str,
    payload: ReviewMigrationBoardReportRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    report = service.resolve_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        resolution_note=payload.resolution_note,
        hide_related_post=payload.hide_post,
    )
    connection.commit()
    return {"report": report}


@router.post(
    "/reports/{report_id}/dismiss",
    response_model=ReviewMigrationBoardReportResponse,
)
def dismiss_migration_board_report(
    report_id: str,
    payload: ReviewMigrationBoardReportRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_moderator)],
) -> dict[str, Any]:
    report = service.dismiss_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        resolution_note=payload.resolution_note,
    )
    connection.commit()
    return {"report": report}

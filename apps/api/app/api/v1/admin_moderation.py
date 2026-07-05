from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_owner
from app.schemas.moderation_feed import ModerationActionListResponse
from app.services import moderation_feed as service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin/moderation", tags=["admin-moderation"])


@router.get("/actions", response_model=ModerationActionListResponse)
def list_moderation_actions(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_owner)],
    entity_type: str | None = Query(None),
    action: str | None = Query(None),
    changed_by: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ModerationActionListResponse:
    return ModerationActionListResponse(
        **service.list_moderation_actions(
            connection,
            entity_type=entity_type,
            action=action,
            changed_by=changed_by,
            limit=limit,
            offset=offset,
        )
    )

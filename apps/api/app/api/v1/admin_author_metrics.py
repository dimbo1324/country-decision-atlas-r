from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_capability
from app.schemas.author_metrics import (
    AdminAuthorMetricDefinition,
    AdminAuthorMetricListResponse,
    ModerateAuthorMetricRequest,
    ModerateAuthorMetricResponse,
)
from app.schemas.common import PublicationStatus
from app.services import author_metrics as service
from app.services.capabilities import MODERATOR_METRICS
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any
from uuid import UUID


router = APIRouter(
    prefix="/admin/author-metrics", tags=["admin-author-metrics"]
)


@router.get("", response_model=AdminAuthorMetricListResponse)
def list_author_metrics_for_admin(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_capability(MODERATOR_METRICS))],
    status: PublicationStatus | None = Query(None),  # noqa: B008
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_definitions_for_moderation(
        connection,
        status=status.value if status is not None else None,
        limit=limit,
        offset=offset,
    )


@router.get("/{definition_id}", response_model=AdminAuthorMetricDefinition)
def get_author_metric_for_admin(
    definition_id: UUID,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_capability(MODERATOR_METRICS))],
) -> dict[str, Any]:
    return service.get_definition_for_moderation(connection, str(definition_id))


@router.post(
    "/{definition_id}/approve", response_model=ModerateAuthorMetricResponse
)
def approve_author_metric(
    definition_id: UUID,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(MODERATOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.approve_definition(
        connection,
        current_user=current_user,
        definition_id=str(definition_id),
    )
    connection.commit()
    return {"definition": definition}


@router.post(
    "/{definition_id}/reject", response_model=ModerateAuthorMetricResponse
)
def reject_author_metric(
    definition_id: UUID,
    payload: ModerateAuthorMetricRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[
        CurrentUser, Depends(require_capability(MODERATOR_METRICS))
    ],
) -> dict[str, Any]:
    definition = service.reject_definition(
        connection,
        current_user=current_user,
        definition_id=str(definition_id),
        reason=payload.moderation_reason,
    )
    connection.commit()
    return {"definition": definition}

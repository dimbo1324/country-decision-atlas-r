from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_owner
from app.schemas.capabilities import (
    CapabilityGrant,
    CapabilityGrantCreate,
    CapabilityGrantListResponse,
    CapabilityGrantResponse,
)
from app.services import capabilities as service
from fastapi import APIRouter, Depends, Query, status
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin/capabilities", tags=["admin-capabilities"])


@router.get("", response_model=CapabilityGrantListResponse)
def list_capability_grants(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_owner)],
    user_id: str | None = Query(None),
    capability: str | None = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> CapabilityGrantListResponse:
    result = service.list_capabilities(
        connection,
        user_id=user_id,
        capability=capability,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
    return CapabilityGrantListResponse(
        items=[CapabilityGrant(**item) for item in result["items"]],
        total=result["total"],
    )


@router.post(
    "",
    response_model=CapabilityGrantResponse,
    status_code=status.HTTP_201_CREATED,
)
def grant_capability(
    payload: CapabilityGrantCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_owner)],
) -> CapabilityGrantResponse:
    row = service.grant_capability(
        connection,
        current_user=current_user,
        user_id=payload.user_id,
        capability=payload.capability,
        note=payload.note,
    )
    connection.commit()
    return CapabilityGrantResponse(item=CapabilityGrant(**row))


@router.delete("/{capability_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_capability(
    capability_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    current_user: Annotated[CurrentUser, Depends(require_owner)],
) -> None:
    service.revoke_capability(
        connection, current_user=current_user, capability_id=capability_id
    )
    connection.commit()

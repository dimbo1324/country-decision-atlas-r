from app.core.auth import CurrentUser
from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.core.rbac import require_editor
from app.schemas.ai_drafts import (
    AIDraft,
    AIDraftGenerateSummaryRequest,
    AIDraftListResponse,
    AIDraftStatusUpdateRequest,
)
from app.schemas.common import ErrorResponse
from app.schemas.contradiction_candidates import (
    ContradictionCandidate,
    ContradictionCandidateGenerateRequest,
    ContradictionCandidateListResponse,
    ContradictionCandidateStatusUpdateRequest,
)
from app.services import (
    ai_drafts as ai_drafts_service,
    contradiction_candidates as contradiction_service,
)
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/admin", tags=["admin-ai"])

_RESPONSES: dict[int | str, dict[str, Any]] = {401: {"model": ErrorResponse}}


@router.post(
    "/ai/drafts/generate-summary",
    response_model=AIDraft,
    responses=_RESPONSES,
)
def generate_summary_draft(
    payload: AIDraftGenerateSummaryRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    row = ai_drafts_service.generate_summary_draft(
        connection,
        settings,
        country_slug=payload.country_slug,
        route_id=payload.route_id,
        source_id=payload.source_id,
        evidence_item_id=payload.evidence_item_id,
        topic=payload.topic,
        locale=payload.locale,
    )
    connection.commit()
    return row


@router.post(
    "/ai/drafts/detect-contradiction",
    response_model=ContradictionCandidate,
    responses=_RESPONSES,
)
def detect_contradiction(
    payload: ContradictionCandidateGenerateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    row = contradiction_service.detect_contradiction_candidate(
        connection,
        settings,
        country_slug=payload.country_slug,
        topic=payload.topic,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        locale=payload.locale,
    )
    connection.commit()
    return row


@router.get(
    "/ai/drafts",
    response_model=AIDraftListResponse,
    responses=_RESPONSES,
)
def list_ai_drafts(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
    status: str | None = Query(None),
    draft_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> AIDraftListResponse:
    items, total = ai_drafts_service.list_ai_drafts_for_admin(
        connection, status=status, draft_type=draft_type, limit=limit
    )
    return AIDraftListResponse(items=items, total=total)


@router.get(
    "/ai/drafts/{draft_id}",
    response_model=AIDraft,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def get_ai_draft(
    draft_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    return ai_drafts_service.get_ai_draft_for_admin(connection, draft_id)


@router.patch(
    "/ai/drafts/{draft_id}/status",
    response_model=AIDraft,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_ai_draft_status(
    draft_id: str,
    payload: AIDraftStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    row = ai_drafts_service.update_ai_draft_status(
        connection, draft_id, payload.status, payload.reviewed_by
    )
    connection.commit()
    return row


@router.get(
    "/contradiction-candidates",
    response_model=ContradictionCandidateListResponse,
    responses=_RESPONSES,
)
def list_contradiction_candidates(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
    status: str | None = Query(None),
    severity: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> ContradictionCandidateListResponse:
    items, total = (
        contradiction_service.list_contradiction_candidates_for_admin(
            connection, status=status, severity=severity, limit=limit
        )
    )
    return ContradictionCandidateListResponse(items=items, total=total)


@router.get(
    "/contradiction-candidates/{candidate_id}",
    response_model=ContradictionCandidate,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def get_contradiction_candidate(
    candidate_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    return contradiction_service.get_contradiction_candidate_for_admin(
        connection, candidate_id
    )


@router.patch(
    "/contradiction-candidates/{candidate_id}/status",
    response_model=ContradictionCandidate,
    responses={**_RESPONSES, 404: {"description": "Not found"}},
)
def update_contradiction_candidate_status(
    candidate_id: str,
    payload: ContradictionCandidateStatusUpdateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_editor)],
) -> dict[str, Any]:
    row = contradiction_service.update_contradiction_candidate_status(
        connection, candidate_id, payload.status, payload.reviewed_by
    )
    connection.commit()
    return row

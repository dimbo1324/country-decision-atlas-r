from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_editor
from app.schemas.country_contribution import (
    CountryProposalListResponse,
    CountryProposalResponse,
    GenericItemResponse,
    ModerationReasonPayload,
    ScenarioScoresUpsert,
)
from app.services import country_contribution as service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any
from uuid import UUID


router = APIRouter(prefix="/admin", tags=["admin-country-contribution"])

_Editor = Annotated[CurrentUser, Depends(require_editor)]
_Conn = Annotated[Connection[Any], Depends(get_connection)]


@router.get("/country-proposals", response_model=CountryProposalListResponse)
def list_country_proposals_for_curation(
    connection: _Conn,
    _: _Editor,
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_proposals_for_curation(
        connection, status=status, limit=limit, offset=offset
    )


@router.get(
    "/country-proposals/{proposal_id}",
    response_model=CountryProposalResponse,
)
def get_country_proposal_for_curation(
    proposal_id: UUID,
    connection: _Conn,
    _: _Editor,
) -> dict[str, Any]:
    return {
        "item": service.get_proposal_for_curation(connection, str(proposal_id))
    }


@router.post(
    "/country-proposals/{proposal_id}/assign-curator",
    response_model=CountryProposalResponse,
)
def assign_country_proposal_curator(
    proposal_id: UUID,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    proposal = service.assign_curator(
        connection, current_user=current_user, proposal_id=str(proposal_id)
    )
    connection.commit()
    return {"item": proposal}


@router.post("/country-proposals/{proposal_id}/readiness-check")
def run_country_proposal_readiness_check(
    proposal_id: UUID,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    snapshot = service.run_readiness_check(
        connection, current_user=current_user, proposal_id=str(proposal_id)
    )
    connection.commit()
    return snapshot


@router.put(
    "/country-proposals/{proposal_id}/scenario-scores",
    response_model=GenericItemResponse,
)
def upsert_country_proposal_scenario_scores(
    proposal_id: UUID,
    payload: ScenarioScoresUpsert,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    result = service.upsert_scenario_scores(
        connection,
        current_user=current_user,
        proposal_id=str(proposal_id),
        scenario_slug=payload.scenario_slug,
        breakdowns=payload.breakdowns,
    )
    connection.commit()
    return {"item": result}


@router.post(
    "/country-proposals/{proposal_id}/publish",
    response_model=CountryProposalResponse,
)
def publish_country_proposal(
    proposal_id: UUID,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    proposal = service.publish_proposal(
        connection, current_user=current_user, proposal_id=str(proposal_id)
    )
    connection.commit()
    return {"item": proposal}


@router.post(
    "/country-proposals/{proposal_id}/reject",
    response_model=CountryProposalResponse,
)
def reject_country_proposal(
    proposal_id: UUID,
    payload: ModerationReasonPayload,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    proposal = service.reject_proposal(
        connection,
        current_user=current_user,
        proposal_id=str(proposal_id),
        reason=payload.reason,
    )
    connection.commit()
    return {"item": proposal}


@router.post(
    "/country-proposals/{proposal_id}/request-changes",
    response_model=CountryProposalResponse,
)
def request_country_proposal_changes(
    proposal_id: UUID,
    payload: ModerationReasonPayload,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    proposal = service.request_changes(
        connection,
        current_user=current_user,
        proposal_id=str(proposal_id),
        reason=payload.reason,
    )
    connection.commit()
    return {"item": proposal}


@router.post(
    "/country-proposals/{proposal_id}/archive",
    response_model=CountryProposalResponse,
)
def archive_country_proposal(
    proposal_id: UUID,
    connection: _Conn,
    current_user: _Editor,
) -> dict[str, Any]:
    proposal = service.archive_proposal(
        connection, current_user=current_user, proposal_id=str(proposal_id)
    )
    connection.commit()
    return {"item": proposal}

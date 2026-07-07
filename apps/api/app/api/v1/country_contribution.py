from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.rbac import require_capability
from app.schemas.country_contribution import (
    ContributorEvidenceItemCreate,
    ContributorEvidenceItemPatch,
    ContributorLegalSignalCreate,
    ContributorLegalSignalPatch,
    ContributorSourceCreate,
    ContributorSourcePatch,
    ContributorTimelineEventCreate,
    CountryCardUpsert,
    CountryMetricValuesUpsert,
    CountryProposalCreate,
    CountryProposalListResponse,
    CountryProposalPatch,
    CountryProposalResponse,
    GenericItemResponse,
    GenericListResponse,
)
from app.services import country_contribution as service
from app.services.capabilities import CONTRIBUTOR_COUNTRIES
from fastapi import APIRouter, Depends, Query, status
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["country-contribution"])

_Contributor = Annotated[
    CurrentUser, Depends(require_capability(CONTRIBUTOR_COUNTRIES))
]
_Conn = Annotated[Connection[Any], Depends(get_connection)]


@router.post(
    "/me/country-proposals",
    response_model=CountryProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_country_proposal(
    payload: CountryProposalCreate,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    proposal = service.create_proposal(
        connection, current_user=current_user, payload=payload
    )
    connection.commit()
    return {"item": proposal}


@router.get("/me/country-proposals", response_model=CountryProposalListResponse)
def list_my_country_proposals(
    connection: _Conn,
    current_user: _Contributor,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    return service.list_my_proposals(
        connection, current_user=current_user, limit=limit, offset=offset
    )


@router.get(
    "/me/country-proposals/{proposal_id}",
    response_model=CountryProposalResponse,
)
def get_my_country_proposal(
    proposal_id: str,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    return {
        "item": service.get_my_proposal(
            connection, current_user=current_user, proposal_id=proposal_id
        )
    }


@router.patch(
    "/me/country-proposals/{proposal_id}",
    response_model=CountryProposalResponse,
)
def patch_my_country_proposal(
    proposal_id: str,
    payload: CountryProposalPatch,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    proposal = service.patch_my_proposal(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": proposal}


@router.post(
    "/me/country-proposals/{proposal_id}/submit",
    response_model=CountryProposalResponse,
)
def submit_my_country_proposal(
    proposal_id: str,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    proposal = service.submit_my_proposal(
        connection, current_user=current_user, proposal_id=proposal_id
    )
    connection.commit()
    return {"item": proposal}


@router.put(
    "/me/country-proposals/{proposal_id}/card/{locale}",
    response_model=GenericItemResponse,
)
def upsert_my_country_proposal_card(
    proposal_id: str,
    locale: str,
    payload: CountryCardUpsert,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.upsert_my_card(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        locale=locale,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.post(
    "/me/country-proposals/{proposal_id}/sources",
    response_model=GenericItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_country_proposal_source(
    proposal_id: str,
    payload: ContributorSourceCreate,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.create_my_source(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.patch(
    "/me/country-proposals/{proposal_id}/sources/{source_id}",
    response_model=GenericItemResponse,
)
def patch_my_country_proposal_source(
    proposal_id: str,
    source_id: str,
    payload: ContributorSourcePatch,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.patch_my_source(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        source_id=source_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.post(
    "/me/country-proposals/{proposal_id}/evidence-items",
    response_model=GenericItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_country_proposal_evidence_item(
    proposal_id: str,
    payload: ContributorEvidenceItemCreate,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.create_my_evidence_item(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.patch(
    "/me/country-proposals/{proposal_id}/evidence-items/{evidence_item_id}",
    response_model=GenericItemResponse,
)
def patch_my_country_proposal_evidence_item(
    proposal_id: str,
    evidence_item_id: str,
    payload: ContributorEvidenceItemPatch,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.patch_my_evidence_item(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        evidence_item_id=evidence_item_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.post(
    "/me/country-proposals/{proposal_id}/legal-signals",
    response_model=GenericItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_country_proposal_legal_signal(
    proposal_id: str,
    payload: ContributorLegalSignalCreate,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.create_my_legal_signal(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.patch(
    "/me/country-proposals/{proposal_id}/legal-signals/{signal_id}",
    response_model=GenericItemResponse,
)
def patch_my_country_proposal_legal_signal(
    proposal_id: str,
    signal_id: str,
    payload: ContributorLegalSignalPatch,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.patch_my_legal_signal(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        signal_id=signal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.post(
    "/me/country-proposals/{proposal_id}/timeline-events",
    response_model=GenericItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_country_proposal_timeline_event(
    proposal_id: str,
    payload: ContributorTimelineEventCreate,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    item = service.create_my_timeline_event(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        payload=payload,
    )
    connection.commit()
    return {"item": item}


@router.put(
    "/me/country-proposals/{proposal_id}/metric-values",
    response_model=GenericListResponse,
)
def upsert_my_country_proposal_metric_values(
    proposal_id: str,
    payload: CountryMetricValuesUpsert,
    connection: _Conn,
    current_user: _Contributor,
) -> dict[str, Any]:
    result = service.upsert_my_metric_values(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        entries=payload.values,
    )
    connection.commit()
    return result

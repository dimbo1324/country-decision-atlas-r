from app.core.database import get_connection
from app.schemas.decision_passports import (
    DecisionPassportCreateRequest,
    DecisionPassportCreateResponse,
    DecisionPassportResponse,
)
from app.services import decision_passports as service
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/decision/passports", tags=["decision-passports"])


@router.post("", response_model=DecisionPassportCreateResponse)
def create_decision_passport(
    payload: DecisionPassportCreateRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionPassportCreateResponse:
    return service.create_decision_passport(
        connection,
        payload.decision_request,
        payload.locale,
        payload.expires_in_days,
    )


@router.get("/{token}", response_model=DecisionPassportResponse)
def read_decision_passport(
    token: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionPassportResponse:
    return service.get_decision_passport_by_token(connection, token)

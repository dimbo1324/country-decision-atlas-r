from app.core.database import get_connection
from app.schemas.decision_engine import (
    DecisionCompareInput,
    DecisionCompareResult,
    DecisionRunRequest,
    DecisionRunResponse,
)
from app.schemas.decision_wizard import (
    DecisionWizardAnswers,
    DecisionWizardRecommendation,
)
from app.services import decision_engine, decision_wizard
from fastapi import APIRouter, Depends, Header
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("/compare", response_model=DecisionCompareResult)
def compare_countries(
    payload: DecisionCompareInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionCompareResult:
    return decision_engine.compare_countries(connection, payload)


@router.post("/run", response_model=DecisionRunResponse)
def run_decision(
    payload: DecisionRunRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    x_cda_session: Annotated[str | None, Header(alias="X-CDA-Session")] = None,
) -> DecisionRunResponse:
    return decision_engine.run_decision(connection, payload, session_id=x_cda_session)


@router.post("/wizard/resolve", response_model=DecisionWizardRecommendation)
def resolve_wizard(
    payload: DecisionWizardAnswers,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    x_cda_session: Annotated[str | None, Header(alias="X-CDA-Session")] = None,
) -> DecisionWizardRecommendation:
    return decision_wizard.resolve_wizard_recommendation(
        connection, payload, session_id=x_cda_session
    )

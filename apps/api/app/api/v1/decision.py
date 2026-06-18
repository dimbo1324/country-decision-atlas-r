from app.core.database import get_connection
from app.schemas.decision_engine import (
    DecisionCompareInput,
    DecisionCompareResult,
    DecisionRunRequest,
    DecisionRunResponse,
)
from app.services import decision_engine
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("/compare", response_model=DecisionCompareResult)
async def compare_countries(
    payload: DecisionCompareInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionCompareResult:
    return decision_engine.compare_countries(connection, payload)


@router.post("/run", response_model=DecisionRunResponse)
async def run_decision(
    payload: DecisionRunRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionRunResponse:
    return decision_engine.run_decision(connection, payload)

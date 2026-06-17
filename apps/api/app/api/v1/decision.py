from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from app.core.database import get_connection
from app.schemas.decision_engine import (
    DecisionCompareInput,
    DecisionCompareResult,
    DecisionRunInput,
    DecisionRunResult,
)
from app.services import decision_engine

router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("/compare", response_model=DecisionCompareResult)
async def compare_countries(
    payload: DecisionCompareInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionCompareResult:
    return decision_engine.compare_countries(connection, payload)


@router.post("/run", response_model=DecisionRunResult)
async def run_decision(
    payload: DecisionRunInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> DecisionRunResult:
    return decision_engine.run_decision(connection, payload)

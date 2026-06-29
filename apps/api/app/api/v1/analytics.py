from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsEventCreateResponse
from app.services.analytics import record_analytics_event
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", response_model=AnalyticsEventCreateResponse)
def create_analytics_event(
    payload: AnalyticsEventCreate,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AnalyticsEventCreateResponse:
    return record_analytics_event(connection, payload, settings)

from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.home_overview import HomeOverviewResponse
from app.services.home_overview import build_home_overview
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/home", tags=["home"])


@router.get("/overview", response_model=HomeOverviewResponse)
def read_home_overview(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> HomeOverviewResponse:
    return build_home_overview(connection, locale)

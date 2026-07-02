from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.search import SearchResponse
from app.services.search import run_search
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: Annotated[str, Query(min_length=1, max_length=200)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    types: str | None = None,
    country_slug: str | None = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SearchResponse:
    return run_search(connection, q, locale, types, country_slug, limit, offset)

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.core.database import get_connection
from app.repositories.common import build_locale
from app.repositories.legal_signals import count_legal_signals, list_legal_signals
from app.schemas.common import LocaleCode, Pagination
from app.schemas.legal_signals import LegalSignalListResponse

router = APIRouter(prefix="/countries/{country_id}/legal-signals", tags=["legal_signals"])


@router.get("", response_model=LegalSignalListResponse)
async def read_country_legal_signals(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleCode = "en",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LegalSignalListResponse:
    rows = list_legal_signals(connection, country_id, limit, offset)
    total = count_legal_signals(connection, country_id)
    return LegalSignalListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=build_locale([], locale),
    )

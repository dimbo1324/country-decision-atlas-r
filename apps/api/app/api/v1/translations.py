from typing import Annotated, Any
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from app.core.database import get_connection
from app.repositories.translations import count_translations, list_translations
from app.schemas.common import Pagination
from app.schemas.translations import TranslationListResponse
router = APIRouter(prefix="/translations", tags=["translations"])
@router.get("", response_model=TranslationListResponse)
async def read_translations(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TranslationListResponse:
    rows = list_translations(connection, limit, offset)
    total = count_translations(connection)
    return TranslationListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )

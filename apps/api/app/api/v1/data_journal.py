from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.data_journal import CountryDataJournalResponse
from app.services.data_journal import build_country_data_journal
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/countries", tags=["data_journal"])


@router.get(
    "/{country_slug}/data-journal", response_model=CountryDataJournalResponse
)
def read_country_data_journal(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CountryDataJournalResponse:
    return build_country_data_journal(
        connection, country_slug, locale, limit, offset
    )

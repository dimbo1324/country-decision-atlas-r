from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.what_changed import WhatChangedResponse
from app.services.what_changed import build_what_changed
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/countries", tags=["what-changed"])


@router.get("/{country_slug}/what-changed", response_model=WhatChangedResponse)
def read_country_what_changed(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    since: datetime | None = None,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> WhatChangedResponse:
    return build_what_changed(connection, country_slug, locale, since, days, limit)

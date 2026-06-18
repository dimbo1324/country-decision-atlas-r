from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.common import build_locale
from app.repositories.countries import (
    count_countries,
    get_country,
    get_profile,
    list_countries,
)
from app.repositories.scores import count_country_scores, list_country_scores
from app.schemas.common import Pagination
from app.schemas.countries import (
    CountryListResponse,
    CountryProfileResponse,
    CountryResponse,
)
from app.schemas.country_read_model import CountryReadModelResponse
from app.schemas.decision_engine import SourceListWithLocaleResponse
from app.schemas.scores import CountryScoreListResponse
from app.services import decision_engine
from app.services.country_read_model import get_country_read_model
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=CountryListResponse)
async def read_countries(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CountryListResponse:
    rows = list_countries(connection, locale, limit, offset)
    total = count_countries(connection)
    return CountryListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=build_locale(rows, locale),
    )


@router.get("/{country_id}", response_model=CountryResponse)
async def read_country(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryResponse:
    row = get_country(connection, country_id, locale)
    if row is None:
        raise HTTPException(status_code=404, detail="Country not found.")
    return CountryResponse(item=row, locale=build_locale([row], locale))


@router.get("/{country_id}/profile", response_model=CountryProfileResponse)
async def read_country_profile(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryProfileResponse:
    row = get_profile(connection, country_id, locale)
    if row is None:
        raise HTTPException(status_code=404, detail="Country profile not found.")
    return CountryProfileResponse(item=row, locale=build_locale([row], locale))


@router.get("/{country_id}/scores", response_model=CountryScoreListResponse)
async def read_country_scores(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CountryScoreListResponse:
    rows = list_country_scores(connection, country_id, locale, limit, offset)
    total = count_country_scores(connection, country_id)
    return CountryScoreListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=build_locale(rows, locale),
    )


@router.get("/{country_slug}/card", response_model=CountryReadModelResponse)
async def read_country_card(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryReadModelResponse:
    result = get_country_read_model(connection, country_slug, locale)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "country_not_found",
                    "message": "Country not found.",
                    "details": {"country_slug": country_slug},
                }
            },
        )
    return result


@router.get("/{country_slug}/sources", response_model=SourceListWithLocaleResponse)
async def read_country_sources(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SourceListWithLocaleResponse:
    return decision_engine.get_country_sources(
        connection, country_slug, locale, limit, offset
    )

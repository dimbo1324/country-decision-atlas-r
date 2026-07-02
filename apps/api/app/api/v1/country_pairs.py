from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.country_pairs import (
    CountryPairCompatibilityListResponse,
    CountryPairCompatibilityResponse,
)
from app.services import country_pairs as country_pairs_service
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["country-pairs"])


@router.get(
    "/country-pairs/{origin_slug}/{destination_slug}",
    response_model=CountryPairCompatibilityResponse,
)
def read_country_pair(
    origin_slug: str,
    destination_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryPairCompatibilityResponse:
    return country_pairs_service.get_country_pair_context(
        connection, origin_slug, destination_slug, locale
    )


@router.get(
    "/countries/{origin_slug}/destination-compatibility",
    response_model=CountryPairCompatibilityListResponse,
)
def read_destination_compatibility(
    origin_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryPairCompatibilityListResponse:
    return country_pairs_service.list_destination_pair_contexts(
        connection, origin_slug, locale
    )

from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.routes import (
    EligibilityFlag,
    RouteDetailResponse,
    RouteListResponse,
    RouteType,
)
from app.services import routes as routes_service
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["routes"])


@router.get(
    "/countries/{country_slug}/routes",
    response_model=RouteListResponse,
)
def read_country_routes(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    route_type: RouteType | None = None,
    allows_work: EligibilityFlag | None = None,
    allows_family: EligibilityFlag | None = None,
    leads_to_pr: EligibilityFlag | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RouteListResponse:
    return routes_service.list_country_routes(
        connection,
        country_slug,
        locale,
        route_type,
        allows_work,
        allows_family,
        leads_to_pr,
        limit,
        offset,
    )


@router.get(
    "/countries/{country_slug}/routes/{route_slug}",
    response_model=RouteDetailResponse,
)
def read_country_route(
    country_slug: str,
    route_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> RouteDetailResponse:
    return routes_service.get_route_detail_by_slug(
        connection, country_slug, route_slug, locale
    )


@router.get("/routes/{route_id}", response_model=RouteDetailResponse)
def read_route(
    route_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> RouteDetailResponse:
    return routes_service.get_route_detail(connection, route_id, locale)

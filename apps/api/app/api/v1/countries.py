from app.core.database import get_connection
from app.core.errors import api_error
from app.core.locales import LocaleQuery
from app.repositories.cii import get_country_cii, get_scenario_metric_weights
from app.repositories.common import build_locale
from app.repositories.countries import (
    count_countries,
    get_country,
    get_profile,
    list_countries,
)
from app.repositories.scores import count_country_scores, list_country_scores
from app.schemas.cii_comparison import CiiCountryComparisonResponse
from app.schemas.common import Pagination
from app.schemas.countries import (
    CountryListResponse,
    CountryProfileResponse,
    CountryResponse,
)
from app.schemas.country_read_model import CountryReadModelCii, CountryReadModelResponse
from app.schemas.decision_engine import SourceListWithLocaleResponse
from app.schemas.scores import CountryScoreListResponse
from app.services import decision_engine
from app.services.cii_comparison import build_cii_comparison
from app.services.country_read_model import build_cii, get_country_read_model
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import Connection
from typing import Annotated, Any, Literal


router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("/compare", response_model=CiiCountryComparisonResponse, tags=["cii"])
async def compare_countries_cii(
    countries: Annotated[
        str, Query(description="Comma-separated country slugs, exactly 2 for MVP")
    ],
    scenario: Annotated[str, Query(description="Scenario slug")],
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CiiCountryComparisonResponse:
    slugs = [s.strip() for s in countries.split(",") if s.strip()]
    unique_slugs = list(dict.fromkeys(slugs))
    if len(unique_slugs) != 2:
        raise api_error(
            422,
            "countries_count_invalid",
            "Exactly 2 unique country slugs are required for comparison.",
            {"provided": slugs},
        )
    if not scenario:
        raise api_error(422, "scenario_required", "Scenario slug is required.", {})
    if not get_scenario_metric_weights(connection, scenario):
        raise api_error(
            422,
            "scenario_not_found",
            "Scenario not found or has no CII weights configured.",
            {"scenario": scenario},
        )
    return build_cii_comparison(connection, unique_slugs, scenario, locale)


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


@router.get("/{country_slug}", response_model=CountryResponse)
async def read_country(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> CountryResponse:
    row = get_country(connection, country_slug, locale)
    if row is None:
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
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


@router.get("/{country_slug}/cii", response_model=CountryReadModelCii)
async def read_country_cii(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    version: str = Query("v1.0", pattern=r"^v\d+\.\d+$"),
    scenario: str | None = Query(None),
) -> CountryReadModelCii:
    if scenario is not None:
        weights = get_scenario_metric_weights(connection, scenario)
        if not weights:
            raise api_error(
                422,
                "scenario_not_found",
                "Scenario not found or has no CII weights configured.",
                {"scenario": scenario},
            )
    scenario_slug = scenario if scenario is not None else ""
    row = get_country_cii(connection, country_slug, version, scenario_slug)
    cii = build_cii(row)
    if cii is None:
        raise HTTPException(
            status_code=404, detail="CII data not available for this country."
        )
    return cii


@router.get("/{country_slug}/sources", response_model=SourceListWithLocaleResponse)
async def read_country_sources(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    source_type: str | None = None,
    language: str | None = None,
    confidence: Literal["low", "medium", "high"] | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal[
        "title", "created_at", "published_at", "last_checked_at", "confidence"
    ] = "title",
    order: Literal["asc", "desc"] = "asc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SourceListWithLocaleResponse:
    return decision_engine.get_country_sources(
        connection,
        country_slug,
        locale,
        limit,
        offset,
        source_type,
        language,
        confidence,
        status,
        sort,
        order,
    )

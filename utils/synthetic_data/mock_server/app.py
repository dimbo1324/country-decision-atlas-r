from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Annotated
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticWorld,
)
from utils.synthetic_data.mock_server.fake_data import (
    WorldIndex,
    cii_preview_to_schema,
    comparison_to_schema,
    country_profile_to_schema,
    country_to_schema,
    resolve_locale,
    source_to_schema,
    trust_to_schema,
)
from utils.synthetic_data.mock_server.schemas import (
    CiiCountryComparisonResponse,
    CountryListResponse,
    CountryProfileResponse,
    CountryReadModelCii,
    CountryResponse,
    CountryTrustResponse,
    Pagination,
    SearchResponse,
    SearchResultItem,
    SourceListWithLocaleResponse,
)


DEFAULT_CORS_ORIGINS = ("http://localhost:3000",)


def _api_error(
    status_code: int, code: str, message: str, details: object = None
) -> HTTPException:
    """Matches apps/api/app/core/errors.py's `api_error()` exactly, so a
    frontend's error-handling code sees the same `{"error": {...}}` shape
    whether it's talking to the real backend or this mock."""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
                "details": details if details is not None else {},
            }
        },
    )


def _country_not_found(slug: str) -> HTTPException:
    return _api_error(
        404, "country_not_found", "Country not found.", {"country_slug": slug}
    )


def create_app(
    world: SyntheticWorld,
    *,
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS,
) -> FastAPI:
    """Serves an already-generated synthetic dataset over HTTP, mimicking
    the shape of apps/api's public read endpoints closely enough that
    apps/web can point NEXT_PUBLIC_API_BASE_URL at this server instead of
    the real backend + Postgres. Read-only, in-memory, no database, no
    network calls out -- and every response is fake, synthetic data."""
    index = WorldIndex.build(world)
    app = FastAPI(
        title="Country Decision Atlas -- synthetic mock server",
        description=FICTIONAL_NOTICE,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origins),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _mark_synthetic(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Synthetic-Data"] = "true"
        return response

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(
        _: Request, exc: HTTPException
    ) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": message,
                    "details": exc.detail,
                }
            },
        )

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "service": "country-decision-atlas-mock-server",
            "dataset_id": world.metadata.dataset_id,
            "countries": sorted(index.countries_by_slug),
            "fictional_notice": FICTIONAL_NOTICE,
        }

    @app.get("/api/v1/countries", response_model=CountryListResponse)
    def list_countries(
        locale: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> CountryListResponse:
        all_countries = sorted(
            index.countries_by_slug.values(), key=lambda country: country.slug
        )
        page = all_countries[offset : offset + limit]
        return CountryListResponse(
            items=[
                country_to_schema(country, generated_at=index.generated_at)
                for country in page
            ],
            pagination=Pagination(
                limit=limit, offset=offset, total=len(all_countries)
            ),
            locale=resolve_locale(locale),
        )

    @app.get(
        "/api/v1/countries/compare",
        response_model=CiiCountryComparisonResponse,
    )
    def compare_countries(
        countries: str, scenario: str
    ) -> CiiCountryComparisonResponse:
        slugs = [slug.strip() for slug in countries.split(",") if slug.strip()]
        unique_slugs = list(dict.fromkeys(slugs))
        if len(unique_slugs) != 2:
            raise _api_error(
                422,
                "countries_count_invalid",
                "Exactly 2 unique country slugs are required for comparison.",
                {"provided": slugs},
            )
        if not scenario:
            raise _api_error(
                422, "scenario_required", "Scenario slug is required.", {}
            )
        previews = []
        for slug in unique_slugs:
            preview = index.cii_previews_by_slug.get(slug)
            if preview is None:
                raise _country_not_found(slug)
            previews.append(preview)
        return comparison_to_schema(
            scenario_slug=scenario, preview_a=previews[0], preview_b=previews[1]
        )

    # NOTE: every route below with a `{country_slug}` path parameter must
    # stay registered *after* `/countries/compare` above -- Starlette
    # matches routes in registration order, so a path-parameter route
    # registered first would swallow `/countries/compare` as if "compare"
    # were a country slug (mirrors the same ordering apps/api's own
    # `countries.py` router relies on).
    @app.get("/api/v1/countries/{country_slug}", response_model=CountryResponse)
    def get_country(
        country_slug: str, locale: str | None = None
    ) -> CountryResponse:
        country = index.countries_by_slug.get(country_slug)
        if country is None:
            raise _country_not_found(country_slug)
        return CountryResponse(
            item=country_to_schema(country, generated_at=index.generated_at),
            locale=resolve_locale(locale),
        )

    @app.get(
        "/api/v1/countries/{country_slug}/profile",
        response_model=CountryProfileResponse,
    )
    def get_country_profile(
        country_slug: str, locale: str | None = None
    ) -> CountryProfileResponse:
        country = index.countries_by_slug.get(country_slug)
        if country is None:
            raise _country_not_found(country_slug)
        article = index.articles_by_country_id.get(country.country_id)
        return CountryProfileResponse(
            item=country_profile_to_schema(
                country, article, generated_at=index.generated_at
            ),
            locale=resolve_locale(locale),
        )

    @app.get(
        "/api/v1/countries/{country_slug}/trust",
        response_model=CountryTrustResponse,
    )
    def get_country_trust(country_slug: str) -> CountryTrustResponse:
        country = index.countries_by_slug.get(country_slug)
        if country is None:
            raise _country_not_found(country_slug)
        return trust_to_schema(
            country,
            legal_signal_count=1,
            generated_at=index.generated_at,
        )

    @app.get(
        "/api/v1/countries/{country_slug}/cii",
        response_model=CountryReadModelCii,
    )
    def get_country_cii(country_slug: str) -> CountryReadModelCii:
        preview = index.cii_previews_by_slug.get(country_slug)
        if preview is None:
            raise _country_not_found(country_slug)
        return cii_preview_to_schema(preview)

    @app.get(
        "/api/v1/countries/{country_slug}/sources",
        response_model=SourceListWithLocaleResponse,
    )
    def get_country_sources(
        country_slug: str, locale: str | None = None
    ) -> SourceListWithLocaleResponse:
        country = index.countries_by_slug.get(country_slug)
        if country is None:
            raise _country_not_found(country_slug)
        sources = index.sources_by_country_id.get(country.country_id, ())
        items = [
            source_to_schema(source, generated_at=index.generated_at)
            for source in sources
        ]
        return SourceListWithLocaleResponse(
            items=items,
            pagination=Pagination(limit=20, offset=0, total=len(items)),
            locale=resolve_locale(locale),
        )

    @app.get("/api/v1/search", response_model=SearchResponse)
    def search(q: str) -> SearchResponse:
        needle = q.strip().casefold()
        items: list[SearchResultItem] = []
        if needle:
            for country in index.countries_by_slug.values():
                article = index.articles_by_country_id.get(country.country_id)
                haystacks = [country.name, country.slug]
                if article is not None:
                    haystacks += [article.title, article.summary]
                if any(needle in text.casefold() for text in haystacks):
                    items.append(
                        SearchResultItem(
                            id=f"country:{country.country_id}",
                            entity_type="country",
                            entity_id=country.country_id,
                            country_slug=country.slug,
                            title=country.name,
                            snippet=(
                                article.summary if article else country.name
                            ),
                            path=f"/countries/{country.slug}",
                            rank=1.0
                            if needle in country.name.casefold()
                            else 0.5,
                        )
                    )
                for source in index.sources_by_country_id.get(
                    country.country_id, ()
                ):
                    if needle in source.title.casefold():
                        items.append(
                            SearchResultItem(
                                id=f"source:{source.source_id}",
                                entity_type="source",
                                entity_id=source.source_id,
                                country_slug=country.slug,
                                title=source.title,
                                snippet=source.title,
                                path=f"/countries/{country.slug}",
                                rank=0.5,
                            )
                        )
        items.sort(key=lambda item: item.rank, reverse=True)
        return SearchResponse(
            query=q,
            locale="en",
            total=len(items),
            limit=20,
            offset=0,
            items=items[:20],
        )

    return app

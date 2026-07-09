import logging
from app.api.v1 import (
    admin,
    admin_ai,
    admin_author_metrics,
    admin_capabilities,
    admin_community,
    admin_country_contribution,
    admin_migration_board,
    admin_moderation,
    admin_translation_jobs,
    admin_users,
    ai,
    analytics,
    auth,
    author_metrics,
    community,
    countries,
    country_contribution,
    country_drift,
    country_pairs,
    data_journal,
    decision,
    decision_passports,
    feature_flags,
    glossary,
    home,
    legal_signals,
    methodology,
    migration_board,
    personas,
    platform_metrics,
    routes,
    scenarios,
    search,
    sources,
    translations,
    trip_planner,
    trust,
    user_stories,
    watchlists,
    weight_profiles,
    what_changed,
)
from app.core.database import close_database_pool, open_database_pool
from app.schemas.system import HealthResponse, ReadinessResponse
from app.services.rate_limiter import check_rate_limit
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from psycopg import Error as PsycopgError
from starlette.concurrency import run_in_threadpool
from typing import Any


logger = logging.getLogger(__name__)


def create_app(
    *,
    settings: Any,
    rate_limit_client: Callable[[Request], str | None],
    health_handler: Callable[[], Awaitable[HealthResponse]],
    readiness_handler: Callable[[], ReadinessResponse],
) -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=_lifespan(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    _register_middleware(app, settings, rate_limit_client)
    _register_exception_handlers(app)
    _register_system_routes(app, health_handler, readiness_handler)
    _register_api_routes(app)
    _install_stable_openapi(app)
    return app


def _lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        open_database_pool()
        try:
            yield
        finally:
            close_database_pool()

    return lifespan


def error_response(
    status_code: int, code: str, message: str, details: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {"code": code, "message": message, "details": details}
        },
    )


_AUTH_RATE_LIMIT_PATHS = {"/api/v1/auth/login", "/api/v1/auth/register"}


def _register_middleware(
    app: FastAPI,
    settings: Any,
    rate_limit_client: Callable[[Request], str | None],
) -> None:
    @app.middleware("http")
    async def security_headers_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.middleware("http")
    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)
        is_auth_path = request.url.path in _AUTH_RATE_LIMIT_PATHS
        if not is_auth_path and settings.app_env != "production":
            return await call_next(request)
        client = rate_limit_client(request)
        if client is not None:
            if is_auth_path:
                allowed = await run_in_threadpool(
                    check_rate_limit,
                    f"auth:{client}",
                    limit=settings.api_rate_limit_auth_per_minute,
                    window_seconds=60,
                )
            else:
                allowed = await run_in_threadpool(
                    check_rate_limit,
                    f"general:{client}",
                    limit=settings.api_rate_limit_per_minute,
                    window_seconds=60,
                )
            if not allowed:
                return error_response(
                    429, "rate_limit_exceeded", "Too many requests."
                )
        return await call_next(request)


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _: Request, exc: HTTPException
    ) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
        return error_response(
            exc.status_code, "http_error", message, exc.detail
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            422, "validation_error", "Request validation failed.", exc.errors()
        )

    @app.exception_handler(LookupError)
    async def lookup_exception_handler(
        _: Request, exc: LookupError
    ) -> JSONResponse:
        return error_response(404, "not_found", str(exc))

    @app.exception_handler(PsycopgError)
    async def database_exception_handler(
        _: Request, exc: PsycopgError
    ) -> JSONResponse:
        logger.error("Database error", exc_info=exc)
        return error_response(
            500, "database_error", "A database error occurred."
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _: Request, exc: Exception
    ) -> JSONResponse:
        logger.error("Unhandled exception", exc_info=exc)
        return error_response(
            500, "internal_error", "An unexpected error occurred."
        )


def _register_system_routes(
    app: FastAPI,
    health_handler: Callable[[], Awaitable[HealthResponse]],
    readiness_handler: Callable[[], ReadinessResponse],
) -> None:
    app.get("/health", tags=["system"], response_model=HealthResponse)(
        health_handler
    )
    app.get(
        "/ready",
        tags=["system"],
        response_model=ReadinessResponse,
        responses={503: {"description": "Database unavailable"}},
    )(readiness_handler)


def _register_api_routes(app: FastAPI) -> None:
    app.include_router(trust.router, prefix="/api/v1")
    app.include_router(country_drift.router, prefix="/api/v1")
    app.include_router(methodology.router, prefix="/api/v1")
    app.include_router(glossary.router, prefix="/api/v1")
    app.include_router(platform_metrics.router, prefix="/api/v1")
    app.include_router(countries.router, prefix="/api/v1")
    app.include_router(data_journal.router, prefix="/api/v1")
    app.include_router(routes.router, prefix="/api/v1")
    app.include_router(country_pairs.router, prefix="/api/v1")
    app.include_router(legal_signals.router, prefix="/api/v1")
    app.include_router(legal_signals.top_level_router, prefix="/api/v1")
    app.include_router(scenarios.router, prefix="/api/v1")
    app.include_router(personas.router, prefix="/api/v1")
    app.include_router(sources.router, prefix="/api/v1")
    app.include_router(translations.router, prefix="/api/v1")
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(platform_metrics.admin_router, prefix="/api/v1")
    app.include_router(trust.admin_router, prefix="/api/v1")
    app.include_router(country_drift.admin_router, prefix="/api/v1")
    app.include_router(admin_translation_jobs.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(feature_flags.router, prefix="/api/v1")
    app.include_router(user_stories.router, prefix="/api/v1")
    app.include_router(decision.router, prefix="/api/v1")
    app.include_router(decision_passports.router, prefix="/api/v1")
    app.include_router(what_changed.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(ai.router, prefix="/api/v1")
    app.include_router(admin_ai.router, prefix="/api/v1")
    app.include_router(community.router, prefix="/api/v1")
    app.include_router(admin_community.router, prefix="/api/v1")
    app.include_router(migration_board.router, prefix="/api/v1")
    app.include_router(admin_migration_board.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(admin_users.router, prefix="/api/v1")
    app.include_router(admin_capabilities.router, prefix="/api/v1")
    app.include_router(admin_moderation.router, prefix="/api/v1")
    app.include_router(watchlists.router, prefix="/api/v1")
    app.include_router(weight_profiles.router, prefix="/api/v1")
    app.include_router(trip_planner.router, prefix="/api/v1")
    app.include_router(trip_planner.shared_router, prefix="/api/v1")
    app.include_router(author_metrics.router, prefix="/api/v1")
    app.include_router(admin_author_metrics.router, prefix="/api/v1")
    app.include_router(country_contribution.router, prefix="/api/v1")
    app.include_router(admin_country_contribution.router, prefix="/api/v1")
    app.include_router(home.router, prefix="/api/v1")


def _normalize_openapi_contract(value: Any) -> None:
    if isinstance(value, dict):
        description = value.get("description")
        if description == "Unprocessable Content":
            value["description"] = "Unprocessable Entity"
        enum_values = value.get("enum")
        if isinstance(enum_values, list) and set(enum_values) == {
            "low",
            "medium",
            "high",
        }:
            value["enum"] = ["high", "medium", "low"]
        for nested in value.values():
            _normalize_openapi_contract(nested)
    elif isinstance(value, list):
        for nested in value:
            _normalize_openapi_contract(nested)


def _install_stable_openapi(app: FastAPI) -> None:
    def stable_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
            webhooks=app.webhooks.routes,
            tags=app.openapi_tags,
            servers=app.servers,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            separate_input_output_schemas=app.separate_input_output_schemas,
        )
        _normalize_openapi_contract(schema)
        app.openapi_schema = schema
        return app.openapi_schema

    openapi_app: Any = app
    openapi_app.openapi = stable_openapi

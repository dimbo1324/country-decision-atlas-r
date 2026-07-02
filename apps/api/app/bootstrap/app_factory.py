from app.api.v1 import (
    admin,
    admin_translation_jobs,
    analytics,
    countries,
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
    personas,
    platform_metrics,
    routes,
    scenarios,
    sources,
    translations,
    trust,
    user_stories,
    what_changed,
)
from app.core.database import close_database_pool, open_database_pool
from app.schemas.system import HealthResponse, ReadinessResponse
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
import logging
from psycopg import Error as PsycopgError
import time
from typing import Any


logger = logging.getLogger(__name__)


def create_app(
    *,
    settings: Any,
    rate_limit_client: Callable[[Request], str | None],
    cleanup_rate_windows: Callable[[float], None],
    rate_windows: dict[str, list[float]],
    health_handler: Callable[[], Awaitable[HealthResponse]],
    readiness_handler: Callable[[], ReadinessResponse],
) -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=_lifespan(settings),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-Admin-Token"],
    )
    _register_middleware(
        app, settings, rate_limit_client, cleanup_rate_windows, rate_windows
    )
    _register_exception_handlers(app)
    _register_system_routes(app, health_handler, readiness_handler)
    _register_api_routes(app)
    _install_stable_openapi(app)
    return app


def _lifespan(settings: Any) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if not settings.admin_token:
            logger.warning(
                "Admin token is not configured - admin endpoints are disabled."
            )
        logger.warning(
            "Rate limiting is per-process (in-memory). "
            "In multi-worker deployments the effective limit scales with worker count. "
            "Migrate to Redis for cross-worker enforcement."
        )
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
        content={"error": {"code": code, "message": message, "details": details}},
    )


def _register_middleware(
    app: FastAPI,
    settings: Any,
    rate_limit_client: Callable[[Request], str | None],
    cleanup_rate_windows: Callable[[float], None],
    rate_windows: dict[str, list[float]],
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
        if settings.app_env != "production":
            return await call_next(request)
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)
        client = rate_limit_client(request)
        if client is not None:
            now = time.monotonic()
            cleanup_rate_windows(now)
            cutoff = now - 60.0
            recent = [t for t in rate_windows.get(client, []) if t > cutoff]
            if len(recent) >= settings.api_rate_limit_per_minute:
                return error_response(429, "rate_limit_exceeded", "Too many requests.")
            recent.append(now)
            rate_windows[client] = recent
        return await call_next(request)


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
        return error_response(exc.status_code, "http_error", message, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            422, "validation_error", "Request validation failed.", exc.errors()
        )

    @app.exception_handler(LookupError)
    async def lookup_exception_handler(_: Request, exc: LookupError) -> JSONResponse:
        return error_response(404, "not_found", str(exc))

    @app.exception_handler(PsycopgError)
    async def database_exception_handler(_: Request, exc: PsycopgError) -> JSONResponse:
        logger.error("Database error", exc_info=exc)
        return error_response(500, "database_error", "A database error occurred.")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception", exc_info=exc)
        return error_response(500, "internal_error", "An unexpected error occurred.")


def _register_system_routes(
    app: FastAPI,
    health_handler: Callable[[], Awaitable[HealthResponse]],
    readiness_handler: Callable[[], ReadinessResponse],
) -> None:
    app.get("/health", tags=["system"], response_model=HealthResponse)(health_handler)
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

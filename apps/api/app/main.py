from app.api.v1 import (
    admin,
    admin_translation_jobs,
    countries,
    decision,
    home,
    legal_signals,
    scenarios,
    sources,
    translations,
    user_stories,
)
from app.core.config import get_settings
from app.core.database import close_database_pool, get_pool, open_database_pool
from app.core.errors import api_error
from app.schemas.system import HealthResponse, ReadinessResponse
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import logging
from psycopg import Error as PsycopgError
from psycopg_pool import PoolTimeout
import time
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_rate_windows: dict[str, list[float]] = {}
_RATE_WINDOW = 60.0
_RATE_EXCLUDED_PATHS = frozenset({"/health", "/ready"})
_last_rate_cleanup = 0.0


def _rate_limit_client(request: Request) -> str | None:
    if request.client is None:
        return None
    if settings.trusted_proxy_headers:
        forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.client.host


def _cleanup_rate_windows(now: float) -> None:
    global _last_rate_cleanup
    if (
        now - _last_rate_cleanup < _RATE_WINDOW
        and len(_rate_windows) <= settings.api_rate_limit_max_clients
    ):
        return
    cutoff = now - _RATE_WINDOW
    active = {
        client: [timestamp for timestamp in timestamps if timestamp > cutoff]
        for client, timestamps in _rate_windows.items()
    }
    active = {client: timestamps for client, timestamps in active.items() if timestamps}
    if len(active) > settings.api_rate_limit_max_clients:
        active = dict(
            sorted(active.items(), key=lambda item: item[1][-1], reverse=True)[
                : settings.api_rate_limit_max_clients
            ]
        )
    _rate_windows.clear()
    _rate_windows.update(active)
    _last_rate_cleanup = now


def error_response(
    status_code: int, code: str, message: str, details: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if not settings.admin_token:
        logger.warning("Admin token is not configured — admin endpoints are disabled.")
    open_database_pool()
    try:
        yield
    finally:
        close_database_pool()


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Admin-Token"],
)


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
    if request.url.path in _RATE_EXCLUDED_PATHS:
        return await call_next(request)
    client = _rate_limit_client(request)
    if client is not None:
        now = time.monotonic()
        _cleanup_rate_windows(now)
        cutoff = now - _RATE_WINDOW
        recent = [t for t in _rate_windows.get(client, []) if t > cutoff]
        if len(recent) >= settings.api_rate_limit_per_minute:
            return error_response(429, "rate_limit_exceeded", "Too many requests.")
        recent.append(now)
        _rate_windows[client] = recent
    return await call_next(request)


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


@app.get("/health", tags=["system"], response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api", environment=settings.app_env)


@app.get(
    "/ready",
    tags=["system"],
    response_model=ReadinessResponse,
    responses={503: {"description": "Database unavailable"}},
)
def ready() -> ReadinessResponse:
    try:
        with get_pool().connection() as connection:
            connection.execute("SELECT 1").fetchone()
    except (PoolTimeout, PsycopgError, RuntimeError) as exc:
        raise api_error(
            503,
            "readiness_database_unavailable",
            "Database connectivity check failed.",
        ) from exc
    return ReadinessResponse(
        status="ready",
        service="api",
        environment=settings.app_env,
        database="ok",
    )


app.include_router(countries.router, prefix="/api/v1")
app.include_router(legal_signals.router, prefix="/api/v1")
app.include_router(legal_signals.top_level_router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(translations.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(admin_translation_jobs.router, prefix="/api/v1")
app.include_router(user_stories.router, prefix="/api/v1")
app.include_router(decision.router, prefix="/api/v1")
app.include_router(home.router, prefix="/api/v1")

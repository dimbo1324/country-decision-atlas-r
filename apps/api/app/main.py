from app.api.v1 import (
    admin,
    admin_translation_jobs,
    countries,
    decision,
    legal_signals,
    scenarios,
    sources,
    translations,
    user_stories,
)
from app.core.config import get_settings
from app.core.database import close_database_pool, open_database_pool
from collections import defaultdict
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import logging
from psycopg import Error as PsycopgError
import time
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_rate_windows: defaultdict[str, list[float]] = defaultdict(list)
_RATE_WINDOW = 60.0


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
    allow_credentials=True,
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
    if request.client is not None:
        ip = request.client.host
        now = time.monotonic()
        cutoff = now - _RATE_WINDOW
        recent = [t for t in _rate_windows[ip] if t > cutoff]
        if len(recent) >= settings.api_rate_limit_per_minute:
            return error_response(429, "rate_limit_exceeded", "Too many requests.")
        recent.append(now)
        if recent:
            _rate_windows[ip] = recent
        else:
            del _rate_windows[ip]
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


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


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

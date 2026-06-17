from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import admin, countries, legal_signals, scenarios, sources, translations
from app.core.config import get_settings
from app.core.database import close_database_pool, open_database_pool


def error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
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
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
    return error_response(exc.status_code, "http_error", message, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "validation_error", "Request validation failed.", exc.errors())


@app.exception_handler(LookupError)
async def lookup_exception_handler(_: Request, exc: LookupError) -> JSONResponse:
    return error_response(404, "not_found", str(exc))


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api", "environment": settings.app_env}


app.include_router(countries.router, prefix="/api/v1")
app.include_router(legal_signals.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(translations.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

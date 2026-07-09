import logging
from app.bootstrap.app_factory import create_app
from app.core.config import get_settings
from app.core.database import get_pool
from app.core.errors import api_error
from app.schemas.system import HealthResponse, ReadinessResponse
from fastapi import Request
from psycopg import Error as PsycopgError
from psycopg_pool import PoolTimeout
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
settings = get_settings()


def _rate_limit_client(request: Request) -> str | None:
    if request.client is None:
        return None
    if (
        settings.trusted_proxy_headers
        and request.client.host in settings.trusted_proxy_ip_set
    ):
        forwarded = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        )
        if forwarded:
            return forwarded
    return request.client.host


async def health() -> HealthResponse:
    return HealthResponse(
        status="ok", service="api", environment=settings.app_env
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


app = create_app(
    settings=settings,
    rate_limit_client=_rate_limit_client,
    health_handler=health,
    readiness_handler=ready,
)


def stable_openapi() -> dict[str, Any]:
    return app.openapi()


openapi_app: Any = app

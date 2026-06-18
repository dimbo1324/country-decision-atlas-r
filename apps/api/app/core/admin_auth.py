from app.core.config import get_settings
from app.core.errors import api_error
from fastapi import Security
from fastapi.security import APIKeyHeader
import secrets


admin_token_header = APIKeyHeader(
    name="X-Admin-Token",
    scheme_name="AdminTokenAuth",
    auto_error=False,
)


def require_admin_token(
    x_admin_token: str | None = Security(admin_token_header),
) -> str:
    settings = get_settings()
    if not settings.admin_token:
        raise api_error(
            500,
            "admin_token_not_configured",
            "Admin token is not configured.",
        )
    if x_admin_token is None or not secrets.compare_digest(
        x_admin_token, settings.admin_token
    ):
        raise api_error(
            401,
            "admin_unauthorized",
            "Admin token is missing or invalid.",
        )
    return "admin"

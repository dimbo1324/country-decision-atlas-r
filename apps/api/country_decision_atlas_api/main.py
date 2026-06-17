from country_decision_atlas_contracts.models import HealthResponse
from country_decision_atlas_shared.config import get_settings
from fastapi import FastAPI

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.get("/health", tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api", environment=settings.app_env)

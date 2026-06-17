from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    app_name: str = "Country Decision Atlas"
    app_env: str = "local"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    api_rate_limit_per_minute: int = 120
    database_url: str = Field(
        default="postgresql://country_atlas:change-me@localhost:5433/country_atlas"
    )
    redis_url: str = "redis://localhost:6379/0"
    meilisearch_host: str = "http://localhost:7700"
    source_refresh_enabled: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    app_name: str = "Country Decision Atlas"
    app_env: str = "production"
    app_debug: bool = False
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str = Field(
        default="postgresql://country_atlas:change-me@localhost:5433/country_atlas"
    )
    redis_url: str = "redis://localhost:6379/0"
    default_locale: str = "ru"
    supported_locales: str = "en,ru"
    admin_token: str | None = None
    api_rate_limit_per_minute: int = 120
    api_rate_limit_max_clients: int = 10000
    trusted_proxy_headers: bool = False
    translation_provider: str = "fake"
    ai_translation_provider: str = "openai"
    ai_translation_model: str = "gpt-4o-mini"
    ai_translation_api_key: str | None = None
    ai_translation_timeout_seconds: int = 30
    ai_translation_max_retries: int = 2
    translation_job_lock_timeout_seconds: int = 900
    translation_job_max_batch_size: int = 100

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.api_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def supported_locale_codes(self) -> set[str]:
        return {
            locale.strip()
            for locale in self.supported_locales.split(",")
            if locale.strip()
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

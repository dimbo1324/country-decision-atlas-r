from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Country Decision Atlas"
    app_env: str = "local"
    app_debug: bool = True
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str = Field(
        default="postgresql://country_atlas:change-me@localhost:5433/country_atlas"
    )
    redis_url: str = "redis://localhost:6379/0"
    default_locale: str = "en"
    supported_locales: str = "en,ru"
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]
    @property
    def supported_locale_codes(self) -> set[str]:
        return {locale.strip() for locale in self.supported_locales.split(",") if locale.strip()}
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

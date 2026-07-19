from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


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
    api_rate_limit_per_minute: int = 120
    api_rate_limit_auth_per_minute: int = 10
    trusted_proxy_headers: bool = False
    trusted_proxy_ips: str = ""
    auth_login_max_failed_attempts: int = 5
    auth_login_failure_window_seconds: int = 900
    auth_login_lockout_seconds: int = 60
    auth_login_lockout_max_seconds: int = 900
    analytics_enabled: bool = True
    analytics_salt: str = "local-dev-analytics-salt"
    cache_mode: str = "null"
    cache_namespace: str = "cda"
    cache_default_ttl_seconds: int = 300
    translation_provider: str = "fake"
    ai_translation_provider: str = "openai"
    ai_translation_model: str = "gpt-4o-mini"
    ai_translation_api_key: str | None = None
    ai_translation_timeout_seconds: int = 30
    ai_translation_max_retries: int = 2
    translation_job_lock_timeout_seconds: int = 900
    translation_job_max_batch_size: int = 100
    ai_mode: Literal["fake", "real", "off"] = "fake"
    ai_provider: str = "fake"
    ai_model: str = "fake-grounded-v1"
    ai_model_version: str = "v1"
    ai_max_context_items: int = 8
    ai_max_context_chars: int = 12000
    ai_log_interactions: bool = True
    auth_session_ttl_hours: int = 168
    auth_session_touch_interval_minutes: int = 5
    auth_password_min_length: int = 12
    auth_registration_enabled: bool = True
    auth_session_cookie_name: str = "cda_session"
    auth_csrf_cookie_name: str = "cda_csrf"
    auth_session_rotation_interval_minutes: int = 15
    auth_session_rotation_grace_seconds: int = 30
    auth_device_fingerprint_salt: str = "local-dev-device-fingerprint-salt"
    security_hsts_enabled: bool = False
    notifier_internal_auth_token: str | None = None
    notifier_grpc_addr: str = "localhost:9090"
    database_pool_min_size: int = 1
    database_pool_max_size: int = 10
    database_pool_timeout_seconds: float = 30.0
    redis_connect_timeout_seconds: float = 0.2

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.api_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def trusted_proxy_ip_set(self) -> set[str]:
        return {
            ip.strip() for ip in self.trusted_proxy_ips.split(",") if ip.strip()
        }

    @model_validator(mode="after")
    def _forbid_default_secrets_in_production(self) -> "Settings":
        """P1-10, Аудит-эпизод 6: nothing stops the app from booting in
        production with the same placeholder secrets docker-compose.yml
        ships for local dev — fail loudly instead of running with a
        guessable analytics salt or a weak/absent inter-service token."""
        if self.app_env != "production":
            return self
        unsafe: list[str] = []
        if "change-me" in self.database_url:
            unsafe.append("database_url")
        if self.analytics_salt == "local-dev-analytics-salt":
            unsafe.append("analytics_salt")
        if self.notifier_internal_auth_token in (None, "dev-grpc-token"):
            unsafe.append("notifier_internal_auth_token")
        if unsafe:
            raise RuntimeError(
                "Refusing to start with APP_ENV=production while these "
                f"settings still hold their local-dev default: {', '.join(unsafe)}. "
                "Set real values via environment variables or .env before "
                "starting in production."
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

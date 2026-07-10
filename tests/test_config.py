"""Settings: production fail-fast on default dev secrets (P1-10, Аудит-эпизод 6)."""

import pytest
from app.core.config import Settings
from typing import Any


_REAL_DATABASE_URL = "postgresql://real:realpass@dbhost:5432/realdb"
_REAL_ANALYTICS_SALT = "a-real-random-analytics-salt"
_REAL_NOTIFIER_TOKEN = "a-real-notifier-token"


def _production_settings(**overrides: Any) -> Settings:
    data: dict[str, Any] = {
        "app_env": "production",
        "database_url": _REAL_DATABASE_URL,
        "analytics_salt": _REAL_ANALYTICS_SALT,
        "notifier_internal_auth_token": _REAL_NOTIFIER_TOKEN,
    }
    data.update(overrides)
    return Settings(**data)


def test_production_with_default_database_url_raises() -> None:
    with pytest.raises(RuntimeError, match="database_url"):
        _production_settings(
            database_url="postgresql://country_atlas:change-me@localhost:5433/country_atlas"
        )


def test_production_with_default_analytics_salt_raises() -> None:
    with pytest.raises(RuntimeError, match="analytics_salt"):
        _production_settings(analytics_salt="local-dev-analytics-salt")


def test_production_with_missing_notifier_token_raises() -> None:
    with pytest.raises(RuntimeError, match="notifier_internal_auth_token"):
        _production_settings(notifier_internal_auth_token=None)


def test_production_with_docker_compose_default_notifier_token_raises() -> None:
    with pytest.raises(RuntimeError, match="notifier_internal_auth_token"):
        _production_settings(notifier_internal_auth_token="dev-grpc-token")


def test_production_with_all_defaults_lists_every_unsafe_field() -> None:
    with pytest.raises(RuntimeError) as exc:
        Settings(app_env="production")
    message = str(exc.value)
    assert "database_url" in message
    assert "analytics_salt" in message
    assert "notifier_internal_auth_token" in message


def test_production_with_real_values_does_not_raise() -> None:
    settings = _production_settings()
    assert settings.app_env == "production"


def test_local_with_default_secrets_does_not_raise() -> None:
    settings = Settings(app_env="local")
    assert settings.database_url != _REAL_DATABASE_URL


def test_non_production_app_env_skips_validation_entirely() -> None:
    # Validation only fires on the exact string "production", matching the
    # existing app_env == "production" checks elsewhere (Secure cookie flag
    # in auth.py, the general rate limiter in app_factory.py) rather than
    # services/feature_flags.py's inverted "local" vs "everything else"
    # convention. A value like "staging" is deliberately not covered here -
    # same scope as the audit finding this closes (P1-10).
    settings = Settings(app_env="staging")
    assert (
        settings.database_url == Settings.model_fields["database_url"].default
    )

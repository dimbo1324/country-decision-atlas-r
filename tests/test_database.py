"""Database pool: configurable size/timeout from Settings, and stats exposure (P2-4, Аудит-эпизод 6)."""

import pytest
from app.core import database
from app.core.config import Settings
from typing import Any
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def _reset_pool() -> Any:
    database._pool = None
    database._readiness_pool = None
    yield
    database._pool = None
    database._readiness_pool = None


def test_open_database_pool_uses_settings_pool_sizing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_pool(**kwargs: Any) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    monkeypatch.setattr(database, "ConnectionPool", fake_pool)
    settings = Settings(
        app_env="local",
        database_pool_min_size=3,
        database_pool_max_size=25,
        database_pool_timeout_seconds=12.5,
    )

    database.open_database_pool(settings)

    assert captured["min_size"] == 3
    assert captured["max_size"] == 25
    assert captured["timeout"] == 12.5


def test_open_database_pool_defaults_match_previous_hardcoded_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_pool(**kwargs: Any) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    monkeypatch.setattr(database, "ConnectionPool", fake_pool)
    settings = Settings(app_env="local")

    database.open_database_pool(settings)

    assert captured["min_size"] == 1
    assert captured["max_size"] == 10
    assert captured["timeout"] == 30.0


def test_open_database_pool_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    def fake_pool(**kwargs: Any) -> MagicMock:
        calls.append(kwargs)
        return MagicMock()

    monkeypatch.setattr(database, "ConnectionPool", fake_pool)
    settings = Settings(app_env="local")

    database.open_database_pool(settings)
    database.open_database_pool(settings)

    assert len(calls) == 1


def test_close_database_pool_clears_the_pool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pool = MagicMock()
    monkeypatch.setattr(database, "ConnectionPool", lambda **_kw: pool)
    database.open_database_pool(Settings(app_env="local"))

    database.close_database_pool()

    pool.close.assert_called_once()
    with pytest.raises(RuntimeError):
        database.get_pool()


def test_get_pool_raises_when_not_initialized() -> None:
    with pytest.raises(RuntimeError, match="not initialized"):
        database.get_pool()


def test_get_pool_stats_delegates_to_pool_get_stats(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pool = MagicMock()
    pool.get_stats.return_value = {"pool_size": 5, "requests_waiting": 0}
    monkeypatch.setattr(database, "ConnectionPool", lambda **_kw: pool)
    database.open_database_pool(Settings(app_env="local"))

    stats = database.get_pool_stats()

    assert stats == {"pool_size": 5, "requests_waiting": 0}
    pool.get_stats.assert_called_once()


def test_get_pool_stats_raises_when_not_initialized() -> None:
    with pytest.raises(RuntimeError, match="not initialized"):
        database.get_pool_stats()


def test_open_readiness_pool_uses_tiny_fixed_sizing_regardless_of_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_pool(**kwargs: Any) -> MagicMock:
        captured.update(kwargs)
        return MagicMock()

    monkeypatch.setattr(database, "ConnectionPool", fake_pool)
    settings = Settings(
        app_env="local",
        database_pool_min_size=3,
        database_pool_max_size=25,
        database_pool_timeout_seconds=12.5,
    )

    database.open_readiness_pool(settings)

    assert captured["min_size"] == 1
    assert captured["max_size"] == 2
    assert captured["timeout"] == 5.0


def test_open_readiness_pool_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    def fake_pool(**kwargs: Any) -> MagicMock:
        calls.append(kwargs)
        return MagicMock()

    monkeypatch.setattr(database, "ConnectionPool", fake_pool)
    settings = Settings(app_env="local")

    database.open_readiness_pool(settings)
    database.open_readiness_pool(settings)

    assert len(calls) == 1


def test_close_readiness_pool_clears_the_pool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pool = MagicMock()
    monkeypatch.setattr(database, "ConnectionPool", lambda **_kw: pool)
    database.open_readiness_pool(Settings(app_env="local"))

    database.close_readiness_pool()

    pool.close.assert_called_once()
    with pytest.raises(RuntimeError):
        database.get_readiness_pool()


def test_get_readiness_pool_raises_when_not_initialized() -> None:
    with pytest.raises(RuntimeError, match="not initialized"):
        database.get_readiness_pool()


def test_readiness_pool_independent_of_main_pool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main_pool = MagicMock()
    readiness_pool = MagicMock()
    calls = iter([main_pool, readiness_pool])
    monkeypatch.setattr(database, "ConnectionPool", lambda **_kw: next(calls))
    settings = Settings(app_env="local")

    database.open_database_pool(settings)
    database.open_readiness_pool(settings)

    assert database.get_pool() is main_pool
    assert database.get_readiness_pool() is readiness_pool
    assert database.get_pool() is not database.get_readiness_pool()

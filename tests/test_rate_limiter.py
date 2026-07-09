"""Redis-backed request rate limiting and per-account login lockout."""

import pytest
from app.core.config import Settings
from app.services import rate_limiter
from typing import Any


class _FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def ping(self) -> bool:
        return True

    def incr(self, key: str) -> int:
        current = int(self.values.get(key, "0")) + 1
        self.values[key] = str(current)
        return current

    def expire(self, key: str, seconds: int) -> None:
        self.ttls[key] = seconds

    def exists(self, key: str) -> int:
        return 1 if key in self.values else 0

    def setex(self, key: str, seconds: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = seconds

    def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)
            self.ttls.pop(key, None)


class _BrokenRedis:
    def ping(self) -> bool:
        raise ConnectionError("redis unavailable")


@pytest.fixture(autouse=True)
def _clear_redis_client_cache() -> Any:
    rate_limiter._get_redis_client.cache_clear()
    yield
    rate_limiter._get_redis_client.cache_clear()


def _settings(**overrides: Any) -> Settings:
    data: dict[str, Any] = {
        "app_env": "local",
        "auth_login_max_failed_attempts": 3,
        "auth_login_failure_window_seconds": 900,
        "auth_login_lockout_seconds": 60,
        "auth_login_lockout_max_seconds": 900,
    }
    data.update(overrides)
    return Settings(**data)


def test_check_rate_limit_allows_requests_under_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    for _ in range(5):
        assert rate_limiter.check_rate_limit("ip:1", limit=5, window_seconds=60)


def test_check_rate_limit_blocks_requests_over_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    for _ in range(5):
        rate_limiter.check_rate_limit("ip:2", limit=5, window_seconds=60)
    assert (
        rate_limiter.check_rate_limit("ip:2", limit=5, window_seconds=60)
        is False
    )


def test_check_rate_limit_fails_open_without_redis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: None)
    assert rate_limiter.check_rate_limit("ip:3", limit=1, window_seconds=60)
    assert rate_limiter.check_rate_limit("ip:3", limit=1, window_seconds=60)


def test_check_rate_limit_fails_open_on_redis_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _RaisingRedis:
        def incr(self, _key: str) -> int:
            raise ConnectionError("boom")

    monkeypatch.setattr(
        rate_limiter, "_get_redis_client", lambda: _RaisingRedis()
    )
    assert rate_limiter.check_rate_limit("ip:4", limit=1, window_seconds=60)


def test_login_lockout_triggers_after_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    settings = _settings()
    email = "user@example.local"
    assert rate_limiter.is_login_locked_out(email) is False
    for _ in range(settings.auth_login_max_failed_attempts):
        rate_limiter.record_login_failure(email, settings)
    assert rate_limiter.is_login_locked_out(email) is True


def test_login_lockout_duration_grows_with_repeated_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    settings = _settings()
    email = "grower@example.local"
    for _ in range(settings.auth_login_max_failed_attempts):
        rate_limiter.record_login_failure(email, settings)
    lockout_key = (
        f"{rate_limiter._LOGIN_LOCKOUT_PREFIX}:"
        f"{rate_limiter._hash_identifier(email)}"
    )
    first_ttl = fake.ttls[lockout_key]
    assert first_ttl == settings.auth_login_lockout_seconds
    rate_limiter.record_login_failure(email, settings)
    second_ttl = fake.ttls[lockout_key]
    assert second_ttl > first_ttl


def test_login_lockout_duration_capped_at_max(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    settings = _settings(auth_login_lockout_max_seconds=100)
    email = "capped@example.local"
    for _ in range(settings.auth_login_max_failed_attempts + 10):
        rate_limiter.record_login_failure(email, settings)
    lockout_key = (
        f"{rate_limiter._LOGIN_LOCKOUT_PREFIX}:"
        f"{rate_limiter._hash_identifier(email)}"
    )
    assert fake.ttls[lockout_key] == settings.auth_login_lockout_max_seconds


def test_clear_login_failures_removes_counter_and_lockout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: fake)
    settings = _settings()
    email = "cleared@example.local"
    for _ in range(settings.auth_login_max_failed_attempts):
        rate_limiter.record_login_failure(email, settings)
    assert rate_limiter.is_login_locked_out(email) is True
    rate_limiter.clear_login_failures(email)
    assert rate_limiter.is_login_locked_out(email) is False


def test_login_lockout_fails_open_without_redis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rate_limiter, "_get_redis_client", lambda: None)
    assert rate_limiter.is_login_locked_out("nobody@example.local") is False
    rate_limiter.record_login_failure("nobody@example.local")
    rate_limiter.clear_login_failures("nobody@example.local")


def test_get_redis_client_returns_none_when_ping_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import redis

    monkeypatch.setattr(
        redis.Redis, "from_url", staticmethod(lambda *_a, **_kw: _BrokenRedis())
    )
    assert rate_limiter._get_redis_client() is None

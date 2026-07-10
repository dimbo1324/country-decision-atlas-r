"""Null and Redis cache backends: miss/error behavior and cache-key composition."""

from app.core.config import Settings
from app.services.cache import (
    NullCache,
    RedisCache,
    get_cache_backend,
    reset_cache_backend,
)
from app.services.cache_invalidation import invalidate_platform_read_cache
from app.services.cache_keys import (
    countries_matrix_key,
    country_card_key,
    filter_hash,
    legal_timeline_key,
    routes_key,
)
from typing import Any


class FailingRedis:
    def get(self, *_args: Any) -> bytes | None:
        raise RuntimeError("redis down")

    def setex(self, *_args: Any) -> None:
        raise RuntimeError("redis down")

    def delete(self, *_args: Any) -> None:
        raise RuntimeError("redis down")

    def scan_iter(self, *_args: Any) -> list[str]:
        raise RuntimeError("redis down")


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.deleted: list[str] = []

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self.values[key] = value

    def delete(self, *keys: str) -> None:
        self.deleted.extend(keys)
        for key in keys:
            self.values.pop(key, None)

    def scan_iter(self, pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [key for key in self.values if key.startswith(prefix)]


def test_null_cache_always_misses_and_never_errors() -> None:
    cache = NullCache()
    assert cache.get_json("v1:test") is None
    cache.set_json("v1:test", {"ok": True}, 30)
    cache.delete("v1:test")
    cache.delete_by_prefix("v1:")


def test_redis_cache_failures_are_non_fatal() -> None:
    cache = RedisCache(FailingRedis(), "cda")
    assert cache.get_json("v1:test") is None
    cache.set_json("v1:test", {"ok": True}, 30)
    cache.delete("v1:test")
    cache.delete_by_prefix("v1:")


def test_get_or_set_json_calls_loader_on_miss_and_not_on_hit() -> None:
    redis = FakeRedis()
    cache = RedisCache(redis, "cda")
    calls = {"count": 0}

    def loader() -> dict[str, Any]:
        calls["count"] += 1
        return {"value": calls["count"]}

    assert cache.get_or_set_json("v1:item", 30, loader) == {"value": 1}
    assert cache.get_or_set_json("v1:item", 30, loader) == {"value": 1}
    assert calls["count"] == 1


def test_cache_keys_include_response_affecting_params() -> None:
    assert "locale=ru" in country_card_key("russia", "ru")
    assert "russia" in country_card_key("russia", "ru")
    assert "filters=" in countries_matrix_key("ru", ["russia"], ["relocation"])
    assert "filters=" in routes_key("argentina", "ru", {"route_type": "work"})
    assert "filters=" in legal_timeline_key("russia", "ru", {"year_from": 2026})


def test_filter_hash_excludes_sensitive_keys() -> None:
    left = filter_hash({"route_type": "work", "admin_token": "secret"})
    right = filter_hash({"route_type": "work", "admin_token": "other"})
    assert left == right


def test_delete_by_prefix_deletes_expected_keys() -> None:
    redis = FakeRedis()
    cache = RedisCache(redis, "cda")
    cache.set_json("v1:routes:russia:locale=ru", {"ok": True}, 30)
    cache.set_json("v1:routes:uruguay:locale=ru", {"ok": True}, 30)
    cache.delete_by_prefix("v1:routes:russia:")
    assert "cda:v1:routes:russia:locale=ru" in redis.deleted
    assert "cda:v1:routes:uruguay:locale=ru" in redis.values


def test_invalidation_calls_expected_prefixes() -> None:
    redis = FakeRedis()
    cache = RedisCache(redis, "cda")
    for key in [
        "v1:home:overview:locale=ru",
        "v1:country:russia:card:locale=ru",
        "v1:routes:russia:locale=ru",
        "v1:timeline:russia:locale=ru",
    ]:
        cache.set_json(key, {"ok": True}, 30)
    invalidate_platform_read_cache("russia", cache)
    assert not redis.values


def test_cache_disabled_returns_null_cache() -> None:
    assert isinstance(get_cache_backend(Settings(cache_mode="null")), NullCache)


def test_get_cache_backend_returns_the_same_redis_client_on_repeat_calls() -> (
    None
):
    reset_cache_backend()
    try:
        settings = Settings(
            cache_mode="redis", redis_url="redis://localhost:6379/0"
        )
        first = get_cache_backend(settings)
        second = get_cache_backend(settings)
        assert first is second
    finally:
        reset_cache_backend()


def test_reset_cache_backend_forces_a_fresh_client() -> None:
    reset_cache_backend()
    try:
        settings = Settings(
            cache_mode="redis", redis_url="redis://localhost:6379/0"
        )
        first = get_cache_backend(settings)
        reset_cache_backend()
        second = get_cache_backend(settings)
        assert first is not second
    finally:
        reset_cache_backend()

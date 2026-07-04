import json
import logging
from app.core.config import Settings, get_settings
from collections.abc import Callable
from typing import Any, Protocol


logger = logging.getLogger(__name__)
MAX_KEY_LENGTH = 240
MAX_TTL_SECONDS = 86400


class CacheBackend(Protocol):
    def get_json(self, key: str) -> Any | None: ...
    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None: ...
    def delete(self, key: str) -> None: ...
    def delete_by_prefix(self, prefix: str) -> None: ...
    def get_or_set_json(
        self, key: str, ttl_seconds: int, loader: Callable[[], Any]
    ) -> Any: ...


class NullCache:
    def get_json(self, key: str) -> Any | None:
        _validate_key(key)
        return None

    def set_json(self, key: str, _value: Any, ttl_seconds: int) -> None:
        _validate_key(key)
        _validate_ttl(ttl_seconds)

    def delete(self, key: str) -> None:
        _validate_key(key)

    def delete_by_prefix(self, prefix: str) -> None:
        _validate_key(prefix)

    def get_or_set_json(
        self, key: str, ttl_seconds: int, loader: Callable[[], Any]
    ) -> Any:
        _validate_key(key)
        _validate_ttl(ttl_seconds)
        return loader()


class RedisCache:
    def __init__(self, client: Any, namespace: str) -> None:
        self.client = client
        self.namespace = namespace.strip(":") or "cda"

    def get_json(self, key: str) -> Any | None:
        namespaced = self._namespaced(key)
        try:
            raw = self.client.get(namespaced)
        except Exception as exc:
            logger.warning("Redis cache get failed.", exc_info=exc)
            return None
        if raw is None:
            return None
        try:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            return json.loads(text)
        except (TypeError, ValueError, UnicodeDecodeError) as exc:
            logger.warning("Redis cache JSON decode failed.", exc_info=exc)
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        namespaced = self._namespaced(key)
        ttl = _validate_ttl(ttl_seconds)
        try:
            payload = json.dumps(value, default=str, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            logger.warning("Redis cache JSON encode failed.", exc_info=exc)
            return
        try:
            self.client.setex(namespaced, ttl, payload)
        except Exception as exc:
            logger.warning("Redis cache set failed.", exc_info=exc)

    def delete(self, key: str) -> None:
        namespaced = self._namespaced(key)
        try:
            self.client.delete(namespaced)
        except Exception as exc:
            logger.warning("Redis cache delete failed.", exc_info=exc)

    def delete_by_prefix(self, prefix: str) -> None:
        namespaced = self._namespaced(prefix)
        try:
            keys = list(self.client.scan_iter(f"{namespaced}*"))
            if keys:
                self.client.delete(*keys)
        except Exception as exc:
            logger.warning("Redis cache prefix delete failed.", exc_info=exc)

    def get_or_set_json(
        self, key: str, ttl_seconds: int, loader: Callable[[], Any]
    ) -> Any:
        cached = self.get_json(key)
        if cached is not None:
            return cached
        value = loader()
        self.set_json(key, value, ttl_seconds)
        return value

    def _namespaced(self, key: str) -> str:
        safe_key = _validate_key(key)
        return f"{self.namespace}:{safe_key}"


def get_cache_backend(settings: Settings | None = None) -> CacheBackend:
    resolved = settings or get_settings()
    if resolved.cache_mode != "redis":
        return NullCache()
    try:
        from redis import Redis

        client = Redis.from_url(
            resolved.redis_url, socket_connect_timeout=0.2, socket_timeout=0.2
        )
        return RedisCache(client, resolved.cache_namespace)
    except Exception as exc:
        logger.warning("Redis cache initialization failed.", exc_info=exc)
        return NullCache()


def cache_ttl(settings: Settings | None = None) -> int:
    resolved = settings or get_settings()
    return _validate_ttl(resolved.cache_default_ttl_seconds)


def _validate_key(key: str) -> str:
    if not key or len(key) > MAX_KEY_LENGTH:
        raise ValueError("Invalid cache key length.")
    return key


def _validate_ttl(ttl_seconds: int) -> int:
    if ttl_seconds <= 0:
        raise ValueError("Cache TTL must be positive.")
    return min(ttl_seconds, MAX_TTL_SECONDS)

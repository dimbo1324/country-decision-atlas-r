import hashlib
import logging
from app.core.config import Settings, get_settings
from functools import lru_cache
from typing import Any


logger = logging.getLogger(__name__)

_LOGIN_FAILURES_PREFIX = "login_fail"
_LOGIN_LOCKOUT_PREFIX = "login_lockout"
_RATE_LIMIT_PREFIX = "rate_limit"


@lru_cache(maxsize=1)
def _get_redis_client() -> Any | None:
    settings = get_settings()
    try:
        from redis import Redis

        client = Redis.from_url(
            settings.redis_url, socket_connect_timeout=0.2, socket_timeout=0.2
        )
        client.ping()
        return client
    except Exception as exc:
        logger.warning("Rate limiter Redis connection failed.", exc_info=exc)
        return None


def _hash_identifier(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


def check_rate_limit(key: str, *, limit: int, window_seconds: int) -> bool:
    """Fixed-window counter. Returns True if the request is allowed."""
    client = _get_redis_client()
    if client is None:
        return True
    redis_key = f"{_RATE_LIMIT_PREFIX}:{key}"
    try:
        count = client.incr(redis_key)
        if count == 1:
            client.expire(redis_key, window_seconds)
        return int(count) <= limit
    except Exception as exc:
        logger.warning("Rate limit check failed; failing open.", exc_info=exc)
        return True


def is_login_locked_out(normalized_email: str) -> bool:
    client = _get_redis_client()
    if client is None:
        return False
    key = f"{_LOGIN_LOCKOUT_PREFIX}:{_hash_identifier(normalized_email)}"
    try:
        return bool(client.exists(key))
    except Exception as exc:
        logger.warning(
            "Login lockout check failed; failing open.", exc_info=exc
        )
        return False


def record_login_failure(
    normalized_email: str, settings: Settings | None = None
) -> None:
    resolved = settings or get_settings()
    client = _get_redis_client()
    if client is None:
        return
    identifier = _hash_identifier(normalized_email)
    failures_key = f"{_LOGIN_FAILURES_PREFIX}:{identifier}"
    try:
        count = client.incr(failures_key)
        if count == 1:
            client.expire(
                failures_key, resolved.auth_login_failure_window_seconds
            )
        if count >= resolved.auth_login_max_failed_attempts:
            excess = count - resolved.auth_login_max_failed_attempts
            lockout_seconds = min(
                resolved.auth_login_lockout_seconds * (2**excess),
                resolved.auth_login_lockout_max_seconds,
            )
            lockout_key = f"{_LOGIN_LOCKOUT_PREFIX}:{identifier}"
            client.setex(lockout_key, lockout_seconds, "1")
            logger.warning(
                "Login lockout triggered after %s failed attempts "
                "(identifier=%s, lockout_seconds=%s).",
                count,
                identifier,
                lockout_seconds,
            )
    except Exception as exc:
        logger.warning("Recording login failure failed.", exc_info=exc)


def clear_login_failures(normalized_email: str) -> None:
    client = _get_redis_client()
    if client is None:
        return
    identifier = _hash_identifier(normalized_email)
    try:
        client.delete(
            f"{_LOGIN_FAILURES_PREFIX}:{identifier}",
            f"{_LOGIN_LOCKOUT_PREFIX}:{identifier}",
        )
    except Exception as exc:
        logger.warning("Clearing login failures failed.", exc_info=exc)

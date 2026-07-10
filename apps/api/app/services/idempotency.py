from app.services.cache import CacheBackend
from collections.abc import Callable
from typing import Any


IDEMPOTENCY_KEY_TTL_SECONDS = 86400
MAX_IDEMPOTENCY_KEY_LENGTH = 128


def with_idempotency_key(
    cache: CacheBackend,
    *,
    scope: str,
    user_id: str,
    idempotency_key: str | None,
    create: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Replays the cached response for a repeated create request instead of
    creating a duplicate (P3-4, Аудит-эпизод 10).

    Guards the most sensitive create endpoints (country proposals, author
    metric definitions) against double-submit — a stale client retry or a
    double click resubmitting the exact same `Idempotency-Key` gets back the
    original response rather than a second draft. Without a key, behaves
    exactly as before (always creates).

    Not a distributed lock: two requests with the same key arriving within
    the same few milliseconds could both miss the cache and both create —
    an accepted, documented tradeoff for this P3-severity finding, not a
    guarantee against true concurrent duplicate submission.
    """
    if not idempotency_key:
        return create()
    safe_key = idempotency_key.strip()[:MAX_IDEMPOTENCY_KEY_LENGTH]
    if not safe_key:
        return create()
    cache_key = f"idempotency:{scope}:{user_id}:{safe_key}"
    return dict(
        cache.get_or_set_json(cache_key, IDEMPOTENCY_KEY_TTL_SECONDS, create)
    )

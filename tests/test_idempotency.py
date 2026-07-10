"""Idempotency-Key replay for the most sensitive create endpoints (P3-4, Аудит-эпизод 10)."""

from app.services.idempotency import with_idempotency_key
from tests.cache_test_helpers import FakeCacheBackend as _FakeCache


def test_without_key_always_creates() -> None:
    cache = _FakeCache()
    calls = []

    def create() -> dict[str, str]:
        calls.append(1)
        return {"id": f"item-{len(calls)}"}

    first = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key=None,
        create=create,
    )
    second = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key=None,
        create=create,
    )

    assert first == {"id": "item-1"}
    assert second == {"id": "item-2"}
    assert len(calls) == 2


def test_repeated_key_replays_the_cached_response() -> None:
    cache = _FakeCache()
    calls = []

    def create() -> dict[str, str]:
        calls.append(1)
        return {"id": f"item-{len(calls)}"}

    first = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key="retry-1",
        create=create,
    )
    second = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key="retry-1",
        create=create,
    )

    assert first == second == {"id": "item-1"}
    assert len(calls) == 1


def test_same_key_different_users_do_not_collide() -> None:
    cache = _FakeCache()
    calls = []

    def create() -> dict[str, str]:
        calls.append(1)
        return {"id": f"item-{len(calls)}"}

    first = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key="same-key",
        create=create,
    )
    second = with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-2",
        idempotency_key="same-key",
        create=create,
    )

    assert first != second
    assert len(calls) == 2


def test_same_key_different_scope_do_not_collide() -> None:
    cache = _FakeCache()
    calls = []

    def create() -> dict[str, str]:
        calls.append(1)
        return {"id": f"item-{len(calls)}"}

    first = with_idempotency_key(
        cache,
        scope="scope_a",
        user_id="user-1",
        idempotency_key="same-key",
        create=create,
    )
    second = with_idempotency_key(
        cache,
        scope="scope_b",
        user_id="user-1",
        idempotency_key="same-key",
        create=create,
    )

    assert first != second
    assert len(calls) == 2


def test_blank_key_is_treated_as_no_key() -> None:
    cache = _FakeCache()
    calls = []

    def create() -> dict[str, str]:
        calls.append(1)
        return {"id": f"item-{len(calls)}"}

    with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key="   ",
        create=create,
    )
    with_idempotency_key(
        cache,
        scope="thing_create",
        user_id="user-1",
        idempotency_key="   ",
        create=create,
    )

    assert len(calls) == 2

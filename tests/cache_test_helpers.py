"""In-memory CacheBackend test double (see app.services.cache.CacheBackend)."""


class FakeCacheBackend:
    def __init__(self) -> None:
        self.store: dict[str, object] = {}

    def get_json(self, key: str) -> object | None:
        return self.store.get(key)

    def set_json(self, key: str, value: object, _ttl_seconds: int) -> None:
        self.store[key] = value

    def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def delete_by_prefix(self, prefix: str) -> None:
        for key in list(self.store):
            if key.startswith(prefix):
                del self.store[key]

    def get_or_set_json(
        self, key: str, _ttl_seconds: int, loader: object
    ) -> object:
        if key in self.store:
            return self.store[key]
        value = loader()  # type: ignore[operator]
        self.store[key] = value
        return value

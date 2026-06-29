from app.services.cache import CacheBackend, get_cache_backend


def invalidate_country_cache(
    country_slug: str, cache: CacheBackend | None = None
) -> None:
    backend = cache or get_cache_backend()
    backend.delete_by_prefix(f"v1:country:{country_slug}:")
    backend.delete_by_prefix("v1:countries:matrix:")


def invalidate_home_cache(cache: CacheBackend | None = None) -> None:
    backend = cache or get_cache_backend()
    backend.delete_by_prefix("v1:home:overview:")


def invalidate_routes_cache(
    country_slug: str, cache: CacheBackend | None = None
) -> None:
    backend = cache or get_cache_backend()
    backend.delete_by_prefix(f"v1:routes:{country_slug}:")


def invalidate_legal_timeline_cache(
    country_slug: str, cache: CacheBackend | None = None
) -> None:
    backend = cache or get_cache_backend()
    backend.delete_by_prefix(f"v1:timeline:{country_slug}:")
    backend.delete_by_prefix("v1:timeline:all:")


def invalidate_platform_read_cache(
    country_slug: str | None = None, cache: CacheBackend | None = None
) -> None:
    backend = cache or get_cache_backend()
    invalidate_home_cache(backend)
    backend.delete_by_prefix("v1:countries:matrix:")
    if country_slug is not None:
        invalidate_country_cache(country_slug, backend)
        invalidate_routes_cache(country_slug, backend)
        invalidate_legal_timeline_cache(country_slug, backend)

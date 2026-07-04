import hashlib
import json
from collections.abc import Mapping
from typing import Any


FORBIDDEN_KEY_PARTS = {
    "session",
    "session_id",
    "session_hash",
    "user",
    "user_id",
    "admin_token",
    "token",
}


def cache_key(*parts: str, **params: Any) -> str:
    normalized = [part.strip(":") for part in parts if part]
    for key, value in sorted(params.items()):
        if value is None or value == "":
            continue
        _ensure_safe_key_part(key)
        normalized.append(f"{key}={_safe_value(value)}")
    return ":".join(normalized)


def filter_hash(filters: Mapping[str, Any]) -> str:
    public_filters = {
        key: value
        for key, value in filters.items()
        if value is not None and value != "" and key not in FORBIDDEN_KEY_PARTS
    }
    encoded = json.dumps(public_filters, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def home_overview_key(locale: str) -> str:
    return cache_key("v1", "home", "overview", locale=locale)


def country_card_key(country_slug: str, locale: str) -> str:
    return cache_key("v1", "country", country_slug, "card", locale=locale)


def countries_matrix_key(
    locale: str,
    country_slugs: list[str] | None,
    scenario_slugs: list[str] | None,
) -> str:
    return cache_key(
        "v1",
        "countries",
        "matrix",
        locale=locale,
        filters=filter_hash(
            {
                "countries": country_slugs or [],
                "scenarios": scenario_slugs or [],
            }
        ),
    )


def legal_timeline_key(
    country_slug: str | None, locale: str, filters: Mapping[str, Any]
) -> str:
    return cache_key(
        "v1",
        "timeline",
        country_slug or "all",
        locale=locale,
        filters=filter_hash(filters),
    )


def routes_key(
    country_slug: str, locale: str, filters: Mapping[str, Any]
) -> str:
    return cache_key(
        "v1",
        "routes",
        country_slug,
        locale=locale,
        filters=filter_hash(filters),
    )


def _safe_value(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return text.strip('"').replace(":", "_").replace(" ", "_")[:96]


def _ensure_safe_key_part(key: str) -> None:
    lowered = key.lower()
    if lowered in FORBIDDEN_KEY_PARTS:
        raise ValueError("Unsafe cache key parameter.")

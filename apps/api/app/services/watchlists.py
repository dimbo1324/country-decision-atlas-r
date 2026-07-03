from app.core.errors import api_error
from app.repositories import countries as countries_repository, watchlists as repository
from app.services.feature_flags import is_feature_enabled_by_key
from psycopg import Connection
from typing import Any


WATCHLIST_FEATURE_KEY = "web_watchlist_enabled"
NOTES_MAX_LENGTH = 2000


def require_watchlist_enabled(connection: Connection[Any]) -> None:
    if not is_feature_enabled_by_key(connection, WATCHLIST_FEATURE_KEY):
        raise api_error(
            403, "feature_disabled", "The watchlist feature is currently disabled.", {}
        )


def _get_country_or_404(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any]:
    country = countries_repository.get_active_country_by_slug(connection, country_slug)
    if country is None:
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {"country_slug": country_slug},
        )
    return country


def list_user_watchlist(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    require_watchlist_enabled(connection)
    return repository.list_user_watchlist(connection, user_id)


def add_country_to_watchlist(
    connection: Connection[Any], *, user_id: str, country_slug: str
) -> dict[str, Any]:
    require_watchlist_enabled(connection)
    country = _get_country_or_404(connection, country_slug)
    repository.add_country_to_watchlist(
        connection, user_id=user_id, country_id=country["id"], created_source="web"
    )
    item = repository.get_user_watchlist_item_by_country_slug(
        connection, user_id, country_slug
    )
    assert item is not None
    return item


def remove_country_from_watchlist(
    connection: Connection[Any], *, user_id: str, country_slug: str
) -> None:
    require_watchlist_enabled(connection)
    country = _get_country_or_404(connection, country_slug)
    repository.archive_country_from_watchlist(
        connection, user_id=user_id, country_id=country["id"]
    )


def update_watchlist_preferences(
    connection: Connection[Any],
    *,
    user_id: str,
    country_slug: str,
    notify_legal_signals: bool | None,
    notify_drift_changes: bool | None,
    notify_route_updates: bool | None,
    notes: str | None,
    notes_provided: bool,
) -> dict[str, Any]:
    require_watchlist_enabled(connection)
    if notes is not None and len(notes) > NOTES_MAX_LENGTH:
        raise api_error(
            422,
            "notes_too_long",
            f"Notes must be at most {NOTES_MAX_LENGTH} characters.",
            {"max_length": NOTES_MAX_LENGTH},
        )
    country = _get_country_or_404(connection, country_slug)
    updated = repository.update_watchlist_preferences(
        connection,
        user_id=user_id,
        country_id=country["id"],
        notify_legal_signals=notify_legal_signals,
        notify_drift_changes=notify_drift_changes,
        notify_route_updates=notify_route_updates,
        notes=notes,
        notes_provided=notes_provided,
    )
    if updated is None:
        raise api_error(
            404,
            "watchlist_item_not_found",
            "This country is not on your watchlist.",
            {"country_slug": country_slug},
        )
    item = repository.get_user_watchlist_item_by_country_slug(
        connection, user_id, country_slug
    )
    assert item is not None
    return item


def get_watchlist_status(
    connection: Connection[Any], *, user_id: str, country_slug: str
) -> bool:
    require_watchlist_enabled(connection)
    country = _get_country_or_404(connection, country_slug)
    return repository.get_watchlist_status_for_country(
        connection, user_id, country["id"]
    )

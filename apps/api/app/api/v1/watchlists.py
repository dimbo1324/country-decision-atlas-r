from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.schemas.watchlists import (
    WatchlistItem,
    WatchlistPreferencesUpdateRequest,
    WatchlistResponse,
    WatchlistStatusResponse,
)
from app.services import watchlists as service
from fastapi import APIRouter, Depends
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["watchlists"])


def _to_watchlist_item(row: dict[str, Any]) -> WatchlistItem:
    return WatchlistItem(
        id=row["id"],
        country_slug=row["country_slug"],
        country_name=row["country_name"],
        status=row["status"],
        notify_legal_signals=row["notify_legal_signals"],
        notify_drift_changes=row["notify_drift_changes"],
        notify_route_updates=row["notify_route_updates"],
        notes=row["notes"],
        created_source=row["created_source"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("/me/watchlist", response_model=WatchlistResponse)
def get_my_watchlist(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> WatchlistResponse:
    items = service.list_user_watchlist(connection, current_user.id)
    return WatchlistResponse(
        total=len(items), items=[_to_watchlist_item(row) for row in items]
    )


@router.post(
    "/me/watchlist/countries/{country_slug}",
    response_model=WatchlistItem,
    status_code=201,
)
def add_country_to_watchlist(
    country_slug: str,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> WatchlistItem:
    item = service.add_country_to_watchlist(
        connection, user_id=current_user.id, country_slug=country_slug
    )
    connection.commit()
    return _to_watchlist_item(item)


@router.delete("/me/watchlist/countries/{country_slug}", status_code=204)
def remove_country_from_watchlist(
    country_slug: str,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.remove_country_from_watchlist(
        connection, user_id=current_user.id, country_slug=country_slug
    )
    connection.commit()


@router.patch(
    "/me/watchlist/countries/{country_slug}",
    response_model=WatchlistItem,
)
def update_watchlist_preferences(
    country_slug: str,
    payload: WatchlistPreferencesUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> WatchlistItem:
    item = service.update_watchlist_preferences(
        connection,
        user_id=current_user.id,
        country_slug=country_slug,
        notify_legal_signals=payload.notify_legal_signals,
        notify_drift_changes=payload.notify_drift_changes,
        notify_route_updates=payload.notify_route_updates,
        notes=payload.notes,
        notes_provided="notes" in payload.model_fields_set,
    )
    connection.commit()
    return _to_watchlist_item(item)


@router.get(
    "/countries/{country_slug}/watchlist-status",
    response_model=WatchlistStatusResponse,
)
def get_country_watchlist_status(
    country_slug: str,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> WatchlistStatusResponse:
    saved = service.get_watchlist_status(
        connection, user_id=current_user.id, country_slug=country_slug
    )
    return WatchlistStatusResponse(country_slug=country_slug, saved=saved)

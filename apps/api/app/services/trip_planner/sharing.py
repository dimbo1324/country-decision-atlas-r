import hashlib
import secrets
from app.core.errors import api_error
from app.repositories import trip_planner as repository
from app.schemas.trip_planner import (
    SharedTripChecklistItem,
    SharedTripResponse,
    SharedTripWaypoint,
    TripShareResponse,
)
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


def enable_share(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> TripShareResponse:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)
    row = repository.enable_trip_share(
        connection,
        trip_id=trip_id,
        user_id=user_id,
        token_hash=token_hash,
        token_prefix=token[:8],
    )
    if row is None:
        raise api_error(404, "trip_not_found", "Trip was not found.", {})
    return TripShareResponse(
        trip_id=trip_id,
        token=token,
        path=f"{helpers.TRIP_SHARE_PATH_PREFIX}/{token}",
        visibility=row["visibility"],
    )


def disable_share(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> None:
    helpers.require_trip_planner_enabled(connection)
    if (
        repository.disable_trip_share(
            connection, trip_id=trip_id, user_id=user_id
        )
        is None
    ):
        raise api_error(404, "trip_not_found", "Trip was not found.", {})


def get_shared_trip(
    connection: Connection[Any], *, token: str
) -> SharedTripResponse:
    helpers.require_trip_planner_enabled(connection)
    trip = repository.get_trip_by_share_token_hash(
        connection, _hash_token(token)
    )
    if trip is None:
        raise api_error(
            404, "shared_trip_not_found", "Shared trip was not found.", {}
        )
    waypoints = repository.list_waypoints(connection, trip["id"])
    checklist = repository.list_checklist_items(connection, trip["id"])
    return SharedTripResponse(
        id=trip["id"],
        title=trip["title"],
        scenario_slug=trip.get("scenario_slug"),
        origin_country=helpers.trip_summary(trip).origin_country,
        status=trip["status"],
        confidence_tier=trip["confidence_tier"],
        waypoints=[
            SharedTripWaypoint(
                position=row["position"],
                country=helpers.waypoint_model(row).country,
                city=row.get("city"),
                kind=row["kind"],
                planned_from=row.get("planned_from"),
                planned_to=row.get("planned_to"),
            )
            for row in waypoints
        ],
        checklist_items=[
            SharedTripChecklistItem(
                title=row["title"],
                due_date=row.get("due_date"),
                status=row["status"],
                position=row["position"],
            )
            for row in checklist
        ],
        updated_at=trip["updated_at"],
    )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

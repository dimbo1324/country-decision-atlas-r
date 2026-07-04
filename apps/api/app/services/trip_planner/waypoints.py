from app.core.errors import api_error
from app.repositories import trip_planner as repository
from app.schemas.trip_planner import (
    TripWaypoint,
    TripWaypointCreateRequest,
    TripWaypointKind,
    TripWaypointReorderRequest,
    TripWaypointUpdateRequest,
)
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


def list_waypoints(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> list[TripWaypoint]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    return [
        helpers.waypoint_model(row)
        for row in repository.list_waypoints(connection, trip_id)
    ]


def create_waypoint(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripWaypointCreateRequest,
) -> TripWaypoint:
    return create_waypoint_from_country_slug(
        connection,
        user_id=user_id,
        trip_id=trip_id,
        country_slug=payload.country_slug,
        city=payload.city,
        kind=payload.kind,
        planned_from=payload.planned_from,
        planned_to=payload.planned_to,
        notes=payload.notes,
        position=payload.position,
    )


def create_waypoint_from_country_slug(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    country_slug: str,
    city: str | None = None,
    kind: TripWaypointKind = "destination",
    planned_from: Any | None = None,
    planned_to: Any | None = None,
    notes: str | None = None,
    position: int | None = None,
) -> TripWaypoint:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    helpers.validate_date_range(planned_from, planned_to)
    country = helpers.country_by_slug_or_404(connection, country_slug)
    resolved_position = position or repository.next_waypoint_position(
        connection, trip_id
    )
    row = repository.create_waypoint(
        connection,
        trip_id=trip_id,
        position=resolved_position,
        country_id=country["id"],
        city=city,
        kind=kind,
        planned_from=planned_from,
        planned_to=planned_to,
        notes=notes,
    )
    helpers.sync_trip_countries_to_watchlist(
        connection, user_id=user_id, trip_id=trip_id
    )
    return helpers.waypoint_model(row)


def update_waypoint(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    waypoint_id: str,
    payload: TripWaypointUpdateRequest,
) -> TripWaypoint:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    current = repository.get_waypoint_for_trip(
        connection, trip_id=trip_id, waypoint_id=waypoint_id
    )
    if current is None:
        raise api_error(
            404, "waypoint_not_found", "Trip waypoint was not found.", {}
        )
    planned_from = (
        payload.planned_from
        if "planned_from" in payload.model_fields_set
        else current.get("planned_from")
    )
    planned_to = (
        payload.planned_to
        if "planned_to" in payload.model_fields_set
        else current.get("planned_to")
    )
    helpers.validate_date_range(planned_from, planned_to)
    country_id = current["country_id"]
    if payload.country_slug is not None:
        country_id = helpers.country_by_slug_or_404(
            connection, payload.country_slug
        )["id"]
    row = repository.update_waypoint(
        connection,
        waypoint_id=waypoint_id,
        trip_id=trip_id,
        position=payload.position or current["position"],
        country_id=country_id,
        city=payload.city
        if "city" in payload.model_fields_set
        else current.get("city"),
        kind=payload.kind or current["kind"],
        planned_from=planned_from,
        planned_to=planned_to,
        notes=payload.notes
        if "notes" in payload.model_fields_set
        else current.get("notes"),
    )
    if row is None:
        raise api_error(
            404, "waypoint_not_found", "Trip waypoint was not found.", {}
        )
    helpers.sync_trip_countries_to_watchlist(
        connection, user_id=user_id, trip_id=trip_id
    )
    return helpers.waypoint_model(row)


def delete_waypoint(
    connection: Connection[Any], *, user_id: str, trip_id: str, waypoint_id: str
) -> None:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    if not repository.delete_waypoint(
        connection, trip_id=trip_id, waypoint_id=waypoint_id
    ):
        raise api_error(
            404, "waypoint_not_found", "Trip waypoint was not found.", {}
        )


def reorder_waypoints(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripWaypointReorderRequest,
) -> list[TripWaypoint]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    current_ids = {
        row["id"] for row in repository.list_waypoints(connection, trip_id)
    }
    requested = list(dict.fromkeys(payload.waypoint_ids))
    if set(requested) != current_ids:
        raise api_error(
            422,
            "waypoint_reorder_mismatch",
            "Reorder payload must include every waypoint exactly once.",
            {},
        )
    for index, item_id in enumerate(requested, start=1):
        repository.set_waypoint_position(
            connection,
            waypoint_id=item_id,
            trip_id=trip_id,
            position=index,
        )
    return list_waypoints(connection, user_id=user_id, trip_id=trip_id)

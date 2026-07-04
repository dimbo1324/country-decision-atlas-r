from app.core.errors import api_error
from app.repositories import route_checklists, trip_planner as repository
from app.schemas.trip_planner import (
    TripChecklistImportRequest,
    TripChecklistItem,
    TripChecklistItemCreateRequest,
    TripChecklistItemUpdateRequest,
)
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


def list_checklist_items(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> list[TripChecklistItem]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    return [
        helpers.checklist_item_model(row)
        for row in repository.list_checklist_items(connection, trip_id)
    ]


def create_checklist_item(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripChecklistItemCreateRequest,
) -> TripChecklistItem:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    _validate_waypoint(connection, trip_id, payload.waypoint_id)
    row = repository.create_checklist_item(
        connection,
        trip_id=trip_id,
        waypoint_id=payload.waypoint_id,
        title=payload.title.strip(),
        description=payload.description,
        due_date=payload.due_date,
        status=payload.status,
        origin_kind="manual",
        origin_ref=None,
        position=payload.position
        or repository.next_checklist_position(connection, trip_id),
    )
    return helpers.checklist_item_model(row)


def update_checklist_item(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    item_id: str,
    payload: TripChecklistItemUpdateRequest,
) -> TripChecklistItem:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    current = repository.get_checklist_item_for_trip(
        connection, trip_id=trip_id, item_id=item_id
    )
    if current is None:
        raise api_error(
            404,
            "checklist_item_not_found",
            "Trip checklist item was not found.",
            {},
        )
    waypoint_id = (
        payload.waypoint_id
        if "waypoint_id" in payload.model_fields_set
        else current.get("waypoint_id")
    )
    _validate_waypoint(connection, trip_id, waypoint_id)
    row = repository.update_checklist_item(
        connection,
        item_id=item_id,
        trip_id=trip_id,
        waypoint_id=waypoint_id,
        title=payload.title.strip()
        if payload.title is not None
        else current["title"],
        description=payload.description
        if "description" in payload.model_fields_set
        else current.get("description"),
        due_date=payload.due_date
        if "due_date" in payload.model_fields_set
        else current.get("due_date"),
        status=payload.status or current["status"],
        position=payload.position or current["position"],
    )
    if row is None:
        raise api_error(
            404,
            "checklist_item_not_found",
            "Trip checklist item was not found.",
            {},
        )
    return helpers.checklist_item_model(row)


def delete_checklist_item(
    connection: Connection[Any], *, user_id: str, trip_id: str, item_id: str
) -> None:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    if not repository.delete_checklist_item(
        connection, trip_id=trip_id, item_id=item_id
    ):
        raise api_error(
            404,
            "checklist_item_not_found",
            "Trip checklist item was not found.",
            {},
        )


def import_route_checklist(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripChecklistImportRequest,
) -> list[TripChecklistItem]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    rows = route_checklists.list_route_checklist_items(
        connection, payload.route_id, "en"
    )
    position = repository.next_checklist_position(connection, trip_id)
    imported = []
    for row in rows:
        imported.append(
            repository.create_checklist_item(
                connection,
                trip_id=trip_id,
                waypoint_id=None,
                title=row["title"],
                description=row.get("description"),
                due_date=None,
                status="todo",
                origin_kind="route_template",
                origin_ref=row["id"],
                position=position,
            )
        )
        position += 1
    return [helpers.checklist_item_model(row) for row in imported]


def _validate_waypoint(
    connection: Connection[Any], trip_id: str, waypoint_id: str | None
) -> None:
    if waypoint_id is None:
        return
    if (
        repository.get_waypoint_for_trip(
            connection, trip_id=trip_id, waypoint_id=waypoint_id
        )
        is None
    ):
        raise api_error(
            422,
            "waypoint_not_in_trip",
            "Checklist waypoint must belong to this trip.",
            {},
        )

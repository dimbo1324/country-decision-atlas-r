from app.core.errors import api_error
from app.repositories import trip_planner as repository
from app.schemas.trip_planner import (
    TripAnnotation,
    TripAnnotationCreateRequest,
    TripAnnotationUpdateRequest,
)
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


def list_annotations(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> list[TripAnnotation]:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    return [
        helpers.annotation_model(row)
        for row in repository.list_annotations(connection, trip_id)
    ]


def create_annotation(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripAnnotationCreateRequest,
) -> TripAnnotation:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    _validate_waypoint(connection, trip_id, payload.waypoint_id)
    row = repository.create_annotation(
        connection,
        trip_id=trip_id,
        waypoint_id=payload.waypoint_id,
        kind=payload.kind,
        body=payload.body.strip(),
        position=payload.position,
    )
    return helpers.annotation_model(row)


def update_annotation(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    annotation_id: str,
    payload: TripAnnotationUpdateRequest,
) -> TripAnnotation:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    current = repository.get_annotation_for_trip(
        connection, trip_id=trip_id, annotation_id=annotation_id
    )
    if current is None:
        raise api_error(
            404, "annotation_not_found", "Trip annotation was not found.", {}
        )
    waypoint_id = (
        payload.waypoint_id
        if "waypoint_id" in payload.model_fields_set
        else current.get("waypoint_id")
    )
    _validate_waypoint(connection, trip_id, waypoint_id)
    row = repository.update_annotation(
        connection,
        annotation_id=annotation_id,
        trip_id=trip_id,
        waypoint_id=waypoint_id,
        kind=payload.kind or current["kind"],
        body=payload.body.strip()
        if payload.body is not None
        else current["body"],
        position=payload.position
        if "position" in payload.model_fields_set
        else current.get("position"),
    )
    if row is None:
        raise api_error(
            404, "annotation_not_found", "Trip annotation was not found.", {}
        )
    return helpers.annotation_model(row)


def delete_annotation(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    annotation_id: str,
) -> None:
    helpers.require_trip_planner_enabled(connection)
    helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    if not repository.delete_annotation(
        connection, trip_id=trip_id, annotation_id=annotation_id
    ):
        raise api_error(
            404, "annotation_not_found", "Trip annotation was not found.", {}
        )


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
            "Annotation waypoint must belong to this trip.",
            {},
        )

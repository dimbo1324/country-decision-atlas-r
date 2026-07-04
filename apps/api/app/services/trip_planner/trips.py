from app.core.errors import api_error
from app.repositories import (
    decision_passports as passport_repository,
    trip_planner as repository,
)
from app.schemas.trip_planner import (
    TripCreateFromPassportRequest,
    TripCreateRequest,
    TripDetail,
    TripSummary,
    TripUpdateRequest,
)
from app.services.decision_passports import _hash_token
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


def list_user_trips(
    connection: Connection[Any], user_id: str
) -> list[TripSummary]:
    helpers.require_trip_planner_enabled(connection)
    return [
        helpers.trip_summary(row)
        for row in repository.list_user_trips(connection, user_id)
    ]


def get_user_trip(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> TripDetail:
    helpers.require_trip_planner_enabled(connection)
    trip = helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    return _detail(connection, trip)


def create_user_trip(
    connection: Connection[Any], *, user_id: str, payload: TripCreateRequest
) -> TripDetail:
    helpers.require_trip_planner_enabled(connection)
    helpers.validate_scenario(connection, payload.scenario_slug)
    origin_country_id = None
    if payload.origin_country_slug:
        origin_country_id = helpers.country_by_slug_or_404(
            connection, payload.origin_country_slug, "origin_country_slug"
        )["id"]
    trip = repository.create_trip(
        connection,
        user_id=user_id,
        title=payload.title.strip(),
        scenario_slug=payload.scenario_slug,
        origin_country_id=origin_country_id,
        status=payload.status,
    )
    helpers.sync_trip_countries_to_watchlist(
        connection, user_id=user_id, trip_id=trip["id"]
    )
    return _detail(connection, trip)


def update_user_trip(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    payload: TripUpdateRequest,
) -> TripDetail:
    helpers.require_trip_planner_enabled(connection)
    current = helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    title = (
        payload.title.strip()
        if payload.title is not None
        else str(current["title"])
    )
    scenario_slug = (
        payload.scenario_slug
        if "scenario_slug" in payload.model_fields_set
        else current.get("scenario_slug")
    )
    helpers.validate_scenario(connection, scenario_slug)
    if "origin_country_slug" in payload.model_fields_set:
        origin_country_id = (
            helpers.country_by_slug_or_404(
                connection,
                payload.origin_country_slug,
                "origin_country_slug",
            )["id"]
            if payload.origin_country_slug is not None
            else None
        )
    else:
        origin_country_id = current.get("origin_country_id")
    status = payload.status or current["status"]
    confidence_tier = payload.confidence_tier or current["confidence_tier"]
    if status == "completed":
        confidence_tier = "confirmed"
    completed_at = helpers.completed_at_for_status(
        status, current.get("completed_at")
    )
    updated = repository.update_trip(
        connection,
        trip_id=trip_id,
        user_id=user_id,
        title=title,
        scenario_slug=scenario_slug,
        origin_country_id=origin_country_id,
        status=status,
        confidence_tier=confidence_tier,
        completed_at=completed_at,
    )
    if updated is None:
        raise api_error(404, "trip_not_found", "Trip was not found.", {})
    helpers.sync_trip_countries_to_watchlist(
        connection, user_id=user_id, trip_id=trip_id
    )
    return _detail(connection, updated)


def delete_user_trip(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> None:
    helpers.require_trip_planner_enabled(connection)
    if not repository.delete_trip(connection, trip_id=trip_id, user_id=user_id):
        raise api_error(404, "trip_not_found", "Trip was not found.", {})


def create_trip_from_passport(
    connection: Connection[Any],
    *,
    user_id: str,
    payload: TripCreateFromPassportRequest,
) -> TripDetail:
    helpers.require_trip_planner_enabled(connection)
    passport = passport_repository.get_decision_passport_by_token_hash(
        connection, _hash_token(payload.token)
    )
    if passport is None:
        raise api_error(
            404,
            "decision_passport_not_found",
            "Decision passport was not found.",
            {},
        )
    selected_slug = passport.get("selected_country_slug")
    if not selected_slug:
        raise api_error(
            422,
            "passport_has_no_selected_country",
            "Decision passport has no selected country.",
            {},
        )
    title = payload.title or f"Move to {selected_slug.title()}"
    trip = create_user_trip(
        connection,
        user_id=user_id,
        payload=TripCreateRequest(
            title=title,
            scenario_slug=passport.get("scenario_slug"),
            origin_country_slug=passport.get("origin_country_slug"),
            status="draft",
        ),
    )
    from app.services.trip_planner import waypoints

    waypoints.create_waypoint_from_country_slug(
        connection,
        user_id=user_id,
        trip_id=trip.id,
        country_slug=selected_slug,
        kind="destination",
    )
    return get_user_trip(connection, user_id=user_id, trip_id=trip.id)


def _detail(connection: Connection[Any], trip: dict[str, Any]) -> TripDetail:
    trip_id = trip["id"]
    return helpers.trip_detail(
        trip,
        repository.list_waypoints(connection, trip_id),
        repository.list_checklist_items(connection, trip_id),
        repository.list_reminders(connection, trip_id),
        repository.list_annotations(connection, trip_id),
    )

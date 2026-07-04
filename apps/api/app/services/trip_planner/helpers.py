from app.core.errors import api_error
from app.repositories import (
    countries as countries_repository,
    trip_planner as repository,
    watchlists as watchlists_repository,
    weight_profiles as weight_profiles_repository,
)
from app.schemas.trip_planner import (
    TripAnnotation,
    TripChecklistItem,
    TripCountryRef,
    TripDetail,
    TripReminder,
    TripSummary,
    TripWaypoint,
)
from app.services.feature_flags import ensure_feature_enabled
from datetime import UTC, date, datetime
from psycopg import Connection
from typing import Any


TRIP_PLANNER_FEATURE_KEY = "trip_planner_enabled"
TRIP_SHARE_PATH_PREFIX = "/trips/shared"


def require_trip_planner_enabled(connection: Connection[Any]) -> None:
    ensure_feature_enabled(
        connection,
        TRIP_PLANNER_FEATURE_KEY,
        "The trip planner feature is currently disabled.",
    )


def get_owned_trip_or_404(
    connection: Connection[Any], trip_id: str, user_id: str
) -> dict[str, Any]:
    trip = repository.get_trip_for_user(connection, trip_id, user_id)
    if trip is None:
        raise api_error(404, "trip_not_found", "Trip was not found.", {})
    return trip


def country_by_slug_or_404(
    connection: Connection[Any], country_slug: str, field: str = "country_slug"
) -> dict[str, Any]:
    country = countries_repository.get_active_country_by_slug(
        connection, country_slug
    )
    if country is None:
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {field: country_slug},
        )
    return country


def validate_scenario(
    connection: Connection[Any], scenario_slug: str | None
) -> None:
    if scenario_slug is None:
        return
    if not weight_profiles_repository.scenario_exists(
        connection, scenario_slug
    ):
        raise api_error(
            404,
            "scenario_not_found",
            "Scenario was not found.",
            {"scenario_slug": scenario_slug},
        )


def validate_date_range(
    planned_from: date | None, planned_to: date | None
) -> None:
    if (
        planned_from is not None
        and planned_to is not None
        and planned_from > planned_to
    ):
        raise api_error(
            422,
            "invalid_waypoint_dates",
            "Waypoint start date must be before or equal to end date.",
            {},
        )


def completed_at_for_status(
    status: str, current_completed_at: datetime | None
) -> datetime | None:
    if status == "completed":
        return current_completed_at or datetime.now(UTC)
    return None


def sync_trip_countries_to_watchlist(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> None:
    trip = repository.get_trip_for_user(connection, trip_id, user_id)
    if trip is None:
        return
    country_ids: list[str] = []
    if trip.get("origin_country_id"):
        country_ids.append(str(trip["origin_country_id"]))
    country_ids.extend(
        str(row["country_id"])
        for row in repository.list_waypoints(connection, trip_id)
    )
    for country_id in dict.fromkeys(country_ids):
        watchlists_repository.add_country_to_watchlist(
            connection,
            user_id=user_id,
            country_id=country_id,
            created_source="web",
        )


def trip_summary(row: dict[str, Any]) -> TripSummary:
    return TripSummary(
        id=row["id"],
        title=row["title"],
        scenario_slug=row.get("scenario_slug"),
        origin_country=_origin_country(row),
        status=row["status"],
        confidence_tier=row["confidence_tier"],
        visibility=row["visibility"],
        share_token_prefix=row.get("share_token_prefix"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row.get("completed_at"),
    )


def trip_detail(
    trip: dict[str, Any],
    waypoints: list[dict[str, Any]],
    checklist_items: list[dict[str, Any]],
    reminders: list[dict[str, Any]],
    annotations: list[dict[str, Any]],
) -> TripDetail:
    return TripDetail(
        **trip_summary(trip).model_dump(),
        waypoints=[waypoint_model(row) for row in waypoints],
        checklist_items=[checklist_item_model(row) for row in checklist_items],
        reminders=[reminder_model(row) for row in reminders],
        annotations=[annotation_model(row) for row in annotations],
    )


def waypoint_model(row: dict[str, Any]) -> TripWaypoint:
    return TripWaypoint(
        id=row["id"],
        position=row["position"],
        country=TripCountryRef(
            id=row["country_id"],
            slug=row["country_slug"],
            name=row["country_name"],
            iso2=row.get("country_iso2"),
        ),
        city=row.get("city"),
        kind=row["kind"],
        planned_from=row.get("planned_from"),
        planned_to=row.get("planned_to"),
        notes=row.get("notes"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def checklist_item_model(row: dict[str, Any]) -> TripChecklistItem:
    return TripChecklistItem(
        id=row["id"],
        waypoint_id=row.get("waypoint_id"),
        title=row["title"],
        description=row.get("description"),
        due_date=row.get("due_date"),
        status=row["status"],
        origin_kind=row["origin_kind"],
        origin_ref=row.get("origin_ref"),
        position=row["position"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def reminder_model(row: dict[str, Any]) -> TripReminder:
    return TripReminder(
        id=row["id"],
        checklist_item_id=row.get("checklist_item_id"),
        checklist_item_title=row.get("checklist_item_title"),
        remind_at=row["remind_at"],
        channel=row["channel"],
        status=row["status"],
        sent_at=row.get("sent_at"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def annotation_model(row: dict[str, Any]) -> TripAnnotation:
    return TripAnnotation(
        id=row["id"],
        waypoint_id=row.get("waypoint_id"),
        kind=row["kind"],
        body=row["body"],
        position=row.get("position"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _origin_country(row: dict[str, Any]) -> TripCountryRef | None:
    if not row.get("origin_country_slug"):
        return None
    return TripCountryRef(
        id=row.get("origin_country_id"),
        slug=row["origin_country_slug"],
        name=row["origin_country_name"],
    )

import json
from app.repositories import trip_planner as repository
from app.services.trip_planner import helpers
from datetime import UTC, date, datetime
from psycopg import Connection
from typing import Any


def export_trip(
    connection: Connection[Any],
    *,
    user_id: str,
    trip_id: str,
    export_format: str,
) -> tuple[str, str, str]:
    helpers.require_trip_planner_enabled(connection)
    trip = helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    detail = helpers.trip_detail(
        trip,
        repository.list_waypoints(connection, trip_id),
        repository.list_checklist_items(connection, trip_id),
        repository.list_reminders(connection, trip_id),
        repository.list_annotations(connection, trip_id),
    )
    if export_format == "json":
        return (
            json.dumps(detail.model_dump(mode="json"), indent=2),
            "application/json",
            f"trip-{trip_id}.json",
        )
    if export_format == "ics":
        return (
            _ics(detail.model_dump(mode="json")),
            "text/calendar; charset=utf-8",
            f"trip-{trip_id}.ics",
        )
    if export_format == "geojson":
        return (
            _geojson(detail.model_dump(mode="json")),
            "application/geo+json",
            f"trip-{trip_id}.geojson",
        )
    raise ValueError(f"Unsupported trip export format: {export_format}")


def _ics(data: dict[str, Any]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Country Decision Atlas//Trip Planner//EN",
    ]
    for item in data["checklist_items"]:
        due_date = item.get("due_date")
        if not due_date:
            continue
        uid = f"trip-{data['id']}-checklist-{item['id']}@country-decision-atlas"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{_escape_ics(uid)}",
                f"DTSTAMP:{_dtstamp()}",
                f"DTSTART;VALUE=DATE:{_date_value(due_date)}",
                f"SUMMARY:{_escape_ics(item['title'])}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def _geojson(data: dict[str, Any]) -> str:
    features = []
    for waypoint in data["waypoints"]:
        features.append(
            {
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "position": waypoint["position"],
                    "country_slug": waypoint["country"]["slug"],
                    "country_name": waypoint["country"]["name"],
                    "city": waypoint.get("city"),
                    "kind": waypoint["kind"],
                    "planned_from": waypoint.get("planned_from"),
                    "planned_to": waypoint.get("planned_to"),
                },
            }
        )
    return json.dumps(
        {"type": "FeatureCollection", "features": features},
        indent=2,
        default=str,
    )


def _escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _dtstamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _date_value(value: str | date) -> str:
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    return value.replace("-", "")

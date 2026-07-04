from app.repositories import country_pairs, trip_planner as repository
from app.schemas.trip_planner import TripWarning, TripWarningsResponse
from app.services.methodology_config import get_active_methodology_config
from app.services.trip_planner import helpers
from psycopg import Connection
from typing import Any


SEVERITY_BY_RANK = {
    1: "low",
    2: "medium",
    3: "high",
    4: "critical",
}

IMPACT_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def build_trip_warnings(
    connection: Connection[Any], *, user_id: str, trip_id: str
) -> TripWarningsResponse:
    helpers.require_trip_planner_enabled(connection)
    trip = helpers.get_owned_trip_or_404(connection, trip_id, user_id)
    waypoints = repository.list_waypoints(connection, trip_id)
    methodology = get_active_methodology_config(connection)
    warnings = [
        *_pair_warnings(connection, trip, waypoints, methodology),
        *_legal_signal_warnings(connection, waypoints, methodology),
    ]
    return TripWarningsResponse(
        trip_id=trip_id,
        methodology_version=methodology.version,
        items=warnings,
    )


def _pair_warnings(
    connection: Connection[Any],
    trip: dict[str, Any],
    waypoints: list[dict[str, Any]],
    methodology: Any,
) -> list[TripWarning]:
    warnings: list[TripWarning] = []
    previous_slug = trip.get("origin_country_slug")
    for waypoint in waypoints:
        destination_slug = waypoint["country_slug"]
        if previous_slug is None:
            previous_slug = destination_slug
            continue
        pair = country_pairs.get_country_pair_compatibility(
            connection, str(previous_slug), str(destination_slug)
        )
        if pair is None:
            warnings.append(
                TripWarning(
                    code="country_pair_missing_context",
                    severity=_severity(
                        methodology.trip_warnings.missing_pair_severity_rank
                    ),
                    message=(
                        "No published compatibility context exists for this route segment."
                    ),
                    source_ids=[],
                    origin_country_slug=str(previous_slug),
                    destination_country_slug=str(destination_slug),
                    waypoint_id=waypoint["id"],
                )
            )
        elif pair["compatibility_label"] == "restrictive":
            sources = country_pairs.list_pair_sources(connection, pair["id"])
            warnings.append(
                TripWarning(
                    code="country_pair_restrictive",
                    severity=_severity(
                        methodology.trip_warnings.restrictive_pair_severity_rank
                    ),
                    message=(
                        pair.get("practical_summary")
                        or "This route segment has restrictive compatibility context."
                    ),
                    source_ids=[str(row["id"]) for row in sources],
                    origin_country_slug=str(previous_slug),
                    destination_country_slug=str(destination_slug),
                    waypoint_id=waypoint["id"],
                )
            )
        previous_slug = destination_slug
    return warnings


def _legal_signal_warnings(
    connection: Connection[Any],
    waypoints: list[dict[str, Any]],
    methodology: Any,
) -> list[TripWarning]:
    slugs = list(dict.fromkeys(str(row["country_slug"]) for row in waypoints))
    if not slugs:
        return []
    min_rank = methodology.trip_warnings.high_impact_min_rank
    waypoint_by_country = {str(row["country_slug"]): row for row in waypoints}
    warnings = []
    for row in repository.list_published_legal_signals_for_country_slugs(
        connection, slugs
    ):
        rank = IMPACT_RANK.get(str(row.get("impact_level")), 1)
        if rank < min_rank:
            continue
        country_slug = str(row["country_slug"])
        waypoint = waypoint_by_country.get(country_slug)
        warnings.append(
            TripWarning(
                code="legal_signal_high_impact",
                severity=_severity(rank),
                message=str(row.get("summary") or row.get("title")),
                source_ids=[str(row["source_id"])]
                if row.get("source_id")
                else [],
                destination_country_slug=country_slug,
                waypoint_id=waypoint["id"] if waypoint else None,
            )
        )
    return warnings


def _severity(rank: int) -> str:
    return SEVERITY_BY_RANK.get(rank, "medium")

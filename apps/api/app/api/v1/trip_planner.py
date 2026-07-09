from app.core.auth import CurrentUser, get_current_active_user
from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.schemas.trip_planner import (
    SharedTripResponse,
    TripAnnotation,
    TripAnnotationCreateRequest,
    TripAnnotationListResponse,
    TripAnnotationUpdateRequest,
    TripChecklistImportRequest,
    TripChecklistItem,
    TripChecklistItemCreateRequest,
    TripChecklistItemUpdateRequest,
    TripChecklistResponse,
    TripCreateFromPassportRequest,
    TripCreateRequest,
    TripDetailResponse,
    TripExportFormat,
    TripListResponse,
    TripReminder,
    TripReminderCreateRequest,
    TripReminderListResponse,
    TripShareResponse,
    TripUpdateRequest,
    TripWarningsResponse,
    TripWaypoint,
    TripWaypointCreateRequest,
    TripWaypointListResponse,
    TripWaypointReorderRequest,
    TripWaypointUpdateRequest,
    TripWhatChangedCountry,
    TripWhatChangedResponse,
)
from app.services import trip_planner as service
from app.services.what_changed import build_what_changed
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from psycopg import Connection
from typing import Annotated, Any
from uuid import UUID


router = APIRouter(tags=["trip-planner"])
shared_router = APIRouter(tags=["trip-planner"])


@router.get("/me/trips", response_model=TripListResponse)
def list_my_trips(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripListResponse:
    items = service.list_user_trips(connection, current_user.id)
    return TripListResponse(total=len(items), items=items)


@router.post("/me/trips", response_model=TripDetailResponse, status_code=201)
def create_my_trip(
    payload: TripCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripDetailResponse:
    item = service.create_user_trip(
        connection, user_id=current_user.id, payload=payload
    )
    connection.commit()
    return TripDetailResponse(item=item)


@router.post(
    "/me/trips/from-passport",
    response_model=TripDetailResponse,
    status_code=201,
)
def create_my_trip_from_passport(
    payload: TripCreateFromPassportRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripDetailResponse:
    item = service.create_trip_from_passport(
        connection, user_id=current_user.id, payload=payload
    )
    connection.commit()
    return TripDetailResponse(item=item)


@router.get("/me/trips/{trip_id}", response_model=TripDetailResponse)
def get_my_trip(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripDetailResponse:
    return TripDetailResponse(
        item=service.get_user_trip(
            connection, user_id=current_user.id, trip_id=str(trip_id)
        )
    )


@router.patch("/me/trips/{trip_id}", response_model=TripDetailResponse)
def update_my_trip(
    trip_id: UUID,
    payload: TripUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripDetailResponse:
    item = service.update_user_trip(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return TripDetailResponse(item=item)


@router.delete("/me/trips/{trip_id}", status_code=204)
def delete_my_trip(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.delete_user_trip(
        connection, user_id=current_user.id, trip_id=str(trip_id)
    )
    connection.commit()


@router.get(
    "/me/trips/{trip_id}/waypoints",
    response_model=TripWaypointListResponse,
)
def list_my_trip_waypoints(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripWaypointListResponse:
    return TripWaypointListResponse(
        items=service.list_waypoints(
            connection, user_id=current_user.id, trip_id=str(trip_id)
        )
    )


@router.post(
    "/me/trips/{trip_id}/waypoints",
    response_model=TripWaypoint,
    status_code=201,
)
def create_my_trip_waypoint(
    trip_id: UUID,
    payload: TripWaypointCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripWaypoint:
    item = service.create_waypoint(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.patch(
    "/me/trips/{trip_id}/waypoints/{waypoint_id}",
    response_model=TripWaypoint,
)
def update_my_trip_waypoint(
    trip_id: UUID,
    waypoint_id: UUID,
    payload: TripWaypointUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripWaypoint:
    item = service.update_waypoint(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        waypoint_id=str(waypoint_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.delete("/me/trips/{trip_id}/waypoints/{waypoint_id}", status_code=204)
def delete_my_trip_waypoint(
    trip_id: UUID,
    waypoint_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.delete_waypoint(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        waypoint_id=str(waypoint_id),
    )
    connection.commit()


@router.post(
    "/me/trips/{trip_id}/waypoints/reorder",
    response_model=TripWaypointListResponse,
)
def reorder_my_trip_waypoints(
    trip_id: UUID,
    payload: TripWaypointReorderRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripWaypointListResponse:
    items = service.reorder_waypoints(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return TripWaypointListResponse(items=items)


@router.get(
    "/me/trips/{trip_id}/checklist",
    response_model=TripChecklistResponse,
)
def list_my_trip_checklist(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripChecklistResponse:
    return TripChecklistResponse(
        items=service.list_checklist_items(
            connection, user_id=current_user.id, trip_id=str(trip_id)
        )
    )


@router.post(
    "/me/trips/{trip_id}/checklist",
    response_model=TripChecklistItem,
    status_code=201,
)
def create_my_trip_checklist_item(
    trip_id: UUID,
    payload: TripChecklistItemCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripChecklistItem:
    item = service.create_checklist_item(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.post(
    "/me/trips/{trip_id}/checklist/import",
    response_model=TripChecklistResponse,
    status_code=201,
)
def import_my_trip_checklist(
    trip_id: UUID,
    payload: TripChecklistImportRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripChecklistResponse:
    items = service.import_route_checklist(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return TripChecklistResponse(items=items)


@router.patch(
    "/me/trips/{trip_id}/checklist/{item_id}",
    response_model=TripChecklistItem,
)
def update_my_trip_checklist_item(
    trip_id: UUID,
    item_id: UUID,
    payload: TripChecklistItemUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripChecklistItem:
    item = service.update_checklist_item(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        item_id=str(item_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.delete("/me/trips/{trip_id}/checklist/{item_id}", status_code=204)
def delete_my_trip_checklist_item(
    trip_id: UUID,
    item_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.delete_checklist_item(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        item_id=str(item_id),
    )
    connection.commit()


@router.get(
    "/me/trips/{trip_id}/warnings",
    response_model=TripWarningsResponse,
)
def read_my_trip_warnings(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripWarningsResponse:
    return service.build_trip_warnings(
        connection, user_id=current_user.id, trip_id=str(trip_id)
    )


@router.get(
    "/me/trips/{trip_id}/reminders",
    response_model=TripReminderListResponse,
)
def list_my_trip_reminders(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripReminderListResponse:
    return TripReminderListResponse(
        items=service.list_reminders(
            connection, user_id=current_user.id, trip_id=str(trip_id)
        )
    )


@router.post(
    "/me/trips/{trip_id}/reminders",
    response_model=TripReminder,
    status_code=201,
)
def create_my_trip_reminder(
    trip_id: UUID,
    payload: TripReminderCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripReminder:
    item = service.create_reminder(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.delete("/me/trips/{trip_id}/reminders/{reminder_id}", status_code=204)
def cancel_my_trip_reminder(
    trip_id: UUID,
    reminder_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.cancel_reminder(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        reminder_id=str(reminder_id),
    )
    connection.commit()


@router.post(
    "/me/trips/{trip_id}/share",
    response_model=TripShareResponse,
)
def enable_my_trip_share(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripShareResponse:
    response = service.enable_share(
        connection, user_id=current_user.id, trip_id=str(trip_id)
    )
    connection.commit()
    return response


@router.delete("/me/trips/{trip_id}/share", status_code=204)
def disable_my_trip_share(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.disable_share(
        connection, user_id=current_user.id, trip_id=str(trip_id)
    )
    connection.commit()


@shared_router.get("/trips/shared/{token}", response_model=SharedTripResponse)
def read_shared_trip(
    token: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> SharedTripResponse:
    return service.get_shared_trip(connection, token=token)


@router.get("/me/trips/{trip_id}/export")
def export_my_trip(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
    format: TripExportFormat = "json",
) -> Response:
    content, media_type, filename = service.export_trip(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        export_format=format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/me/trips/{trip_id}/annotations",
    response_model=TripAnnotationListResponse,
)
def list_my_trip_annotations(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripAnnotationListResponse:
    return TripAnnotationListResponse(
        items=service.list_annotations(
            connection, user_id=current_user.id, trip_id=str(trip_id)
        )
    )


@router.post(
    "/me/trips/{trip_id}/annotations",
    response_model=TripAnnotation,
    status_code=201,
)
def create_my_trip_annotation(
    trip_id: UUID,
    payload: TripAnnotationCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripAnnotation:
    item = service.create_annotation(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.patch(
    "/me/trips/{trip_id}/annotations/{annotation_id}",
    response_model=TripAnnotation,
)
def update_my_trip_annotation(
    trip_id: UUID,
    annotation_id: UUID,
    payload: TripAnnotationUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> TripAnnotation:
    item = service.update_annotation(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        annotation_id=str(annotation_id),
        payload=payload,
    )
    connection.commit()
    return item


@router.delete(
    "/me/trips/{trip_id}/annotations/{annotation_id}", status_code=204
)
def delete_my_trip_annotation(
    trip_id: UUID,
    annotation_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> None:
    service.delete_annotation(
        connection,
        user_id=current_user.id,
        trip_id=str(trip_id),
        annotation_id=str(annotation_id),
    )
    connection.commit()


@router.get(
    "/me/trips/{trip_id}/what-changed",
    response_model=TripWhatChangedResponse,
)
def read_my_trip_what_changed(
    trip_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    since: datetime | None = None,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TripWhatChangedResponse:
    trip = service.get_user_trip(
        connection, user_id=current_user.id, trip_id=str(trip_id)
    )
    country_slugs = list(
        dict.fromkeys(
            [
                *(
                    [trip.origin_country.slug]
                    if trip.origin_country is not None
                    else []
                ),
                *[waypoint.country.slug for waypoint in trip.waypoints],
            ]
        )
    )
    countries = []
    for country_slug in country_slugs:
        result = build_what_changed(
            connection, country_slug, locale, since, days, limit
        )
        countries.append(
            TripWhatChangedCountry(
                country_slug=country_slug, total=result.summary.total
            )
        )
    return TripWhatChangedResponse(trip_id=str(trip_id), countries=countries)

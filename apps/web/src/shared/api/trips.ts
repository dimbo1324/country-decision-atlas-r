import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPatch, apiPost } from "./http";

export type TripSummary = components["schemas"]["TripSummary"];
export type TripDetail = components["schemas"]["TripDetail"];
export type TripDetailResponse = components["schemas"]["TripDetailResponse"];
export type TripListResponse = components["schemas"]["TripListResponse"];
export type TripCreateRequest = components["schemas"]["TripCreateRequest"];
export type TripCreateFromPassportRequest =
  components["schemas"]["TripCreateFromPassportRequest"];
export type TripUpdateRequest = components["schemas"]["TripUpdateRequest"];
export type TripCountryRef = components["schemas"]["TripCountryRef"];
export type TripWaypoint = components["schemas"]["TripWaypoint"];
export type TripWaypointCreateRequest =
  components["schemas"]["TripWaypointCreateRequest"];
export type TripWaypointUpdateRequest =
  components["schemas"]["TripWaypointUpdateRequest"];
export type TripWaypointListResponse =
  components["schemas"]["TripWaypointListResponse"];
export type TripWaypointReorderRequest =
  components["schemas"]["TripWaypointReorderRequest"];
export type TripChecklistItem = components["schemas"]["TripChecklistItem"];
export type TripChecklistItemCreateRequest =
  components["schemas"]["TripChecklistItemCreateRequest"];
export type TripChecklistItemUpdateRequest =
  components["schemas"]["TripChecklistItemUpdateRequest"];
export type TripChecklistResponse =
  components["schemas"]["TripChecklistResponse"];
export type TripChecklistImportRequest =
  components["schemas"]["TripChecklistImportRequest"];
export type TripReminder = components["schemas"]["TripReminder"];
export type TripReminderCreateRequest =
  components["schemas"]["TripReminderCreateRequest"];
export type TripReminderListResponse =
  components["schemas"]["TripReminderListResponse"];
export type TripWarning = components["schemas"]["TripWarning"];
export type TripWarningsResponse =
  components["schemas"]["TripWarningsResponse"];
export type TripWhatChangedResponse =
  components["schemas"]["TripWhatChangedResponse"];
export type TripAnnotation = components["schemas"]["TripAnnotation"];
export type TripAnnotationCreateRequest =
  components["schemas"]["TripAnnotationCreateRequest"];
export type TripAnnotationUpdateRequest =
  components["schemas"]["TripAnnotationUpdateRequest"];
export type TripAnnotationListResponse =
  components["schemas"]["TripAnnotationListResponse"];
export type TripShareResponse = components["schemas"]["TripShareResponse"];
export type SharedTripResponse = components["schemas"]["SharedTripResponse"];

export function listTrips(): Promise<TripListResponse> {
  return apiGet<TripListResponse>("/api/v1/me/trips", {
    headers: csrfHeaders(),
  });
}

export function createTrip(
  payload: TripCreateRequest,
): Promise<TripDetailResponse> {
  return apiPost<TripDetailResponse, TripCreateRequest>(
    "/api/v1/me/trips",
    payload,
    { headers: csrfHeaders() },
  );
}

export function createTripFromPassport(
  payload: TripCreateFromPassportRequest,
): Promise<TripDetailResponse> {
  return apiPost<TripDetailResponse, TripCreateFromPassportRequest>(
    "/api/v1/me/trips/from-passport",
    payload,
    { headers: csrfHeaders() },
  );
}

export function getTrip(tripId: string): Promise<TripDetailResponse> {
  return apiGet<TripDetailResponse>(`/api/v1/me/trips/${tripId}`, {
    headers: csrfHeaders(),
  });
}

export function updateTrip(
  tripId: string,
  payload: TripUpdateRequest,
): Promise<TripDetailResponse> {
  return apiPatch<TripDetailResponse, TripUpdateRequest>(
    `/api/v1/me/trips/${tripId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function deleteTrip(tripId: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/trips/${tripId}`, {
    headers: csrfHeaders(),
  });
}

export function listWaypoints(
  tripId: string,
): Promise<TripWaypointListResponse> {
  return apiGet<TripWaypointListResponse>(
    `/api/v1/me/trips/${tripId}/waypoints`,
    { headers: csrfHeaders() },
  );
}

export function createWaypoint(
  tripId: string,
  payload: TripWaypointCreateRequest,
): Promise<TripWaypoint> {
  return apiPost<TripWaypoint, TripWaypointCreateRequest>(
    `/api/v1/me/trips/${tripId}/waypoints`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateWaypoint(
  tripId: string,
  waypointId: string,
  payload: TripWaypointUpdateRequest,
): Promise<TripWaypoint> {
  return apiPatch<TripWaypoint, TripWaypointUpdateRequest>(
    `/api/v1/me/trips/${tripId}/waypoints/${waypointId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function deleteWaypoint(
  tripId: string,
  waypointId: string,
): Promise<void> {
  return apiDelete<void>(`/api/v1/me/trips/${tripId}/waypoints/${waypointId}`, {
    headers: csrfHeaders(),
  });
}

export function reorderWaypoints(
  tripId: string,
  waypointIds: string[],
): Promise<TripWaypointListResponse> {
  return apiPost<TripWaypointListResponse, TripWaypointReorderRequest>(
    `/api/v1/me/trips/${tripId}/waypoints/reorder`,
    { waypoint_ids: waypointIds },
    { headers: csrfHeaders() },
  );
}

export function listChecklist(tripId: string): Promise<TripChecklistResponse> {
  return apiGet<TripChecklistResponse>(`/api/v1/me/trips/${tripId}/checklist`, {
    headers: csrfHeaders(),
  });
}

export function createChecklistItem(
  tripId: string,
  payload: TripChecklistItemCreateRequest,
): Promise<TripChecklistItem> {
  return apiPost<TripChecklistItem, TripChecklistItemCreateRequest>(
    `/api/v1/me/trips/${tripId}/checklist`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function importChecklist(
  tripId: string,
  routeId: string,
): Promise<TripChecklistResponse> {
  return apiPost<TripChecklistResponse, TripChecklistImportRequest>(
    `/api/v1/me/trips/${tripId}/checklist/import`,
    { route_id: routeId },
    { headers: csrfHeaders() },
  );
}

export function updateChecklistItem(
  tripId: string,
  itemId: string,
  payload: TripChecklistItemUpdateRequest,
): Promise<TripChecklistItem> {
  return apiPatch<TripChecklistItem, TripChecklistItemUpdateRequest>(
    `/api/v1/me/trips/${tripId}/checklist/${itemId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function deleteChecklistItem(
  tripId: string,
  itemId: string,
): Promise<void> {
  return apiDelete<void>(`/api/v1/me/trips/${tripId}/checklist/${itemId}`, {
    headers: csrfHeaders(),
  });
}

export function getWarnings(tripId: string): Promise<TripWarningsResponse> {
  return apiGet<TripWarningsResponse>(`/api/v1/me/trips/${tripId}/warnings`, {
    headers: csrfHeaders(),
  });
}

export function listReminders(
  tripId: string,
): Promise<TripReminderListResponse> {
  return apiGet<TripReminderListResponse>(
    `/api/v1/me/trips/${tripId}/reminders`,
    { headers: csrfHeaders() },
  );
}

export function createReminder(
  tripId: string,
  payload: TripReminderCreateRequest,
): Promise<TripReminder> {
  return apiPost<TripReminder, TripReminderCreateRequest>(
    `/api/v1/me/trips/${tripId}/reminders`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function cancelReminder(
  tripId: string,
  reminderId: string,
): Promise<void> {
  return apiDelete<void>(`/api/v1/me/trips/${tripId}/reminders/${reminderId}`, {
    headers: csrfHeaders(),
  });
}

export function enableShare(tripId: string): Promise<TripShareResponse> {
  return apiPost<TripShareResponse, Record<string, never>>(
    `/api/v1/me/trips/${tripId}/share`,
    {},
    { headers: csrfHeaders() },
  );
}

export function disableShare(tripId: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/trips/${tripId}/share`, {
    headers: csrfHeaders(),
  });
}

export function exportTrip(tripId: string): Promise<TripDetail> {
  return apiGet<TripDetail>(`/api/v1/me/trips/${tripId}/export`, {
    headers: csrfHeaders(),
  });
}

export function listAnnotations(
  tripId: string,
): Promise<TripAnnotationListResponse> {
  return apiGet<TripAnnotationListResponse>(
    `/api/v1/me/trips/${tripId}/annotations`,
    { headers: csrfHeaders() },
  );
}

export function createAnnotation(
  tripId: string,
  payload: TripAnnotationCreateRequest,
): Promise<TripAnnotation> {
  return apiPost<TripAnnotation, TripAnnotationCreateRequest>(
    `/api/v1/me/trips/${tripId}/annotations`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateAnnotation(
  tripId: string,
  annotationId: string,
  payload: TripAnnotationUpdateRequest,
): Promise<TripAnnotation> {
  return apiPatch<TripAnnotation, TripAnnotationUpdateRequest>(
    `/api/v1/me/trips/${tripId}/annotations/${annotationId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function deleteAnnotation(
  tripId: string,
  annotationId: string,
): Promise<void> {
  return apiDelete<void>(
    `/api/v1/me/trips/${tripId}/annotations/${annotationId}`,
    { headers: csrfHeaders() },
  );
}

export function getWhatChanged(
  tripId: string,
): Promise<TripWhatChangedResponse> {
  return apiGet<TripWhatChangedResponse>(
    `/api/v1/me/trips/${tripId}/what-changed`,
    { headers: csrfHeaders() },
  );
}

export function getSharedTrip(token: string): Promise<SharedTripResponse> {
  return apiGet<SharedTripResponse>(`/api/v1/trips/shared/${token}`);
}

export const tripsApi = {
  listTrips,
  createTrip,
  createTripFromPassport,
  getTrip,
  updateTrip,
  deleteTrip,
  listWaypoints,
  createWaypoint,
  updateWaypoint,
  deleteWaypoint,
  reorderWaypoints,
  listChecklist,
  createChecklistItem,
  importChecklist,
  updateChecklistItem,
  deleteChecklistItem,
  getWarnings,
  listReminders,
  createReminder,
  cancelReminder,
  enableShare,
  disableShare,
  exportTrip,
  listAnnotations,
  createAnnotation,
  updateAnnotation,
  deleteAnnotation,
  getWhatChanged,
  getSharedTrip,
};

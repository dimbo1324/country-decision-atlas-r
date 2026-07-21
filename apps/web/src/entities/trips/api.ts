import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import type {
  TripAnnotationCreateRequest,
  TripAnnotationUpdateRequest,
  TripChecklistItemCreateRequest,
  TripChecklistItemUpdateRequest,
  TripChecklistResponse,
  TripCreateFromPassportRequest,
  TripCreateRequest,
  TripDetailResponse,
  TripReminderCreateRequest,
  TripUpdateRequest,
  TripWaypointCreateRequest,
  TripWaypointListResponse,
  TripWaypointUpdateRequest,
} from "../../shared/api/trips";
import { toast } from "@country-decision-atlas/ui";
import { tripsApi } from "../../shared/api/trips";
import { mutationErrorMessage } from "../../shared/api/http";

const TRIPS_QUERY_KEY = ["trips", "list"] as const;
const tripQueryKey = (tripId: string) => ["trips", "detail", tripId] as const;
const warningsQueryKey = (tripId: string) =>
  ["trips", "warnings", tripId] as const;
const whatChangedQueryKey = (tripId: string) =>
  ["trips", "what-changed", tripId] as const;

export function tripsQuery() {
  return queryOptions({
    queryKey: TRIPS_QUERY_KEY,
    queryFn: () => tripsApi.listTrips(),
    staleTime: 30_000,
  });
}

export function tripQuery(tripId: string) {
  return queryOptions({
    queryKey: tripQueryKey(tripId),
    queryFn: () => tripsApi.getTrip(tripId),
    enabled: Boolean(tripId),
    staleTime: 10_000,
  });
}

export function tripWarningsQuery(tripId: string) {
  return queryOptions({
    queryKey: warningsQueryKey(tripId),
    queryFn: () => tripsApi.getWarnings(tripId),
    enabled: Boolean(tripId),
    staleTime: 30_000,
  });
}

export function tripWhatChangedQuery(tripId: string) {
  return queryOptions({
    queryKey: whatChangedQueryKey(tripId),
    queryFn: () => tripsApi.getWhatChanged(tripId),
    enabled: Boolean(tripId),
    staleTime: 30_000,
  });
}

export function useCreateTripMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripCreateRequest) => tripsApi.createTrip(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: TRIPS_QUERY_KEY });
    },
  });
}

export function useCreateTripFromPassportMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripCreateFromPassportRequest) =>
      tripsApi.createTripFromPassport(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: TRIPS_QUERY_KEY });
    },
  });
}

export function useUpdateTripMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripUpdateRequest) =>
      tripsApi.updateTrip(tripId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
      void queryClient.invalidateQueries({ queryKey: TRIPS_QUERY_KEY });
    },
  });
}

export function useDeleteTripMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tripId: string) => tripsApi.deleteTrip(tripId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: TRIPS_QUERY_KEY });
    },
  });
}

export function useCreateWaypointMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripWaypointCreateRequest) =>
      tripsApi.createWaypoint(tripId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useUpdateWaypointMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      waypointId,
      payload,
    }: {
      waypointId: string;
      payload: TripWaypointUpdateRequest;
    }) => tripsApi.updateWaypoint(tripId, waypointId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useDeleteWaypointMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (waypointId: string) =>
      tripsApi.deleteWaypoint(tripId, waypointId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

/** Optimistic reorder: the dnd-kit drop already shows the new order in local
 * state; this mirrors it into the trip-detail cache immediately so a refetch
 * mid-drag doesn't snap waypoints back, then rolls back on error. */
export function useReorderWaypointsMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (waypointIds: string[]) =>
      tripsApi.reorderWaypoints(tripId, waypointIds),
    onMutate: async (waypointIds: string[]) => {
      await queryClient.cancelQueries({ queryKey: tripQueryKey(tripId) });
      const previous = queryClient.getQueryData<TripDetailResponse>(
        tripQueryKey(tripId),
      );
      if (previous) {
        const byId = new Map(
          previous.item.waypoints?.map((w) => [w.id, w]) ?? [],
        );
        const reordered = waypointIds
          .map((id, index) => {
            const waypoint = byId.get(id);
            return waypoint ? { ...waypoint, position: index } : null;
          })
          .filter((w): w is NonNullable<typeof w> => w !== null);
        queryClient.setQueryData<TripDetailResponse>(tripQueryKey(tripId), {
          item: { ...previous.item, waypoints: reordered },
        });
      }
      return { previous };
    },
    onError: (error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(tripQueryKey(tripId), context.previous);
      }
      toast.error(mutationErrorMessage(error));
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useCreateChecklistItemMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripChecklistItemCreateRequest) =>
      tripsApi.createChecklistItem(tripId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useImportChecklistMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (routeId: string) => tripsApi.importChecklist(tripId, routeId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

/** Optimistic status toggle (todo/in_progress/done/skipped): flips the
 * checkbox immediately, rolls back on error, per the plan's explicit
 * optimistic-CRUD pattern for checklist toggles. */
export function useUpdateChecklistItemMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      itemId,
      payload,
    }: {
      itemId: string;
      payload: TripChecklistItemUpdateRequest;
    }) => tripsApi.updateChecklistItem(tripId, itemId, payload),
    onMutate: async ({ itemId, payload }) => {
      await queryClient.cancelQueries({ queryKey: tripQueryKey(tripId) });
      const previous = queryClient.getQueryData<TripDetailResponse>(
        tripQueryKey(tripId),
      );
      if (previous) {
        queryClient.setQueryData<TripDetailResponse>(tripQueryKey(tripId), {
          item: {
            ...previous.item,
            checklist_items: previous.item.checklist_items?.map((item) =>
              item.id === itemId
                ? {
                    ...item,
                    ...(payload.status != null
                      ? { status: payload.status }
                      : {}),
                    ...(payload.title != null ? { title: payload.title } : {}),
                    ...(payload.description !== undefined
                      ? { description: payload.description }
                      : {}),
                    ...(payload.due_date !== undefined
                      ? { due_date: payload.due_date }
                      : {}),
                  }
                : item,
            ),
          },
        });
      }
      return { previous };
    },
    onError: (error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(tripQueryKey(tripId), context.previous);
      }
      toast.error(mutationErrorMessage(error));
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useDeleteChecklistItemMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (itemId: string) =>
      tripsApi.deleteChecklistItem(tripId, itemId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useCreateReminderMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripReminderCreateRequest) =>
      tripsApi.createReminder(tripId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useCancelReminderMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reminderId: string) =>
      tripsApi.cancelReminder(tripId, reminderId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useEnableShareMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => tripsApi.enableShare(tripId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useDisableShareMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => tripsApi.disableShare(tripId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useCreateAnnotationMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TripAnnotationCreateRequest) =>
      tripsApi.createAnnotation(tripId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useUpdateAnnotationMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      annotationId,
      payload,
    }: {
      annotationId: string;
      payload: TripAnnotationUpdateRequest;
    }) => tripsApi.updateAnnotation(tripId, annotationId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export function useDeleteAnnotationMutation(tripId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (annotationId: string) =>
      tripsApi.deleteAnnotation(tripId, annotationId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: tripQueryKey(tripId) });
    },
  });
}

export const getSharedTrip = tripsApi.getSharedTrip;
export const exportTrip = tripsApi.exportTrip;
export type { TripWaypointListResponse, TripChecklistResponse };

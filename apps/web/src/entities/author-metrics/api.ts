import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { authorMetricsApi } from "../../shared/api/author-metrics";
import type {
  AuthorMetricValueItem,
  CreateAuthorMetricRequest,
  ModerateAuthorMetricRequest,
  PublicationStatus,
  UpdateAuthorMetricRequest,
} from "../../shared/api/author-metrics";

const MY_METRICS_QUERY_KEY = ["author-metrics", "mine"] as const;
const myMetricQueryKey = (definitionId: string) =>
  ["author-metrics", "mine", definitionId] as const;
const myMetricValuesQueryKey = (definitionId: string) =>
  ["author-metrics", "mine", definitionId, "values"] as const;
const authorPublicMetricsQueryKey = (userId: string) =>
  ["author-metrics", "public", userId] as const;
const authorReputationQueryKey = (userId: string) =>
  ["author-metrics", "reputation", userId] as const;

export function myAuthorMetricsQuery() {
  return queryOptions({
    queryKey: MY_METRICS_QUERY_KEY,
    queryFn: () => authorMetricsApi.listMyAuthorMetrics(),
  });
}

export function myAuthorMetricQuery(definitionId: string) {
  return queryOptions({
    queryKey: myMetricQueryKey(definitionId),
    queryFn: () => authorMetricsApi.getMyAuthorMetric(definitionId),
    enabled: Boolean(definitionId),
  });
}

export function myAuthorMetricValuesQuery(definitionId: string) {
  return queryOptions({
    queryKey: myMetricValuesQueryKey(definitionId),
    queryFn: () => authorMetricsApi.listMyAuthorMetricValues(definitionId),
    enabled: Boolean(definitionId),
  });
}

export function authorPublicMetricsQuery(userId: string) {
  return queryOptions({
    queryKey: authorPublicMetricsQueryKey(userId),
    queryFn: () => authorMetricsApi.listAuthorPublicMetrics(userId),
    enabled: Boolean(userId),
  });
}

export function authorReputationQuery(userId: string) {
  return queryOptions({
    queryKey: authorReputationQueryKey(userId),
    queryFn: () => authorMetricsApi.getAuthorReputation(userId),
    enabled: Boolean(userId),
    retry: false,
  });
}

export function useCreateAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateAuthorMetricRequest) =>
      authorMetricsApi.createMyAuthorMetric(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_METRICS_QUERY_KEY });
    },
  });
}

export function useUpdateAuthorMetricMutation(definitionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateAuthorMetricRequest) =>
      authorMetricsApi.updateMyAuthorMetric(definitionId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_METRICS_QUERY_KEY });
      void queryClient.invalidateQueries({
        queryKey: myMetricQueryKey(definitionId),
      });
    },
  });
}

export function useSubmitAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (definitionId: string) =>
      authorMetricsApi.submitMyAuthorMetric(definitionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_METRICS_QUERY_KEY });
    },
  });
}

export function useArchiveAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (definitionId: string) =>
      authorMetricsApi.archiveMyAuthorMetric(definitionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_METRICS_QUERY_KEY });
    },
  });
}

export function useUpsertAuthorMetricValuesMutation(definitionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (items: AuthorMetricValueItem[]) =>
      authorMetricsApi.bulkUpsertMyAuthorMetricValues(definitionId, items),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: myMetricValuesQueryKey(definitionId),
      });
    },
  });
}

const ADMIN_METRICS_QUERY_KEY = ["author-metrics", "admin"] as const;

export function adminAuthorMetricsQuery(status?: PublicationStatus) {
  return queryOptions({
    queryKey: [...ADMIN_METRICS_QUERY_KEY, status ?? "all"] as const,
    queryFn: () => authorMetricsApi.listAdminAuthorMetrics(status),
  });
}

export function useApproveAdminAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (definitionId: string) =>
      authorMetricsApi.approveAdminAuthorMetric(definitionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ADMIN_METRICS_QUERY_KEY,
      });
    },
  });
}

export function useRejectAdminAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      definitionId,
      payload,
    }: {
      definitionId: string;
      payload: ModerateAuthorMetricRequest;
    }) => authorMetricsApi.rejectAdminAuthorMetric(definitionId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ADMIN_METRICS_QUERY_KEY,
      });
    },
  });
}

export function useForkAuthorMetricMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      definitionId,
      slug,
    }: {
      definitionId: string;
      slug: string;
    }) => authorMetricsApi.forkAuthorMetric(definitionId, slug),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_METRICS_QUERY_KEY });
    },
  });
}

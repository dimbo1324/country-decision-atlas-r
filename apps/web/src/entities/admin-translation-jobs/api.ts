import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { adminTranslationJobsApi } from "../../shared/api/admin-translation-jobs";
import type {
  TranslationJobCreateMissingRequest,
  TranslationJobCreateStaleRequest,
  TranslationJobProcessBatchRequest,
  TranslationJobRetryFailedRequest,
} from "../../shared/api/admin-translation-jobs";

const QUERY_KEY = ["admin", "translation-jobs"] as const;

export function adminTranslationJobsQuery() {
  return queryOptions({
    queryKey: QUERY_KEY,
    queryFn: () => adminTranslationJobsApi.listAdminTranslationJobs(),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: QUERY_KEY });
}

export function useCreateMissingTranslationJobsMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (payload: TranslationJobCreateMissingRequest) =>
      adminTranslationJobsApi.createMissingTranslationJobs(payload),
    onSuccess: invalidate,
  });
}

export function useCreateStaleTranslationJobsMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (payload: TranslationJobCreateStaleRequest) =>
      adminTranslationJobsApi.createStaleTranslationJobs(payload),
    onSuccess: invalidate,
  });
}

export function useProcessTranslationJobBatchMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (payload: TranslationJobProcessBatchRequest) =>
      adminTranslationJobsApi.processTranslationJobBatch(payload),
    onSuccess: invalidate,
  });
}

export function useRetryFailedTranslationJobsMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (payload: TranslationJobRetryFailedRequest) =>
      adminTranslationJobsApi.retryFailedTranslationJobs(payload),
    onSuccess: invalidate,
  });
}

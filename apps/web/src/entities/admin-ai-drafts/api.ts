import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { adminAiDraftsApi } from "../../shared/api/admin-ai-drafts";
import type {
  AIDraftGenerateSummaryRequest,
  AIDraftStatusUpdateRequest,
} from "../../shared/api/admin-ai-drafts";

const QUERY_KEY = ["admin", "ai-drafts"] as const;

export function adminAiDraftsQuery(status?: string) {
  return queryOptions({
    queryKey: [...QUERY_KEY, status ?? "all"] as const,
    queryFn: () => adminAiDraftsApi.listAdminAiDrafts(status),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: QUERY_KEY });
}

export function useGenerateAiDraftSummaryMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (payload: AIDraftGenerateSummaryRequest) =>
      adminAiDraftsApi.generateAiDraftSummary(payload),
    onSuccess: invalidate,
  });
}

export function useUpdateAiDraftStatusMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      draftId,
      payload,
    }: {
      draftId: string;
      payload: AIDraftStatusUpdateRequest;
    }) => adminAiDraftsApi.updateAiDraftStatus(draftId, payload),
    onSuccess: invalidate,
  });
}

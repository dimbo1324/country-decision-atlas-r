import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { adminContradictionCandidatesApi } from "../../shared/api/admin-contradiction-candidates";
import type { ContradictionCandidateStatusUpdateRequest } from "../../shared/api/admin-contradiction-candidates";

const QUERY_KEY = ["admin", "contradiction-candidates"] as const;

export function adminContradictionCandidatesQuery(status?: string) {
  return queryOptions({
    queryKey: [...QUERY_KEY, status ?? "all"] as const,
    queryFn: () =>
      adminContradictionCandidatesApi.listAdminContradictionCandidates(status),
  });
}

export function useUpdateContradictionCandidateStatusMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      candidateId,
      payload,
    }: {
      candidateId: string;
      payload: ContradictionCandidateStatusUpdateRequest;
    }) =>
      adminContradictionCandidatesApi.updateContradictionCandidateStatus(
        candidateId,
        payload,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

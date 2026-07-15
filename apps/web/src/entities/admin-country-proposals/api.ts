import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { adminCountryProposalsApi } from "../../shared/api/admin-country-proposals";
import type {
  ModerationReasonPayload,
  PublicationStatus,
} from "../../shared/api/admin-country-proposals";

const QUERY_KEY = ["admin", "country-proposals"] as const;

export function adminCountryProposalsQuery(status?: PublicationStatus) {
  return queryOptions({
    queryKey: [...QUERY_KEY, status ?? "all"] as const,
    queryFn: () => adminCountryProposalsApi.listAdminCountryProposals(status),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: QUERY_KEY });
}

export function useAssignCuratorMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (proposalId: string) =>
      adminCountryProposalsApi.assignCountryProposalCurator(proposalId),
    onSuccess: invalidate,
  });
}

export function useReadinessCheckMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (proposalId: string) =>
      adminCountryProposalsApi.runCountryProposalReadinessCheck(proposalId),
    onSuccess: invalidate,
  });
}

export function usePublishProposalMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (proposalId: string) =>
      adminCountryProposalsApi.publishCountryProposal(proposalId),
    onSuccess: invalidate,
  });
}

export function useRejectProposalMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      proposalId,
      payload,
    }: {
      proposalId: string;
      payload: ModerationReasonPayload;
    }) => adminCountryProposalsApi.rejectCountryProposal(proposalId, payload),
    onSuccess: invalidate,
  });
}

export function useRequestChangesMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      proposalId,
      payload,
    }: {
      proposalId: string;
      payload: ModerationReasonPayload;
    }) =>
      adminCountryProposalsApi.requestCountryProposalChanges(
        proposalId,
        payload,
      ),
    onSuccess: invalidate,
  });
}

export function useArchiveProposalMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: (proposalId: string) =>
      adminCountryProposalsApi.archiveCountryProposal(proposalId),
    onSuccess: invalidate,
  });
}

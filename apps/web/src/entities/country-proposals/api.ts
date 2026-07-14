import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { countryProposalsApi } from "../../shared/api/country-proposals";
import type {
  ContributorEvidenceItemCreate,
  ContributorLegalSignalCreate,
  ContributorSourceCreate,
  ContributorTimelineEventCreate,
  CountryCardUpsert,
  CountryMetricValueEntry,
  CountryProposalCreate,
  CountryProposalPatch,
} from "../../shared/api/country-proposals";

const MY_PROPOSALS_QUERY_KEY = ["country-proposals", "mine"] as const;
const myProposalQueryKey = (proposalId: string) =>
  ["country-proposals", "mine", proposalId] as const;

export function myCountryProposalsQuery() {
  return queryOptions({
    queryKey: MY_PROPOSALS_QUERY_KEY,
    queryFn: () => countryProposalsApi.listMyCountryProposals(),
  });
}

export function myCountryProposalQuery(proposalId: string) {
  return queryOptions({
    queryKey: myProposalQueryKey(proposalId),
    queryFn: () => countryProposalsApi.getMyCountryProposal(proposalId),
    enabled: Boolean(proposalId),
  });
}

export function useCreateCountryProposalMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CountryProposalCreate) =>
      countryProposalsApi.createMyCountryProposal(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_PROPOSALS_QUERY_KEY });
    },
  });
}

export function usePatchCountryProposalMutation(proposalId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CountryProposalPatch) =>
      countryProposalsApi.patchMyCountryProposal(proposalId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: myProposalQueryKey(proposalId),
      });
    },
  });
}

export function useSubmitCountryProposalMutation(proposalId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => countryProposalsApi.submitMyCountryProposal(proposalId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: myProposalQueryKey(proposalId),
      });
      void queryClient.invalidateQueries({ queryKey: MY_PROPOSALS_QUERY_KEY });
    },
  });
}

export function useUpsertCountryProposalCardMutation(proposalId: string) {
  return useMutation({
    mutationFn: ({
      locale,
      payload,
    }: {
      locale: string;
      payload: CountryCardUpsert;
    }) =>
      countryProposalsApi.upsertMyCountryProposalCard(
        proposalId,
        locale,
        payload,
      ),
  });
}

export function useCreateCountryProposalSourceMutation(proposalId: string) {
  return useMutation({
    mutationFn: (payload: ContributorSourceCreate) =>
      countryProposalsApi.createMyCountryProposalSource(proposalId, payload),
  });
}

export function useCreateCountryProposalEvidenceItemMutation(
  proposalId: string,
) {
  return useMutation({
    mutationFn: (payload: ContributorEvidenceItemCreate) =>
      countryProposalsApi.createMyCountryProposalEvidenceItem(
        proposalId,
        payload,
      ),
  });
}

export function useCreateCountryProposalLegalSignalMutation(
  proposalId: string,
) {
  return useMutation({
    mutationFn: (payload: ContributorLegalSignalCreate) =>
      countryProposalsApi.createMyCountryProposalLegalSignal(
        proposalId,
        payload,
      ),
  });
}

export function useCreateCountryProposalTimelineEventMutation(
  proposalId: string,
) {
  return useMutation({
    mutationFn: (payload: ContributorTimelineEventCreate) =>
      countryProposalsApi.createMyCountryProposalTimelineEvent(
        proposalId,
        payload,
      ),
  });
}

export function useUpsertCountryProposalMetricValuesMutation(
  proposalId: string,
) {
  return useMutation({
    mutationFn: (values: CountryMetricValueEntry[]) =>
      countryProposalsApi.upsertMyCountryProposalMetricValues(
        proposalId,
        values,
      ),
  });
}

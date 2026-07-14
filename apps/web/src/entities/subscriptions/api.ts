import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import type { CreateSubscriptionRequest } from "../../shared/api/subscriptions";
import { subscriptionsApi } from "../../shared/api/subscriptions";

const SUBSCRIPTIONS_QUERY_KEY = ["subscriptions", "list"] as const;
const FEED_QUERY_KEY = ["subscriptions", "feed"] as const;

export function subscriptionsQuery() {
  return queryOptions({
    queryKey: SUBSCRIPTIONS_QUERY_KEY,
    queryFn: () => subscriptionsApi.listSubscriptions(),
    staleTime: 30_000,
  });
}

export function subscriptionsFeedQuery() {
  return queryOptions({
    queryKey: FEED_QUERY_KEY,
    queryFn: () => subscriptionsApi.getSubscriptionsFeed(),
    staleTime: 30_000,
  });
}

export function useCreateSubscriptionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateSubscriptionRequest) =>
      subscriptionsApi.createSubscription(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: SUBSCRIPTIONS_QUERY_KEY,
      });
      void queryClient.invalidateQueries({ queryKey: FEED_QUERY_KEY });
    },
  });
}

export function useDeleteSubscriptionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (subscriptionId: string) =>
      subscriptionsApi.deleteSubscription(subscriptionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: SUBSCRIPTIONS_QUERY_KEY,
      });
      void queryClient.invalidateQueries({ queryKey: FEED_QUERY_KEY });
    },
  });
}

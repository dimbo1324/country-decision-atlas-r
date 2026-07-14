import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPost } from "./http";

export type SubscriptionResponse =
  components["schemas"]["SubscriptionResponse"];
export type SubscriptionListResponse =
  components["schemas"]["SubscriptionListResponse"];
export type SubscriptionFeedResponse =
  components["schemas"]["SubscriptionFeedResponse"];
export type CreateSubscriptionRequest =
  components["schemas"]["CreateSubscriptionRequest"];
export type FeedEntryResponse = components["schemas"]["FeedEntryResponse"];

export function listSubscriptions(): Promise<SubscriptionListResponse> {
  return apiGet<SubscriptionListResponse>("/api/v1/me/subscriptions", {
    headers: csrfHeaders(),
  });
}

export function createSubscription(
  payload: CreateSubscriptionRequest,
): Promise<SubscriptionResponse> {
  return apiPost<SubscriptionResponse, CreateSubscriptionRequest>(
    "/api/v1/me/subscriptions",
    payload,
    { headers: csrfHeaders() },
  );
}

export function deleteSubscription(subscriptionId: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/subscriptions/${subscriptionId}`, {
    headers: csrfHeaders(),
  });
}

export function getSubscriptionsFeed(): Promise<SubscriptionFeedResponse> {
  return apiGet<SubscriptionFeedResponse>("/api/v1/me/subscriptions/feed", {
    headers: csrfHeaders(),
  });
}

export const subscriptionsApi = {
  listSubscriptions,
  createSubscription,
  deleteSubscription,
  getSubscriptionsFeed,
};

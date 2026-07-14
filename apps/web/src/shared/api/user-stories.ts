import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, apiPost, queryString } from "./http";

export type UserStory = components["schemas"]["UserStory"];
export type UserStoryListResponse =
  components["schemas"]["UserStoryListResponse"];
export type UserStoryResponse = components["schemas"]["UserStoryResponse"];
export type UserStoryCreate = components["schemas"]["UserStoryCreate"];

type ListUserStoriesParams = {
  originCountrySlug?: string;
  destinationCountrySlug?: string;
  scenario?: string;
  verificationStatus?: string;
  isSynthetic?: boolean;
  status?: "published" | "archived";
  sort?: "created_at" | "year" | "satisfaction_score";
  order?: "asc" | "desc";
  limit?: number;
  offset?: number;
};

export function listUserStories(
  params: ListUserStoriesParams = {},
): Promise<UserStoryListResponse> {
  return apiGet<UserStoryListResponse>(
    `/api/v1/user-stories${queryString({
      origin_country_slug: params.originCountrySlug,
      destination_country_slug: params.destinationCountrySlug,
      scenario: params.scenario,
      verification_status: params.verificationStatus,
      is_synthetic: params.isSynthetic,
      status: params.status,
      sort: params.sort,
      order: params.order,
      limit: params.limit,
      offset: params.offset,
    })}`,
  );
}

export function getUserStory(storyId: string): Promise<UserStoryResponse> {
  return apiGet<UserStoryResponse>(`/api/v1/user-stories/${storyId}`);
}

export function createUserStory(
  payload: UserStoryCreate,
): Promise<UserStoryResponse> {
  return apiPost<UserStoryResponse, UserStoryCreate>(
    "/api/v1/user-stories",
    payload,
  );
}

export const userStoriesApi = {
  listUserStories,
  getUserStory,
  createUserStory,
};

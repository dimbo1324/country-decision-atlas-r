import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { userStoriesApi } from "../../shared/api/user-stories";
import type { UserStoryCreate } from "../../shared/api/user-stories";

type ListUserStoriesFilters = {
  destinationCountrySlug?: string;
  scenario?: string;
  isSynthetic?: boolean;
  limit?: number;
};

const USER_STORIES_QUERY_KEY = (filters: ListUserStoriesFilters) =>
  ["user-stories", filters] as const;

export function userStoriesQuery(filters: ListUserStoriesFilters = {}) {
  return queryOptions({
    queryKey: USER_STORIES_QUERY_KEY(filters),
    queryFn: () =>
      userStoriesApi.listUserStories({
        destinationCountrySlug: filters.destinationCountrySlug,
        scenario: filters.scenario,
        isSynthetic: filters.isSynthetic,
        status: "published",
        limit: filters.limit ?? 20,
      }),
    staleTime: 30_000,
  });
}

export function useCreateUserStoryMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserStoryCreate) =>
      userStoriesApi.createUserStory(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["user-stories"] });
    },
  });
}

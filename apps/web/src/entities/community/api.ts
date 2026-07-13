import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  communityApi,
  type CommunityAnswerCreate,
  type CommunityQuestionCreate,
  type CommunityVoteCreate,
  type DataErrorReportCreate,
  type UserStoryRatingCreate,
} from "../../shared/api/community";

export function communityQuestionsQuery(countrySlug: string) {
  return queryOptions({
    queryKey: ["community", "questions", countrySlug] as const,
    queryFn: () => communityApi.listCommunityQuestions({ country_slug: countrySlug }),
    staleTime: 30_000,
  });
}

export function communityAnswersQuery(questionId: string) {
  return queryOptions({
    queryKey: ["community", "answers", questionId] as const,
    queryFn: () => communityApi.listCommunityAnswers(questionId),
    staleTime: 30_000,
  });
}

function useInvalidateCommunityQuestions(countrySlug: string) {
  const queryClient = useQueryClient();
  return () =>
    queryClient.invalidateQueries({
      queryKey: ["community", "questions", countrySlug],
    });
}

export function useCreateCommunityQuestionMutation(countrySlug: string) {
  const invalidate = useInvalidateCommunityQuestions(countrySlug);
  return useMutation({
    mutationFn: (payload: CommunityQuestionCreate) =>
      communityApi.createCommunityQuestion(payload),
    onSuccess: invalidate,
  });
}

export function useCreateCommunityAnswerMutation(questionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CommunityAnswerCreate) =>
      communityApi.createCommunityAnswer(questionId, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["community", "answers", questionId],
      }),
  });
}

export function useVoteCommunityAnswerMutation(questionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      answerId,
      payload,
    }: {
      answerId: string;
      payload: CommunityVoteCreate;
    }) => communityApi.voteCommunityAnswer(answerId, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["community", "answers", questionId],
      }),
  });
}

export function useCreateDataErrorReportMutation() {
  return useMutation({
    mutationFn: (payload: DataErrorReportCreate) =>
      communityApi.createDataErrorReport(payload),
  });
}

export function useCreateUserStoryRatingMutation() {
  return useMutation({
    mutationFn: (payload: UserStoryRatingCreate) =>
      communityApi.createUserStoryRating(payload),
  });
}

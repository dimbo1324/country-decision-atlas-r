import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import {
  communityApi,
  type CommunityAnswerCreate,
  type CommunityQuestionCreate,
  type CommunityStatusUpdateRequest,
  type CommunityVoteCreate,
  type DataErrorReportCreate,
  type DataErrorReportStatusUpdateRequest,
  type UserStoryRatingCreate,
  type UserStoryRatingStatusUpdateRequest,
} from "../../shared/api/community";

export function communityQuestionsQuery(countrySlug: string) {
  return queryOptions({
    queryKey: ["community", "questions", countrySlug] as const,
    queryFn: () =>
      communityApi.listCommunityQuestions({ country_slug: countrySlug }),
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

export function adminCommunityQuestionsQuery(status?: string) {
  return queryOptions({
    queryKey: ["community", "admin", "questions", status ?? "all"] as const,
    queryFn: () => communityApi.listAdminCommunityQuestions(status),
  });
}

export function adminCommunityAnswersQuery(status?: string) {
  return queryOptions({
    queryKey: ["community", "admin", "answers", status ?? "all"] as const,
    queryFn: () => communityApi.listAdminCommunityAnswers(status),
  });
}

export function adminDataErrorReportsQuery(status?: string) {
  return queryOptions({
    queryKey: [
      "community",
      "admin",
      "data-error-reports",
      status ?? "all",
    ] as const,
    queryFn: () => communityApi.listAdminDataErrorReports(status),
  });
}

export function adminUserStoryRatingsQuery(status?: string) {
  return queryOptions({
    queryKey: [
      "community",
      "admin",
      "user-story-ratings",
      status ?? "all",
    ] as const,
    queryFn: () => communityApi.listAdminUserStoryRatings(status),
  });
}

function useInvalidateCommunityAdmin() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: ["community", "admin"] });
  };
}

export function useUpdateCommunityQuestionStatusMutation() {
  const invalidate = useInvalidateCommunityAdmin();
  return useMutation({
    mutationFn: ({
      questionId,
      payload,
    }: {
      questionId: string;
      payload: CommunityStatusUpdateRequest;
    }) => communityApi.updateCommunityQuestionStatus(questionId, payload),
    onSuccess: invalidate,
  });
}

export function useUpdateCommunityAnswerStatusMutation() {
  const invalidate = useInvalidateCommunityAdmin();
  return useMutation({
    mutationFn: ({
      answerId,
      payload,
    }: {
      answerId: string;
      payload: CommunityStatusUpdateRequest;
    }) => communityApi.updateCommunityAnswerStatus(answerId, payload),
    onSuccess: invalidate,
  });
}

export function useUpdateDataErrorReportStatusMutation() {
  const invalidate = useInvalidateCommunityAdmin();
  return useMutation({
    mutationFn: ({
      reportId,
      payload,
    }: {
      reportId: string;
      payload: DataErrorReportStatusUpdateRequest;
    }) => communityApi.updateDataErrorReportStatus(reportId, payload),
    onSuccess: invalidate,
  });
}

export function useUpdateUserStoryRatingStatusMutation() {
  const invalidate = useInvalidateCommunityAdmin();
  return useMutation({
    mutationFn: ({
      ratingId,
      payload,
    }: {
      ratingId: string;
      payload: UserStoryRatingStatusUpdateRequest;
    }) => communityApi.updateUserStoryRatingStatus(ratingId, payload),
    onSuccess: invalidate,
  });
}

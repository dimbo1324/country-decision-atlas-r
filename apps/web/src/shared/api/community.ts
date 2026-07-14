import type { components } from "@country-decision-atlas/contracts/generated/types";

import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch, apiPost, queryString } from "./http";

export type CommunityQuestion = components["schemas"]["CommunityQuestion"];
export type CommunityQuestionCreate =
  components["schemas"]["CommunityQuestionCreate"];
export type CommunityQuestionListResponse =
  components["schemas"]["CommunityQuestionListResponse"];
export type CommunityAnswer = components["schemas"]["CommunityAnswer"];
export type CommunityAnswerCreate =
  components["schemas"]["CommunityAnswerCreate"];
export type CommunityVoteCreate = components["schemas"]["CommunityVoteCreate"];
export type ConsensusSummary = components["schemas"]["ConsensusSummary"];
export type DataErrorReport = components["schemas"]["DataErrorReport"];
export type DataErrorReportCreate =
  components["schemas"]["DataErrorReportCreate"];
export type UserStoryRating = components["schemas"]["UserStoryRating"];
export type UserStoryRatingCreate =
  components["schemas"]["UserStoryRatingCreate"];
export type CommunityStatusUpdateRequest =
  components["schemas"]["CommunityStatusUpdateRequest"];
export type DataErrorReportStatusUpdateRequest =
  components["schemas"]["DataErrorReportStatusUpdateRequest"];
export type UserStoryRatingStatusUpdateRequest =
  components["schemas"]["UserStoryRatingStatusUpdateRequest"];

export function listCommunityQuestions(params: {
  country_slug?: string;
  topic?: string;
  limit?: number;
}): Promise<CommunityQuestionListResponse> {
  return apiGet<CommunityQuestionListResponse>(
    `/api/v1/community/questions${queryString(params)}`,
  );
}

export function listCommunityAnswers(
  questionId: string,
): Promise<CommunityAnswer[]> {
  return apiGet<CommunityAnswer[]>(
    `/api/v1/community/questions/${questionId}/answers`,
  );
}

export function createCommunityQuestion(
  payload: CommunityQuestionCreate,
): Promise<CommunityQuestion> {
  return apiPost<CommunityQuestion, CommunityQuestionCreate>(
    "/api/v1/community/questions",
    payload,
  );
}

export function createCommunityAnswer(
  questionId: string,
  payload: CommunityAnswerCreate,
): Promise<CommunityAnswer> {
  return apiPost<CommunityAnswer, CommunityAnswerCreate>(
    `/api/v1/community/questions/${questionId}/answers`,
    payload,
  );
}

export function voteCommunityAnswer(
  answerId: string,
  payload: CommunityVoteCreate,
): Promise<ConsensusSummary> {
  return apiPost<ConsensusSummary, CommunityVoteCreate>(
    `/api/v1/community/answers/${answerId}/votes`,
    payload,
  );
}

export function createDataErrorReport(
  payload: DataErrorReportCreate,
): Promise<DataErrorReport> {
  return apiPost<DataErrorReport, DataErrorReportCreate>(
    "/api/v1/community/data-error-reports",
    payload,
  );
}

export function createUserStoryRating(
  payload: UserStoryRatingCreate,
): Promise<UserStoryRating> {
  return apiPost<UserStoryRating, UserStoryRatingCreate>(
    "/api/v1/community/user-story-ratings",
    payload,
  );
}

export function listAdminCommunityQuestions(
  status?: string,
): Promise<CommunityQuestion[]> {
  return apiGet<CommunityQuestion[]>(
    `/api/v1/admin/community/questions${queryString({ status })}`,
    { headers: csrfHeaders() },
  );
}

export function updateCommunityQuestionStatus(
  questionId: string,
  payload: CommunityStatusUpdateRequest,
): Promise<CommunityQuestion> {
  return apiPatch<CommunityQuestion, CommunityStatusUpdateRequest>(
    `/api/v1/admin/community/questions/${questionId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listAdminCommunityAnswers(
  status?: string,
): Promise<CommunityAnswer[]> {
  return apiGet<CommunityAnswer[]>(
    `/api/v1/admin/community/answers${queryString({ status })}`,
    { headers: csrfHeaders() },
  );
}

export function updateCommunityAnswerStatus(
  answerId: string,
  payload: CommunityStatusUpdateRequest,
): Promise<CommunityAnswer> {
  return apiPatch<CommunityAnswer, CommunityStatusUpdateRequest>(
    `/api/v1/admin/community/answers/${answerId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listAdminDataErrorReports(
  status?: string,
): Promise<DataErrorReport[]> {
  return apiGet<DataErrorReport[]>(
    `/api/v1/admin/community/data-error-reports${queryString({ status })}`,
    { headers: csrfHeaders() },
  );
}

export function updateDataErrorReportStatus(
  reportId: string,
  payload: DataErrorReportStatusUpdateRequest,
): Promise<DataErrorReport> {
  return apiPatch<DataErrorReport, DataErrorReportStatusUpdateRequest>(
    `/api/v1/admin/community/data-error-reports/${reportId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listAdminUserStoryRatings(
  status?: string,
): Promise<UserStoryRating[]> {
  return apiGet<UserStoryRating[]>(
    `/api/v1/admin/community/user-story-ratings${queryString({ status })}`,
    { headers: csrfHeaders() },
  );
}

export function updateUserStoryRatingStatus(
  ratingId: string,
  payload: UserStoryRatingStatusUpdateRequest,
): Promise<UserStoryRating> {
  return apiPatch<UserStoryRating, UserStoryRatingStatusUpdateRequest>(
    `/api/v1/admin/community/user-story-ratings/${ratingId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export const communityApi = {
  listCommunityQuestions,
  listCommunityAnswers,
  createCommunityQuestion,
  createCommunityAnswer,
  voteCommunityAnswer,
  createDataErrorReport,
  createUserStoryRating,
  listAdminCommunityQuestions,
  updateCommunityQuestionStatus,
  listAdminCommunityAnswers,
  updateCommunityAnswerStatus,
  listAdminDataErrorReports,
  updateDataErrorReportStatus,
  listAdminUserStoryRatings,
  updateUserStoryRatingStatus,
};

import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPatch, apiPost, queryString } from "./http";

export type MigrationBoardPostListResponse =
  components["schemas"]["MigrationBoardPostListResponse"];
export type MigrationBoardPostDetail =
  components["schemas"]["MigrationBoardPostDetail"];
export type MyMigrationBoardPost =
  components["schemas"]["MyMigrationBoardPost"];
export type MyMigrationBoardPostListResponse =
  components["schemas"]["MyMigrationBoardPostListResponse"];
export type CreateMigrationBoardPostRequest =
  components["schemas"]["CreateMigrationBoardPostRequest"];
export type UpdateMigrationBoardPostRequest =
  components["schemas"]["UpdateMigrationBoardPostRequest"];
export type ContactRequestListResponse =
  components["schemas"]["ContactRequestListResponse"];
export type ContactRequestResponse =
  components["schemas"]["ContactRequestResponse"];
export type CreateContactRequestRequest =
  components["schemas"]["CreateContactRequestRequest"];
export type CreateMigrationBoardReportRequest =
  components["schemas"]["CreateMigrationBoardReportRequest"];
export type MigrationBoardReportResponse =
  components["schemas"]["MigrationBoardReportResponse"];
export type CompanionMatchesResponse =
  components["schemas"]["CompanionMatchesResponse"];
export type AdminMigrationBoardPostListResponse =
  components["schemas"]["AdminMigrationBoardPostListResponse"];
export type MigrationBoardReportListResponse =
  components["schemas"]["MigrationBoardReportListResponse"];
export type ModerateMigrationBoardPostRequest =
  components["schemas"]["ModerateMigrationBoardPostRequest"];
export type ReviewMigrationBoardReportRequest =
  components["schemas"]["ReviewMigrationBoardReportRequest"];
export type BlockedUserListResponse =
  components["schemas"]["BlockedUserListResponse"];

export type BoardPostFilters = {
  destination_country?: string;
  origin_country?: string;
  route_id?: string;
  scenario?: string;
  persona?: string;
  timeline_window?: string;
  migration_stage?: string;
  companion_goal?: string;
  household_type?: string;
  preferred_language?: string;
  tag?: string;
  visibility?: string;
  limit?: number;
  offset?: number;
};

export function listBoardPosts(
  filters: BoardPostFilters = {},
): Promise<MigrationBoardPostListResponse> {
  return apiGet<MigrationBoardPostListResponse>(
    `/api/v1/migration-board/posts${queryString(filters)}`,
    { headers: csrfHeaders() },
  );
}

export function getBoardPost(
  postId: string,
): Promise<MigrationBoardPostDetail> {
  return apiGet<MigrationBoardPostDetail>(
    `/api/v1/migration-board/posts/${postId}`,
    {
      headers: csrfHeaders(),
    },
  );
}

export function listMyBoardPosts(): Promise<MyMigrationBoardPostListResponse> {
  return apiGet<MyMigrationBoardPostListResponse>(
    "/api/v1/me/migration-board/posts",
    {
      headers: csrfHeaders(),
    },
  );
}

export function createBoardPost(
  payload: CreateMigrationBoardPostRequest,
): Promise<MyMigrationBoardPost> {
  return apiPost<MyMigrationBoardPost, CreateMigrationBoardPostRequest>(
    "/api/v1/me/migration-board/posts",
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateBoardPost(
  postId: string,
  payload: UpdateMigrationBoardPostRequest,
): Promise<MyMigrationBoardPost> {
  return apiPatch<MyMigrationBoardPost, UpdateMigrationBoardPostRequest>(
    `/api/v1/me/migration-board/posts/${postId}`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function submitBoardPost(
  postId: string,
): Promise<{ post: MyMigrationBoardPost }> {
  return apiPost<{ post: MyMigrationBoardPost }, Record<string, never>>(
    `/api/v1/me/migration-board/posts/${postId}/submit`,
    {},
    { headers: csrfHeaders() },
  );
}

export function archiveBoardPost(
  postId: string,
): Promise<{ post: MyMigrationBoardPost }> {
  return apiPost<{ post: MyMigrationBoardPost }, Record<string, never>>(
    `/api/v1/me/migration-board/posts/${postId}/archive`,
    {},
    { headers: csrfHeaders() },
  );
}

export function listCompanionMatches(
  postId?: string,
): Promise<CompanionMatchesResponse> {
  const path = postId
    ? `/api/v1/me/migration-board/posts/${postId}/matches`
    : "/api/v1/me/migration-board/matches";
  return apiGet<CompanionMatchesResponse>(path, { headers: csrfHeaders() });
}

export function createContactRequest(
  postId: string,
  payload: CreateContactRequestRequest,
): Promise<ContactRequestResponse> {
  return apiPost<ContactRequestResponse, CreateContactRequestRequest>(
    `/api/v1/migration-board/posts/${postId}/contact-requests`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listIncomingContactRequests(): Promise<ContactRequestListResponse> {
  return apiGet<ContactRequestListResponse>(
    "/api/v1/me/migration-board/contact-requests/incoming",
    { headers: csrfHeaders() },
  );
}

export function listOutgoingContactRequests(): Promise<ContactRequestListResponse> {
  return apiGet<ContactRequestListResponse>(
    "/api/v1/me/migration-board/contact-requests/outgoing",
    { headers: csrfHeaders() },
  );
}

export function acceptContactRequest(
  requestId: string,
): Promise<{ request: ContactRequestResponse }> {
  return apiPost<
    { request: ContactRequestResponse },
    { response_note?: string | null }
  >(
    `/api/v1/me/migration-board/contact-requests/${requestId}/accept`,
    {},
    { headers: csrfHeaders() },
  );
}

export function declineContactRequest(
  requestId: string,
): Promise<{ request: ContactRequestResponse }> {
  return apiPost<
    { request: ContactRequestResponse },
    { response_note?: string | null }
  >(
    `/api/v1/me/migration-board/contact-requests/${requestId}/decline`,
    {},
    { headers: csrfHeaders() },
  );
}

export function cancelContactRequest(
  requestId: string,
): Promise<{ request: ContactRequestResponse }> {
  return apiPost<{ request: ContactRequestResponse }, Record<string, never>>(
    `/api/v1/me/migration-board/contact-requests/${requestId}/cancel`,
    {},
    { headers: csrfHeaders() },
  );
}

export function reportPost(
  postId: string,
  payload: CreateMigrationBoardReportRequest,
): Promise<MigrationBoardReportResponse> {
  return apiPost<
    MigrationBoardReportResponse,
    CreateMigrationBoardReportRequest
  >(`/api/v1/migration-board/posts/${postId}/report`, payload, {
    headers: csrfHeaders(),
  });
}

export function blockUser(userId: string, reason?: string): Promise<unknown> {
  return apiPost<unknown, { reason?: string }>(
    `/api/v1/me/migration-board/blocks/${userId}`,
    { reason },
    { headers: csrfHeaders() },
  );
}

export function unblockUser(userId: string): Promise<void> {
  return apiDelete<void>(`/api/v1/me/migration-board/blocks/${userId}`, {
    headers: csrfHeaders(),
  });
}

export function listBlockedUsers(): Promise<BlockedUserListResponse> {
  return apiGet<BlockedUserListResponse>("/api/v1/me/migration-board/blocks", {
    headers: csrfHeaders(),
  });
}

export function listAdminBoardPosts(
  status?: string,
): Promise<AdminMigrationBoardPostListResponse> {
  return apiGet<AdminMigrationBoardPostListResponse>(
    `/api/v1/admin/migration-board/posts${queryString({ status })}`,
    { headers: csrfHeaders() },
  );
}

export function approveAdminBoardPost(postId: string): Promise<unknown> {
  return apiPost<unknown, Record<string, never>>(
    `/api/v1/admin/migration-board/posts/${postId}/approve`,
    {},
    { headers: csrfHeaders() },
  );
}

export function rejectAdminBoardPost(
  postId: string,
  payload: ModerateMigrationBoardPostRequest,
): Promise<unknown> {
  return apiPost<unknown, ModerateMigrationBoardPostRequest>(
    `/api/v1/admin/migration-board/posts/${postId}/reject`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function hideAdminBoardPost(
  postId: string,
  payload: ModerateMigrationBoardPostRequest,
): Promise<unknown> {
  return apiPost<unknown, ModerateMigrationBoardPostRequest>(
    `/api/v1/admin/migration-board/posts/${postId}/hide`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listAdminBoardReports(): Promise<MigrationBoardReportListResponse> {
  return apiGet<MigrationBoardReportListResponse>(
    "/api/v1/admin/migration-board/reports",
    { headers: csrfHeaders() },
  );
}

export function resolveAdminBoardReport(
  reportId: string,
  payload: ReviewMigrationBoardReportRequest,
): Promise<unknown> {
  return apiPost<unknown, ReviewMigrationBoardReportRequest>(
    `/api/v1/admin/migration-board/reports/${reportId}/resolve`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function dismissAdminBoardReport(
  reportId: string,
  payload: ReviewMigrationBoardReportRequest,
): Promise<unknown> {
  return apiPost<unknown, ReviewMigrationBoardReportRequest>(
    `/api/v1/admin/migration-board/reports/${reportId}/dismiss`,
    payload,
    { headers: csrfHeaders() },
  );
}

export const migrationBoardApi = {
  listBoardPosts,
  getBoardPost,
  listMyBoardPosts,
  createBoardPost,
  updateBoardPost,
  submitBoardPost,
  archiveBoardPost,
  listCompanionMatches,
  createContactRequest,
  listIncomingContactRequests,
  listOutgoingContactRequests,
  acceptContactRequest,
  declineContactRequest,
  cancelContactRequest,
  reportPost,
  blockUser,
  unblockUser,
  listBlockedUsers,
  listAdminBoardPosts,
  approveAdminBoardPost,
  rejectAdminBoardPost,
  hideAdminBoardPost,
  listAdminBoardReports,
  resolveAdminBoardReport,
  dismissAdminBoardReport,
};

import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPatch, apiPost } from "./http";

export type AdminUser = components["schemas"]["AdminUser"];
export type AdminUserListResponse =
  components["schemas"]["AdminUserListResponse"];
export type RoleUpdateRequest = components["schemas"]["RoleUpdateRequest"];
export type UserStatusUpdateRequest =
  components["schemas"]["UserStatusUpdateRequest"];
export type AuthSession = components["schemas"]["AuthSession"];
export type UserSessionListResponse =
  components["schemas"]["UserSessionListResponse"];
export type RevokeAllSessionsResponse =
  components["schemas"]["RevokeAllSessionsResponse"];

export function listAdminUsers(): Promise<AdminUserListResponse> {
  return apiGet<AdminUserListResponse>("/api/v1/admin/users", {
    headers: csrfHeaders(),
  });
}

export function updateUserRole(
  userId: string,
  payload: RoleUpdateRequest,
): Promise<AdminUser> {
  return apiPatch<AdminUser, RoleUpdateRequest>(
    `/api/v1/admin/users/${userId}/role`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function updateUserStatus(
  userId: string,
  payload: UserStatusUpdateRequest,
): Promise<AdminUser> {
  return apiPatch<AdminUser, UserStatusUpdateRequest>(
    `/api/v1/admin/users/${userId}/status`,
    payload,
    { headers: csrfHeaders() },
  );
}

export function listUserSessions(
  userId: string,
): Promise<UserSessionListResponse> {
  return apiGet<UserSessionListResponse>(
    `/api/v1/admin/users/${userId}/sessions`,
    { headers: csrfHeaders() },
  );
}

export function revokeAllUserSessions(
  userId: string,
): Promise<RevokeAllSessionsResponse> {
  return apiPost<RevokeAllSessionsResponse, Record<string, never>>(
    `/api/v1/admin/users/${userId}/sessions/revoke-all`,
    {},
    { headers: csrfHeaders() },
  );
}

export const adminUsersApi = {
  listAdminUsers,
  updateUserRole,
  updateUserStatus,
  listUserSessions,
  revokeAllUserSessions,
};

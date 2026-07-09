import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPost } from "./http";

export type AuthUser = components["schemas"]["AuthUser"];
export type AuthSession = components["schemas"]["AuthSession"];
export type AuthTokenResponse = components["schemas"]["AuthTokenResponse"];
export type RegisterRequest = components["schemas"]["RegisterRequest"];
export type LoginRequest = components["schemas"]["LoginRequest"];
export type CurrentUserResponse = components["schemas"]["CurrentUserResponse"];
export type UserSessionListResponse =
  components["schemas"]["UserSessionListResponse"];
export type TelegramLinkRequest = components["schemas"]["TelegramLinkRequest"];
export type TelegramLinkResponse =
  components["schemas"]["TelegramLinkResponse"];
export type TelegramLinkStatusResponse =
  components["schemas"]["TelegramLinkStatusResponse"];
export type RevokeAllSessionsRequest =
  components["schemas"]["RevokeAllSessionsRequest"];
export type SecurityNotification =
  components["schemas"]["SecurityNotification"];
export type SecurityNotificationListResponse =
  components["schemas"]["SecurityNotificationListResponse"];

export function register(payload: RegisterRequest): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse, RegisterRequest>(
    "/api/v1/auth/register",
    payload,
  );
}

export function login(payload: LoginRequest): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse, LoginRequest>(
    "/api/v1/auth/login",
    payload,
  );
}

export function logout(): Promise<{ ok: boolean }> {
  return apiPost<{ ok: boolean }, Record<string, never>>(
    "/api/v1/auth/logout",
    {},
    { headers: csrfHeaders() },
  );
}

export function getMe(): Promise<CurrentUserResponse> {
  return apiGet<CurrentUserResponse>("/api/v1/auth/me", {
    headers: csrfHeaders(),
  });
}

export function listSessions(): Promise<UserSessionListResponse> {
  return apiGet<UserSessionListResponse>("/api/v1/auth/sessions", {
    headers: csrfHeaders(),
  });
}

export function revokeSession(sessionId: string): Promise<{ ok: boolean }> {
  return apiDelete<{ ok: boolean }>(`/api/v1/auth/sessions/${sessionId}`, {
    headers: csrfHeaders(),
  });
}

export function revokeAllSessions(
  currentPassword: string,
): Promise<{ revoked_count: number }> {
  return apiPost<{ revoked_count: number }, RevokeAllSessionsRequest>(
    "/api/v1/auth/sessions/revoke-all",
    { current_password: currentPassword },
    { headers: csrfHeaders() },
  );
}

export function listSecurityNotifications(): Promise<SecurityNotificationListResponse> {
  return apiGet<SecurityNotificationListResponse>(
    "/api/v1/auth/security-notifications",
    { headers: csrfHeaders() },
  );
}

export function acknowledgeSecurityNotification(
  notificationId: string,
): Promise<{ ok: boolean }> {
  return apiPost<{ ok: boolean }, Record<string, never>>(
    `/api/v1/auth/security-notifications/${notificationId}/ack`,
    {},
    { headers: csrfHeaders() },
  );
}

export function linkTelegram(code: string): Promise<TelegramLinkResponse> {
  return apiPost<TelegramLinkResponse, TelegramLinkRequest>(
    "/api/v1/auth/telegram/link",
    { code },
    { headers: csrfHeaders() },
  );
}

export function unlinkTelegram(): Promise<{ ok: boolean }> {
  return apiDelete<{ ok: boolean }>("/api/v1/auth/telegram/link", {
    headers: csrfHeaders(),
  });
}

export function getTelegramLinkStatus(): Promise<TelegramLinkStatusResponse> {
  return apiGet<TelegramLinkStatusResponse>("/api/v1/auth/telegram/link", {
    headers: csrfHeaders(),
  });
}

export const authApi = {
  register,
  login,
  logout,
  getMe,
  listSessions,
  revokeSession,
  revokeAllSessions,
  listSecurityNotifications,
  acknowledgeSecurityNotification,
  linkTelegram,
  unlinkTelegram,
  getTelegramLinkStatus,
};

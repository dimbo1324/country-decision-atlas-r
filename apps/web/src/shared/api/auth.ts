import type { components } from "@country-decision-atlas/contracts/generated/types";
import { authHeaders } from "../auth/session";
import { apiDelete, apiGet, apiPost } from "./http";

export type AuthUser = components["schemas"]["AuthUser"];
export type AuthSession = components["schemas"]["AuthSession"];
export type AuthTokenResponse = components["schemas"]["AuthTokenResponse"];
export type RegisterRequest = components["schemas"]["RegisterRequest"];
export type LoginRequest = components["schemas"]["LoginRequest"];
export type CurrentUserResponse = components["schemas"]["CurrentUserResponse"];
export type UserSessionListResponse = components["schemas"]["UserSessionListResponse"];
export type TelegramLinkRequest = components["schemas"]["TelegramLinkRequest"];
export type TelegramLinkResponse = components["schemas"]["TelegramLinkResponse"];
export type TelegramLinkStatusResponse =
  components["schemas"]["TelegramLinkStatusResponse"];

export function register(payload: RegisterRequest): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse, RegisterRequest>("/api/v1/auth/register", payload);
}

export function login(payload: LoginRequest): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse, LoginRequest>("/api/v1/auth/login", payload);
}

export function logout(): Promise<{ ok: boolean }> {
  return apiPost<{ ok: boolean }, Record<string, never>>(
    "/api/v1/auth/logout",
    {},
    { headers: authHeaders() },
  );
}

export function getMe(): Promise<CurrentUserResponse> {
  return apiGet<CurrentUserResponse>("/api/v1/auth/me", { headers: authHeaders() });
}

export function listSessions(): Promise<UserSessionListResponse> {
  return apiGet<UserSessionListResponse>("/api/v1/auth/sessions", {
    headers: authHeaders(),
  });
}

export function revokeSession(sessionId: string): Promise<{ ok: boolean }> {
  return apiDelete<{ ok: boolean }>(`/api/v1/auth/sessions/${sessionId}`, {
    headers: authHeaders(),
  });
}

export function revokeAllSessions(): Promise<{ revoked_count: number }> {
  return apiPost<{ revoked_count: number }, Record<string, never>>(
    "/api/v1/auth/sessions/revoke-all",
    {},
    { headers: authHeaders() },
  );
}

export function linkTelegram(code: string): Promise<TelegramLinkResponse> {
  return apiPost<TelegramLinkResponse, TelegramLinkRequest>(
    "/api/v1/auth/telegram/link",
    { code },
    { headers: authHeaders() },
  );
}

export function unlinkTelegram(): Promise<{ ok: boolean }> {
  return apiDelete<{ ok: boolean }>("/api/v1/auth/telegram/link", {
    headers: authHeaders(),
  });
}

export function getTelegramLinkStatus(): Promise<TelegramLinkStatusResponse> {
  return apiGet<TelegramLinkStatusResponse>("/api/v1/auth/telegram/link", {
    headers: authHeaders(),
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
  linkTelegram,
  unlinkTelegram,
  getTelegramLinkStatus,
};

import type { APIRequestContext } from "@playwright/test";
import { API_BASE_URL } from "./env";

export interface SeededUser {
  email: string;
  password: string;
  displayName: string;
}

let counter = 0;

export function uniqueEmail(prefix: string): string {
  counter += 1;
  return `${prefix}-${Date.now()}-${counter}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

/** Registers a user directly against the API instead of driving the
 * `/register` form — the same endpoint the form submits to
 * (`POST /api/v1/auth/register`) already sets session cookies on success,
 * so this produces a real, indistinguishable session in ~100-200ms instead
 * of the ~5-8s a full UI registration takes.
 *
 * Pass `context.request` (not the bare `request` fixture) so the response's
 * Set-Cookie headers land in that BrowserContext's cookie jar — any `page`
 * created from the same `context` will then already be authenticated, no
 * extra wiring needed. */
export async function createUserViaApi(
  request: APIRequestContext,
  overrides?: Partial<SeededUser>,
): Promise<SeededUser> {
  const user: SeededUser = {
    email: overrides?.email ?? uniqueEmail("e2e-user"),
    password: overrides?.password ?? "a-very-strong-password-123",
    displayName: overrides?.displayName ?? "E2E Seeded User",
  };

  const response = await request.post(`${API_BASE_URL}/api/v1/auth/register`, {
    data: {
      email: user.email,
      password: user.password,
      display_name: user.displayName,
    },
  });

  if (!response.ok()) {
    throw new Error(
      `createUserViaApi: POST /auth/register failed with ${response.status()}: ${await response.text()}`,
    );
  }

  return user;
}

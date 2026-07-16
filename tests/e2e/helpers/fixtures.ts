import { test as base } from "@playwright/test";
import { createUserViaApi, type SeededUser } from "./auth";
import { WEB_BASE_URL } from "./env";

interface AuthFixtures {
  seededUser: SeededUser;
}

// Mirrors apps/web/src/shared/auth/session.ts's setSessionHint() exactly:
// a first-party, non-httpOnly `cda_session_hint=1` cookie the frontend sets
// on its OWN origin right after a successful auth check, deliberately
// separate from the API's own Set-Cookie session/CSRF cookies (which may
// live on a different origin entirely). AuthProvider gates its mount-time
// `/auth/me` check behind this hint — seeding a session purely via
// `context.request` never runs that frontend JS, so without also setting
// this cookie here, the app would still render as fully anonymous even
// though the browser already holds a valid session.
const SESSION_HINT_COOKIE_NAME = "cda_session_hint";

/** `page`/`context` extended with a `seededUser` fixture: a real,
 * API-registered account already logged into that test's `context` before
 * the test body runs — skips the `/register` UI flow for tests that don't
 * care how the session was created, just that one exists.
 *
 * Deliberately test-scoped, not worker-scoped: Playwright already gives
 * each test its own fresh `context`, so this is the natural safe scope —
 * a worker-scoped shared user would save a further ~100ms per test at the
 * cost of specs that assert exact state counts (empty-state checks, item
 * counts) becoming order-dependent on whatever a previous test in the same
 * worker left behind. */
export const test = base.extend<AuthFixtures>({
  seededUser: async ({ context }, use) => {
    const user = await createUserViaApi(context.request);
    await context.addCookies([
      {
        name: SESSION_HINT_COOKIE_NAME,
        value: "1",
        url: WEB_BASE_URL,
      },
    ]);
    await use(user);
  },
});

export { expect } from "@playwright/test";

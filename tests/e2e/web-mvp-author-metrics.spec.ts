import { test, expect } from "./helpers/fixtures";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { API_BASE_URL } from "./helpers/env";
import { e2eRoutes } from "./helpers/routes";

test.describe("author metrics studio", () => {
  test("/account/author-metrics without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.accountAuthorMetrics);
    await expectPageReady(page);
    await expect(
      page.getByTestId("author-metrics-unauthenticated"),
    ).toBeVisible();
  });

  test("a logged-in user without the author.metrics capability sees a permission error, not a crash", async ({
    page,
    seededUser,
  }) => {
    // author.metrics is a capability-gated action (require_capability, no
    // role bypass -- confirmed in apps/api/app/core/rbac.py) granted only
    // via POST /api/v1/admin/capabilities (require_owner). There is no
    // way to grant it through the public UI, so -- matching the same
    // negative-only pattern already used for migration-board and
    // community moderation -- this test covers the real, reachable
    // behavior for a freshly registered user rather than a full create
    // flow that would require owner-level test setup this suite doesn't
    // have.
    await page.goto(e2eRoutes.accountAuthorMetrics);
    await expect(page.getByTestId("author-metrics-studio")).toBeVisible();
    await expect(page.locator("body")).toContainText(
      /insufficient_capability|Что-то пошло не так/i,
    );
    await expectNoAppCrash(page);
  });

  test("public author profile page renders for any user id without crashing", async ({
    page,
    seededUser,
  }) => {
    // fetch() needs a real page origin to run from -- the seededUser
    // fixture only sets cookies, it never navigates `page` (still
    // about:blank at this point without a goto first).
    await page.goto(e2eRoutes.account);
    const me = await page.evaluate(async (apiBaseUrl) => {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
        credentials: "include",
      });
      return (await response.json()) as { user: { id: string } };
    }, API_BASE_URL);

    await page.goto(e2eRoutes.authorProfile(me.user.id));
    await expect(page.getByTestId("author-profile-view")).toBeVisible();
    await expect(
      page.getByTestId("author-profile-metrics-empty-state"),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });
});

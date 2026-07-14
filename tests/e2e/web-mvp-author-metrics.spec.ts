import type { Page } from "@playwright/test";
import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { API_BASE_URL } from "./helpers/env";
import { e2eRoutes } from "./helpers/routes";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

async function registerViaUi(page: Page, email: string) {
  await page.goto(e2eRoutes.register);
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-display-name").fill("Author Metrics User");
  await page
    .getByTestId("register-password")
    .fill("a-very-strong-password-123");
  await page.getByTestId("register-submit").click();
  await expect(page).toHaveURL(new RegExp(e2eRoutes.account));
}

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
    const email = uniqueEmail("author-metrics-no-capability-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.accountAuthorMetrics);
    await expect(page.getByTestId("author-metrics-studio")).toBeVisible();
    await expect(page.locator("body")).toContainText(
      /insufficient_capability|Что-то пошло не так/i,
    );
    await expectNoAppCrash(page);
  });

  test("public author profile page renders for any user id without crashing", async ({
    page,
  }) => {
    const email = uniqueEmail("author-metrics-profile-user");
    await registerViaUi(page, email);

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

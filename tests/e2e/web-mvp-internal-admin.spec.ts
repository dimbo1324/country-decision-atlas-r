import { test, expect } from "./helpers/fixtures";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

const UNAUTHENTICATED_ROUTES: { name: string; path: string }[] = [
  {
    name: "author-metrics moderation",
    path: e2eRoutes.authorMetricsModeration,
  },
  { name: "country-proposals admin", path: e2eRoutes.countryProposalsAdmin },
  {
    name: "contradiction-candidates admin",
    path: e2eRoutes.contradictionCandidatesAdmin,
  },
  { name: "ai-drafts admin", path: e2eRoutes.aiDraftsAdmin },
  { name: "users admin", path: e2eRoutes.usersAdmin },
  { name: "translation-jobs admin", path: e2eRoutes.translationJobsAdmin },
  { name: "recompute admin", path: e2eRoutes.recomputeAdmin },
  { name: "evidence admin", path: e2eRoutes.evidenceAdmin },
];

test.describe("internal ops console", () => {
  test("the queue sidebar renders on an /internal page", async ({ page }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectPageReady(page);
    await expect(page.getByTestId("internal-sidebar")).toBeVisible();
    await expectNoAppCrash(page);
  });

  for (const route of UNAUTHENTICATED_ROUTES) {
    test(`${route.name} without a session shows an insufficient-rights notice, not a crash`, async ({
      page,
    }) => {
      await page.goto(route.path);
      await expectPageReady(page);
      await expect(page.locator("body")).toContainText(/Недостаточно прав/i);
      await expectNoAppCrash(page);
    });
  }

  test("a logged-in regular user is forbidden from the users admin queue", async ({
    page,
    seededUser,
  }) => {
    // ADMIN_ROLES/STRICT_ADMIN_ROLES-gated pages have no path to grant a
    // higher role through the public UI, so -- matching the negative-only
    // pattern used since Stage 10 -- this covers the real reachable
    // behavior for a freshly registered "user"-role account.
    await page.goto(e2eRoutes.usersAdmin);
    await expect(page.locator("body")).toContainText(/Недостаточно прав/i);
    await expectNoAppCrash(page);
  });
});

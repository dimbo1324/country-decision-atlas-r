import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("analytics event ingestion accepts anonymous event", async ({
  request,
}) => {
  const response = await request.post(
    `${API_BASE_URL}/api/v1/analytics/events`,
    {
      data: {
        event_type: "page_view",
        session_id: "playwright-session-analytics",
        source: "web",
        path: "/",
        locale: "ru",
        metadata: {
          surface: "e2e",
        },
      },
    },
  );
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.accepted).toBe(true);
  expect(body.stored).toBe(true);
  expect(body.session_id).toBeUndefined();
  expect(body.session_hash).toBeUndefined();
});

test("analytics smoke keeps core pages working", async ({ page }) => {
  await page.goto(e2eRoutes.decision());
  await expect(page.locator("h1")).toBeVisible();
  await expectNoAppCrash(page);

  await page.goto(e2eRoutes.country("russia", "ru"));
  await expect(page.locator("[data-testid='country-card']")).toBeVisible({
    timeout: 15_000,
  });
  await expectNoAppCrash(page);

  await page.goto(e2eRoutes.country("argentina", "ru"));
  await expect(page.locator("h1")).toBeVisible();
  await expectNoAppCrash(page);
});

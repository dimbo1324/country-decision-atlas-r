import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("platform features API returns seeded flags", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/platform/features`,
  );
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(
    body.items.some(
      (item: { key: string }) => item.key === "analytics_enabled",
    ),
  ).toBe(true);
});

test("data journal feature detail returns access decision", async ({
  request,
}) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/platform/features/data_journal_enabled`,
  );
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.item.key).toBe("data_journal_enabled");
  expect(body.decision.feature_key).toBe("data_journal_enabled");
});

test("country page shows public-safe data journal block when enabled", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("data-journal-block")
    .or(page.getByTestId("data-journal-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expect(page.locator("body")).not.toContainText("changed_by");
  await expect(page.locator("body")).not.toContainText("raw_diff");
  await expect(page.locator("body")).not.toContainText("internal_metadata");
  await expectNoAppCrash(page);
});

test("data journal shows API error when journal endpoint fails", async ({
  page,
}) => {
  await page.route(
    `${API_BASE_URL}/api/v1/countries/russia/data-journal**`,
    async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            code: "forced_data_journal_failure",
            message: "Forced data journal failure",
          },
        }),
      });
    },
  );

  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("data-journal-error")).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByTestId("data-journal-empty")).not.toBeVisible();
  await expectNoAppCrash(page);
});

test("old decision flow and persona selector still work", async ({ page }) => {
  await page.goto(e2eRoutes.decision());
  await expectPageReady(page);
  await expect(page.getByTestId("persona-selector")).toBeVisible();
  await expectNoAppCrash(page);
});

test("routes block still works", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("country-routes-block")).toBeVisible();
  await expectNoAppCrash(page);
});

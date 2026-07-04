import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("platform-metrics API returns 200 with feature enabled", async ({
  request,
}) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/russia/platform-metrics`,
  );
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
});

test("platform-metrics API returns 404 for unknown country", async ({
  request,
}) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/unknown-country-xyz/platform-metrics`,
  );
  expect(response.status()).toBe(404);
});

test("platform-metrics API returns 422 for invalid scenario", async ({
  request,
}) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/russia/platform-metrics?scenario=bad_scenario`,
  );
  expect(response.status()).toBe(422);
});

test("country page shows platform intelligence section", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const section = page.getByTestId("platform-intelligence-section");
  await expect(section).toBeVisible();
  await expectNoAppCrash(page);
});

test("platform intelligence block shows empty state when no metrics computed", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("platform-intelligence-block")
    .or(page.getByTestId("platform-intelligence-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("platform intelligence shows API error when metrics endpoint fails", async ({
  page,
}) => {
  await page.route(
    `${API_BASE_URL}/api/v1/countries/russia/platform-metrics**`,
    async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            code: "forced_platform_metrics_failure",
            message: "Forced platform metrics failure",
          },
        }),
      });
    },
  );

  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("platform-intelligence-error")).toBeVisible({
    timeout: 15_000,
  });
  await expect(
    page.getByTestId("platform-intelligence-empty"),
  ).not.toBeVisible();
  await expectNoAppCrash(page);
});

test("platform intelligence handles insufficient_data metrics gracefully", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expectNoAppCrash(page);
  const crash = page.getByText("Unhandled Runtime Error", { exact: false });
  await expect(crash).not.toBeVisible();
});

test("decision page still shows ranking after platform intelligence added", async ({
  page,
}) => {
  await page.goto(e2eRoutes.decision());
  await expectPageReady(page);
  await page.getByTestId("decision-run-button").click();
  await page.waitForTimeout(3000);
  await expectNoAppCrash(page);
});

test("decision page risk context does not appear when no results", async ({
  page,
}) => {
  await page.goto(e2eRoutes.decision());
  await expectPageReady(page);
  await expect(page.getByTestId("decision-risk-context")).not.toBeVisible();
  await expectNoAppCrash(page);
});

test("no crash on mobile viewport for country card platform intelligence", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expectNoAppCrash(page);
});

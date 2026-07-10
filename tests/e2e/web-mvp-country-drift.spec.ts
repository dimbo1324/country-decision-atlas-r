import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("drift API returns 200 for known country russia", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/russia/drift`,
  );
  expect(response.status()).toBe(200);
});

test("drift API returns 200 for known country uruguay", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/uruguay/drift`,
  );
  expect(response.status()).toBe(200);
});

test("drift API returns 200 for known country argentina", async ({
  request,
}) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/argentina/drift`,
  );
  expect(response.status()).toBe(200);
});

test("drift API returns 404 for unknown country", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/unknown-country-xyz/drift`,
  );
  expect(response.status()).toBe(404);
});

test("drift API response contains required shape", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/russia/drift`,
  );
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body).toHaveProperty("country_slug");
  expect(body).toHaveProperty("latest_snapshot");
  expect(body).toHaveProperty("history");
  expect(body).toHaveProperty("disclaimer");
});

test("country page shows drift section", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const section = page.getByTestId("country-drift-section");
  await expect(section).toBeVisible();
  await expectNoAppCrash(page);
});

test("russia country page renders drift block or empty state", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("country-drift-block")
    .or(page.getByTestId("country-drift-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("uruguay country page renders drift block or empty state", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("uruguay", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("country-drift-block")
    .or(page.getByTestId("country-drift-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("argentina country page renders drift block or empty state", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("argentina", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("country-drift-block")
    .or(page.getByTestId("country-drift-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("drift block shows insufficient_data state without crash when API returns empty snapshot", async ({
  page,
}) => {
  await page.route(
    `${API_BASE_URL}/api/v1/countries/russia/drift**`,
    async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          country_slug: "russia",
          latest_snapshot: null,
          history: [],
          disclaimer: "This is a contextual trend indicator, not legal advice.",
        }),
      });
    },
  );
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("country-drift-empty")).toBeVisible({
    timeout: 15_000,
  });
  await expectNoAppCrash(page);
});

test("drift block shows error state when API fails", async ({ page }) => {
  await page.route(
    `${API_BASE_URL}/api/v1/countries/russia/drift**`,
    async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            code: "forced_drift_failure",
            message: "Forced drift failure",
          },
        }),
      });
    },
  );
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("country-drift-error")).toBeVisible({
    timeout: 15_000,
  });
  await expectNoAppCrash(page);
});

test("drift block shows error state when API request hangs past the timeout", async ({
  page,
}) => {
  // apps/web/src/shared/config/env.ts::API_TIMEOUT_MS defaults to 10s;
  // this delay must stay comfortably above that default.
  test.setTimeout(45_000);
  await page.route(
    `${API_BASE_URL}/api/v1/countries/russia/drift**`,
    async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 11_000));
      await route
        .fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            country_slug: "russia",
            latest_snapshot: null,
            history: [],
            disclaimer:
              "This is a contextual trend indicator, not legal advice.",
          }),
        })
        .catch(() => undefined);
    },
  );
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expect(page.getByTestId("country-drift-error")).toBeVisible({
    timeout: 15_000,
  });
  await expectNoAppCrash(page);
});

test("no crash on mobile viewport for country drift section", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expectNoAppCrash(page);
});

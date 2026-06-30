import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("trust API returns 200 or 404 for known country", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/russia/trust`,
  );
  expect([200, 404]).toContain(response.status());
});

test("trust API returns 404 for unknown country", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/unknown-country-xyz/trust`,
  );
  expect(response.status()).toBe(404);
});

test("methodology API returns 200 with items array", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/methodology`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
});

test("glossary API returns 200 with items array", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/glossary`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
});

test("glossary API supports category filter", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/glossary?category=trust`,
  );
  expect(response.ok()).toBeTruthy();
});

test("methodology API returns 404 for unknown section", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/methodology/nonexistent-slug-xyz`,
  );
  expect(response.status()).toBe(404);
});

test("glossary API returns 404 for unknown term", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/glossary/nonexistent-slug-xyz`,
  );
  expect(response.status()).toBe(404);
});

test("country page shows trust surface section", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const section = page.getByTestId("trust-surface-section");
  await expect(section).toBeVisible();
  await expectNoAppCrash(page);
});

test("trust surface block shows badge or empty state", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("trust-surface-block")
    .or(page.getByTestId("trust-surface-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("methodology page loads without crash", async ({ page }) => {
  await page.goto("/methodology");
  await expectPageReady(page);
  const main = page.getByTestId("methodology-page");
  await expect(main).toBeVisible();
  await expectNoAppCrash(page);
});

test("no crash on mobile viewport for trust surface on country card", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await expectNoAppCrash(page);
});

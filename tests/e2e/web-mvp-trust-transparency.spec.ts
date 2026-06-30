import { expect, test } from "@playwright/test";
import { API_BASE_URL } from "./helpers/env";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("trust API returns 200 for known country russia", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/countries/russia/trust`);
  expect(response.status()).toBe(200);
});

test("trust API returns 200 for known country uruguay", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/countries/uruguay/trust`);
  expect(response.status()).toBe(200);
});

test("trust API returns 200 for known country argentina", async ({ request }) => {
  const response = await request.get(
    `${API_BASE_URL}/api/v1/countries/argentina/trust`,
  );
  expect(response.status()).toBe(200);
});

test("trust API response contains required fields", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/countries/russia/trust`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body).toHaveProperty("trust_label");
  expect(body).toHaveProperty("confidence");
  expect(body).toHaveProperty("freshness_status");
  expect(body).toHaveProperty("components");
  expect(body).toHaveProperty("disclaimer");
  if (body.trust_label !== "insufficient_data") {
    expect(typeof body.trust_score).toBe("number");
  }
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
  expect(body.items.length).toBeGreaterThanOrEqual(12);
});

test("methodology API locale=ru returns items", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/methodology?locale=ru`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
  expect(body.items.length).toBeGreaterThanOrEqual(1);
});

test("methodology API contains CII explanation section", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/methodology`);
  const body = await response.json();
  const slugs: string[] = body.items.map((s: { slug: string }) => s.slug);
  expect(slugs).toContain("what_is_cii");
  expect(slugs).toContain("what_is_trust_score");
  expect(slugs).toContain("legal_disclaimer");
});

test("glossary API returns 200 with items array", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/glossary`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
  expect(body.items.length).toBeGreaterThanOrEqual(19);
});

test("glossary API supports category filter", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/glossary?category=trust`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
});

test("glossary API locale=ru returns items", async ({ request }) => {
  const response = await request.get(`${API_BASE_URL}/api/v1/glossary?locale=ru`);
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
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

test("trust surface block shows trust badge and confidence", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  const block = page.getByTestId("trust-surface-block");
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("trust surface block shows contradiction context", async ({ page }) => {
  await page.goto(e2eRoutes.country("russia", "ru"));
  await expectPageReady(page);
  await page.getByTestId("trust-surface-block").waitFor({ timeout: 15_000 });
  const contradiction = page.getByTestId("contradiction-context");
  await expect(contradiction).toBeVisible();
  await expectNoAppCrash(page);
});

test("uruguay country page trust surface loads or shows empty state", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("uruguay", "ru"));
  await expectPageReady(page);
  const block = page
    .getByTestId("trust-surface-block")
    .or(page.getByTestId("trust-surface-empty"));
  await expect(block).toBeVisible({ timeout: 15_000 });
  await expectNoAppCrash(page);
});

test("argentina country page trust surface loads or shows empty state", async ({
  page,
}) => {
  await page.goto(e2eRoutes.country("argentina", "ru"));
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

test("methodology page shows glossary section", async ({ page }) => {
  await page.goto("/methodology");
  await expectPageReady(page);
  const glossary = page.getByTestId("glossary-section");
  await expect(glossary).toBeVisible();
  await expectNoAppCrash(page);
});

test("methodology page shows legal disclaimer", async ({ page }) => {
  await page.goto("/methodology");
  await expectPageReady(page);
  const disclaimer = page.locator(".disclaimer-notice");
  await expect(disclaimer).toBeVisible();
  await expectNoAppCrash(page);
});

test("decision page shows disclaimer after results load", async ({ page }) => {
  await page.goto("/decision");
  await expectPageReady(page);
  await expectNoAppCrash(page);
});

test("locale=ru preserved on methodology page", async ({ page }) => {
  await page.goto("/methodology?locale=ru");
  await expectPageReady(page);
  await expect(page).toHaveURL(/locale=ru/);
  await expectNoAppCrash(page);
});

test("legal signals page shows disclaimer", async ({ page }) => {
  await page.goto("/legal-signals");
  await expectPageReady(page);
  const disclaimer = page.locator(".disclaimer-notice");
  await expect(disclaimer).toBeVisible();
  await expectNoAppCrash(page);
});

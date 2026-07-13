import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("compare matrix page", () => {
  test("/compare opens with heading", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expectHasMainHeading(page, /сравнение стран по сценариям/i);
    await expectNoAppCrash(page);
  });

  test("matrix table renders", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("Russia row exists in matrix", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(page.locator('[data-testid="matrix-row-russia"]')).toBeVisible(
      {
        timeout: 10_000,
      },
    );
    await expectNoAppCrash(page);
  });

  test("Uruguay row exists in matrix", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="matrix-row-uruguay"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("Argentina row exists in matrix", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="matrix-row-argentina"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("5 scenario columns exist", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const headers = page.getByTestId("matrix-scenario-header");
    await expect(headers).toHaveCount(5);
    await expectNoAppCrash(page);
  });

  test("cells contain numeric scores", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const firstScore = page.getByTestId("matrix-cell-score").first();
    const text = await firstScore.textContent();
    expect(text).toMatch(/\d+\.\d+|—/);
    await expectNoAppCrash(page);
  });

  test("legend exists", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-legend"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("summary exists", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-summary"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("cell links exist and point to country pages", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const firstLink = page.getByTestId("matrix-cell-link").first();
    const href = await firstLink.getAttribute("href");
    expect(href).toMatch(/\/countries\//);
    await expectNoAppCrash(page);
  });

  test("responsive: /compare at 390x844 does not crash", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.compare);
    await expectHasMainHeading(page, /сравнение стран по сценариям/i);
    await expectNoAppCrash(page);
  });

  test("heatmap CSS classes applied to cells", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const hasHeatmap = await page
      .locator(
        '[data-score-band="weak"], [data-score-band="limited"], [data-score-band="moderate"], [data-score-band="strong"], [data-score-band="excellent"]',
      )
      .count();
    expect(hasHeatmap).toBeGreaterThan(0);
    await expectNoAppCrash(page);
  });
});

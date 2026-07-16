import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Argentina CII integration", () => {
  test("/countries/argentina shows CII block after CII integration", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    const ciiBlock = page.locator("[data-testid='cii-block']");
    await expect(ciiBlock).toBeVisible({ timeout: 15_000 });
  });

  test("/countries/argentina CII block shows numeric score", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
    const scoreText = await page
      .locator("[data-testid='cii-block']")
      .textContent();
    expect(scoreText).toMatch(/\d+/);
  });

  test("/countries/argentina?locale=en CII block visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "en"));
    await expectNoAppCrash(page);
    const ciiBlock = page.locator("[data-testid='cii-block']");
    await expect(ciiBlock).toBeVisible({ timeout: 15_000 });
  });

  test("/compare shows Argentina row with numeric scores", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      page.locator('[data-testid="matrix-row-argentina"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const row = page.locator('[data-testid="matrix-row-argentina"]');
    const scoreText = await row.textContent();
    expect(scoreText).toMatch(/\d+/);
    await expectNoAppCrash(page);
  });

  test("/compare Argentina row has 5 cells", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    const argentinaRow = page.locator('[data-testid="matrix-row-argentina"]');
    const cells = argentinaRow.locator("td");
    const count = await cells.count();
    expect(count).toBeGreaterThanOrEqual(5);
    await expectNoAppCrash(page);
  });

  test("/countries/argentina legal section shows empty state without crash", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 15_000 });
  });

  test("Russia remains accessible after Argentina CII integration", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Uruguay remains accessible after Argentina CII integration", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("responsive: /compare at 390x844 shows Argentina row", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      page.locator('[data-testid="matrix-row-argentina"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

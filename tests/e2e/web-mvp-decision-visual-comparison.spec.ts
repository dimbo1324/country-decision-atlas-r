import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("decision visual comparison (CII)", () => {
  test("decision page loads and old text result appears after run", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.locator("h1")).toBeVisible();

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).toBeVisible();
    await expect(runButton).not.toBeDisabled();

    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });

    await expectNoAppCrash(page);
  });

  test("CII visual comparison block appears after run with 2 candidates", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.locator("h1")).toBeVisible();

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).not.toBeDisabled();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });

    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 15_000,
    });

    await expectNoAppCrash(page);
  });

  test("CII spider chart is rendered", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).not.toBeDisabled();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.locator(".ciiSpiderChart")).toBeVisible({
      timeout: 15_000,
    });

    await expectNoAppCrash(page);
  });

  test("CII metric bars are rendered", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).not.toBeDisabled();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.locator(".ciiCompareBars")).toBeVisible({
      timeout: 15_000,
    });

    await expectNoAppCrash(page);
  });

  test("CII winner list is rendered", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).not.toBeDisabled();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.locator(".ciiWinnerList")).toBeVisible({
      timeout: 15_000,
    });

    await expectNoAppCrash(page);
  });

  test("page does not crash on reload after decision run", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).not.toBeDisabled();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });

    await page.reload();
    await expect(page.locator("h1")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

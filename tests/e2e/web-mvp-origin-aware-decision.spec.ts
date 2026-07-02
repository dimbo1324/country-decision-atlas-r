import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Origin-aware decision context", () => {
  test("user selects origin country and sees origin-aware context in results", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("origin-select")).toBeVisible();
    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("decision-run-button").click();

    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("origin-aware-context").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("old flow without origin still works", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("origin-select")).toHaveValue("");
    await page.getByTestId("decision-run-button").click();

    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("origin-aware-context")).toHaveCount(0);
    await expectNoAppCrash(page);
  });

  test("persona still works together with origin", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("persona-selector").selectOption({ index: 1 });
    await page.getByTestId("decision-run-button").click();

    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("decision-persona-meta")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("custom weights still work together with origin", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("decision-weights-panel").locator("summary").click();
    await page.getByTestId("decision-weight-slider-business_score").fill("80");
    await page.getByTestId("decision-run-button").click();

    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("decision-personalization-result")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

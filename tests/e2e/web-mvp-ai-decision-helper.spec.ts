import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("AI decision helper", () => {
  test("decision helper is visible and can suggest hints", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("ai-decision-helper")).toBeVisible();
    await page
      .getByTestId("ai-decision-intent-input")
      .fill("Я хочу переехать с семьёй, бюджет ограничен.");
    await page.getByTestId("ai-decision-intent-submit").click();
    await expect(
      page
        .getByTestId("ai-decision-result")
        .or(page.getByTestId("ai-decision-error"))
        .first(),
    ).toBeVisible({ timeout: 20_000 });
    await expectNoAppCrash(page);
  });

  test("explain number panel opens on country CII block", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("cii-block")).toBeVisible({ timeout: 20_000 });
    await page.getByTestId("ai-explain-number-button").click();
    await expect(
      page
        .getByTestId("ai-explain-number-panel")
        .or(page.getByText("Объяснение временно недоступно."))
        .first(),
    ).toBeVisible({ timeout: 20_000 });
    await expectNoAppCrash(page);
  });
});

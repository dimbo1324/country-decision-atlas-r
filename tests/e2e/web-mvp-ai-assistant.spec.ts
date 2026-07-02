import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("AI assistant", () => {
  test("assistant page opens and can ask a question", async ({ page }) => {
    await page.goto(e2eRoutes.assistant("ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("ai-assistant-page")).toBeVisible();
    await page.getByTestId("ai-question-input").fill("Что известно об Уругвае?");
    await page.getByTestId("ai-country-input").fill("uruguay");
    await page.getByTestId("ai-submit").click();

    await expect(
      page
        .getByTestId("ai-answer-card")
        .or(page.getByTestId("ai-refusal"))
        .or(page.getByTestId("ai-error"))
        .first(),
    ).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId("ai-disclaimer")).toBeVisible({ timeout: 20_000 });
    await expectNoAppCrash(page);
  });

  test("assistant page survives mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.assistant("ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("ai-assistant-page")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { goToDecisionStep } from "./helpers/decision";
import { e2eRoutes } from "./helpers/routes";

test.describe("AI assistant UI invariants", () => {
  test("a non-refused answer without citations is never rendered as plain trustworthy prose", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.assistant("ru"));
    await expectPageReady(page);

    await page
      .getByTestId("ai-question-input")
      .fill("Что известно об Уругвае?");
    await page.getByTestId("ai-country-input").fill("uruguay");
    await page.getByTestId("ai-submit").click();

    await expect(page.getByTestId("ai-answer-card")).toBeVisible({
      timeout: 20_000,
    });

    const refused = await page.getByTestId("ai-refusal").isVisible();
    if (!refused) {
      const hasCitations = await page.getByTestId("ai-citations").isVisible();
      const hasUncitedFlag = await page
        .getByTestId("ai-answer-uncited")
        .isVisible();
      // Structural invariant: a non-refused answer is either backed by
      // citations, or explicitly flagged as unverified -- never rendered
      // as plain trustworthy prose with neither.
      expect(hasCitations || hasUncitedFlag).toBe(true);
    }
    await expectNoAppCrash(page);
  });

  test("explain-number is available for the decision winner's score", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expectPageReady(page);

    await goToDecisionStep(page, 4);
    const runButton = page.getByRole("button", { name: /запустить подбор/i });
    await expect(runButton).toBeVisible();
    await runButton.click();

    await expect(page.getByTestId("decision-winner-block")).toBeVisible({
      timeout: 20_000,
    });
    const explainButton = page
      .getByTestId("decision-winner-block")
      .getByTestId("ai-explain-number-button");
    await expect(explainButton).toBeVisible();
    await explainButton.click();

    await expect(
      page
        .getByTestId("ai-explain-number-panel")
        .or(page.getByText("Объяснение временно недоступно."))
        .first(),
    ).toBeVisible({ timeout: 20_000 });
    await expectNoAppCrash(page);
  });
});

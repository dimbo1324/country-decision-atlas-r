import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

async function runDecision(page: import("@playwright/test").Page) {
  const runButton = page.getByTestId("decision-run-button");
  await expect(runButton).toBeVisible();
  await expect(runButton).not.toBeDisabled();
  await runButton.click();
  await expect(page.getByTestId("decision-results")).toBeVisible({
    timeout: 20_000,
  });
}

test.describe("Decision personalization sliders", () => {
  test("/decision opens", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.getByTestId("decision-weights-panel")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("priority sliders are visible after expanding panel", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("decision-weights-panel").locator("summary").click();
    await expect(
      page.getByTestId("decision-weight-slider-safety_score"),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("user can change safety slider", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const slider = page.getByTestId("decision-weight-slider-safety_score");
    await slider.fill("80");
    await expect(slider).toHaveValue("80");
    await expectNoAppCrash(page);
  });

  test("decision run succeeds with custom weights", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const slider = page.getByTestId("decision-weight-slider-safety_score");
    await slider.fill("80");

    await runDecision(page);
    await expectNoAppCrash(page);
  });

  test("result shows personalized calculation message", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const slider = page.getByTestId("decision-weight-slider-safety_score");
    await slider.fill("80");

    await runDecision(page);
    await expect(
      page.getByTestId("decision-personalization-result"),
    ).toContainText("Результат адаптирован под ваши приоритеты");
    await expectNoAppCrash(page);
  });

  test("reset priorities works", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const slider = page.getByTestId("decision-weight-slider-safety_score");
    await slider.fill("80");
    await expect(slider).toHaveValue("80");

    await page.getByTestId("decision-weights-reset").click();
    await expect(slider).toHaveValue("20");
    await expectNoAppCrash(page);
  });

  test("all-zero weights are blocked client-side", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const criteria = [
      "legalization_score",
      "long_term_status_score",
      "cost_of_living_score",
      "safety_score",
      "business_score",
      "legal_stability_score",
      "source_quality_score",
    ];
    for (const criterion of criteria) {
      await page.getByTestId(`decision-weight-slider-${criterion}`).fill("0");
    }

    await expect(page.getByTestId("decision-run-button")).toBeDisabled();
    await expectNoAppCrash(page);
  });

  test("persona + custom weights works together", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("persona-selector").selectOption("family");
    await page.getByTestId("decision-weights-panel").locator("summary").click();

    const slider = page.getByTestId("decision-weight-slider-safety_score");
    await slider.fill("80");

    await runDecision(page);
    await expect(
      page.getByTestId("decision-personalization-result"),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("mobile layout does not crash", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("decision-weights-panel")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

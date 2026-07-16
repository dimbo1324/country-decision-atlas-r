import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { goToDecisionStep } from "./helpers/decision";
import { e2eRoutes } from "./helpers/routes";

test.describe("Decision wizard", () => {
  test("applies a guided recommendation and runs decision", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("decision-wizard")).toBeVisible();
    await page.getByTestId("decision-wizard-toggle").click();
    await expect(page.getByTestId("decision-wizard-panel")).toBeVisible();
    await page
      .getByTestId("decision-wizard-primary-goal-option-business")
      .click();
    await page.getByTestId("decision-wizard-budget-option-high").click();
    await page
      .getByTestId("decision-wizard-business_priority-option-high")
      .click();
    await page.getByTestId("decision-wizard-apply").click();

    await expect(page.getByTestId("decision-wizard-result")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("decision-wizard-explanation")).toBeVisible();
    await expect(page.getByTestId("decision-wizard-manual-note")).toBeVisible();

    await goToDecisionStep(page, 1);
    await expect(
      page.getByTestId(
        "decision-scenario-select-option-business_self_employment",
      ),
    ).toHaveAttribute("aria-checked", "true");

    await goToDecisionStep(page, 3);
    await expect(page.getByTestId("persona-selector")).toHaveValue("investor");

    await page.getByTestId("decision-weights-panel").locator("summary").click();
    await expect(
      page.getByTestId("decision-weight-slider-business_score"),
    ).not.toHaveValue("10");

    await goToDecisionStep(page, 4);
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expectNoAppCrash(page);
  });

  test("manual form remains usable after wizard apply", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("decision-wizard-toggle").click();
    await page
      .getByTestId("decision-wizard-family-option-family_with_children")
      .click();
    await page.getByTestId("decision-wizard-apply").click();
    await expect(page.getByTestId("decision-wizard-result")).toBeVisible({
      timeout: 20_000,
    });

    await goToDecisionStep(page, 3);
    await page.getByTestId("persona-selector").selectOption("");

    await goToDecisionStep(page, 1);
    await page
      .getByTestId("decision-scenario-select-option-relocation_residence")
      .click();

    await goToDecisionStep(page, 4);
    await expect(page.getByTestId("decision-run-button")).not.toBeDisabled();
    await expectNoAppCrash(page);
  });

  test("wizard panel can be opened and closed", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("decision-wizard-panel")).toBeHidden();
    await page.getByTestId("decision-wizard-toggle").click();
    await expect(page.getByTestId("decision-wizard-panel")).toBeVisible();
    await page.getByTestId("decision-wizard-toggle").click();
    await expect(page.getByTestId("decision-wizard-panel")).toBeHidden();
    await expectNoAppCrash(page);
  });
});

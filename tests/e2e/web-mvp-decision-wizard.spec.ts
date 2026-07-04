import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
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
      .getByTestId("decision-wizard-primary-goal")
      .selectOption("business");
    await page.getByTestId("decision-wizard-budget").selectOption("high");
    await page
      .getByTestId("decision-wizard-business_priority")
      .selectOption("high");
    await page.getByTestId("decision-wizard-apply").click();

    await expect(page.getByTestId("decision-wizard-result")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("decision-wizard-explanation")).toBeVisible();
    await expect(page.getByTestId("decision-wizard-manual-note")).toBeVisible();
    await expect(page.getByTestId("decision-scenario-select")).toHaveValue(
      "business_self_employment",
    );
    await expect(page.getByTestId("persona-selector")).toHaveValue("investor");

    await page.getByTestId("decision-weights-panel").locator("summary").click();
    await expect(
      page.getByTestId("decision-weight-slider-business_score"),
    ).not.toHaveValue("10");

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
      .getByTestId("decision-wizard-family")
      .selectOption("family_with_children");
    await page.getByTestId("decision-wizard-apply").click();
    await expect(page.getByTestId("decision-wizard-result")).toBeVisible({
      timeout: 20_000,
    });

    await page.getByTestId("persona-selector").selectOption("");
    await page
      .getByTestId("decision-scenario-select")
      .selectOption("relocation_residence");
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

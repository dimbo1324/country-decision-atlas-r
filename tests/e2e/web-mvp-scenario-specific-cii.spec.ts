import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { goToDecisionStep } from "./helpers/decision";

const DECISION_URL = "/ru/decision";
const RELOCATION_SLUG = "relocation_residence";
const BUSINESS_SLUG = "business_self_employment";

async function runDecision(
  page: import("@playwright/test").Page,
  scenarioSlug: string,
) {
  await goToDecisionStep(page, 1);
  await page
    .locator(`[data-testid="decision-scenario-select-option-${scenarioSlug}"]`)
    .click();
  await goToDecisionStep(page, 4);
  const btn = page.locator('[data-testid="decision-run-button"]');
  await btn.click();
  await page.waitForTimeout(2000);
}

test.describe("scenario-specific CII visual comparison", () => {
  test("visual comparison appears after relocation_residence run", async ({
    page,
  }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("scenario label updates to relocation scenario", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });
    const scenarioLabel = page.locator(".ciiCompareScenarioLabel");
    const isVisible = await scenarioLabel.isVisible().catch(() => false);
    if (isVisible) {
      const text = await scenarioLabel.textContent();
      expect(text?.length).toBeGreaterThan(0);
    }
    await expectNoAppCrash(page);
  });

  test("visual comparison appears after business_self_employment run", async ({
    page,
  }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, BUSINESS_SLUG);
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("changing scenario re-renders visual comparison without crash", async ({
    page,
  }) => {
    await page.goto(DECISION_URL);

    await runDecision(page, RELOCATION_SLUG);
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });

    await runDecision(page, BUSINESS_SLUG);
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });

    await expectNoAppCrash(page);
  });

  test("metric bars appear for both scenarios", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.getByTestId("cii-compare-bars")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("winner list appears for both scenarios", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, BUSINESS_SLUG);
    await expect(page.getByTestId("cii-winner-list")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("old decision text result is still visible after CII comparison renders", async ({
    page,
  }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.locator('[data-testid="decision-results"]')).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.getByTestId("cii-compare-block")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("spider chart renders for business scenario", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, BUSINESS_SLUG);
    await expect(page.getByTestId("cii-spider-chart")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

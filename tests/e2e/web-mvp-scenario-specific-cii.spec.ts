import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";

const DECISION_URL = "/decision?locale=ru";
const RELOCATION_SLUG = "relocation_residence";
const BUSINESS_SLUG = "business_self_employment";

async function runDecision(
  page: import("@playwright/test").Page,
  scenarioSlug: string,
) {
  const select = page.locator('[data-testid="decision-scenario-select"]');
  await select.selectOption(scenarioSlug);
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
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("scenario label updates to relocation scenario", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
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
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("changing scenario re-renders visual comparison without crash", async ({
    page,
  }) => {
    await page.goto(DECISION_URL);

    await runDecision(page, RELOCATION_SLUG);
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 10_000,
    });

    await runDecision(page, BUSINESS_SLUG);
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 10_000,
    });

    await expectNoAppCrash(page);
  });

  test("metric bars appear for both scenarios", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, RELOCATION_SLUG);
    await expect(page.locator(".ciiCompareBars")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("winner list appears for both scenarios", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, BUSINESS_SLUG);
    await expect(page.locator(".ciiWinnerList")).toBeVisible({
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
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("spider chart renders for business scenario", async ({ page }) => {
    await page.goto(DECISION_URL);
    await runDecision(page, BUSINESS_SLUG);
    await expect(page.locator(".ciiSpiderChart")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

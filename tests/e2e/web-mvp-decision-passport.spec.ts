import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Decision Passport", () => {
  test("run decision, create passport, open saved report", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });

    await expect(page.getByTestId("decision-passport-actions")).toBeVisible();
    await page.getByTestId("create-passport-button").click();
    await expect(page.getByTestId("passport-link-block")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByTestId("passport-link")).toBeVisible();

    await page.getByTestId("passport-link").click();
    await expect(page).toHaveURL(/\/decision\/passports\/.+/);
    // Next.js 15 streaming SSR sometimes leaves an orphaned hidden
    // placeholder div for this route's Suspense boundary (confirmed via
    // the raw response: its $RC relocation call targets a different
    // boundary), so testids here can match a real but `hidden`, invisible
    // second node — .first() picks the rendered one.
    await expect(
      page.getByTestId("decision-passport-page").first(),
    ).toBeVisible();
    await expect(page.getByTestId("decision-results").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("passport page shows disclaimer, methodology, and winner", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await page.getByTestId("create-passport-button").click();
    await expect(page.getByTestId("passport-link-block")).toBeVisible({
      timeout: 20_000,
    });
    await page.getByTestId("passport-link").click();
    await expect(page).toHaveURL(/\/decision\/passports\/.+/);

    await expect(page.locator(".disclaimer-notice").first()).toBeVisible();
    // Same orphaned-hidden-placeholder streaming quirk as the previous test.
    await expect(
      page.getByTestId("passport-methodology").first(),
    ).toBeVisible();
    await expect(page.locator(".decisionWinnerBlock").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("copy link button works", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await page.getByTestId("create-passport-button").click();
    await expect(page.getByTestId("passport-link-block")).toBeVisible({
      timeout: 20_000,
    });

    await page.getByTestId("copy-passport-link").click();
    await expectNoAppCrash(page);
  });

  test("unknown passport token shows error state, not a crash", async ({
    page,
  }) => {
    await page.goto("/ru/decision/passports/unknown-token-value");
    await expect(
      page.getByText(/недоступен|not found|error/i).first(),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("old decision flow without origin still works after passport feature added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.getByTestId("origin-select")).toHaveValue("");
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expectNoAppCrash(page);
  });

  test("persona and custom weights work together with passport creation", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("persona-selector").selectOption({ index: 1 });
    await page.getByTestId("decision-weights-panel").locator("summary").click();
    await page.getByTestId("decision-weight-slider-business_score").fill("70");
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });

    await page.getByTestId("create-passport-button").click();
    await expect(page.getByTestId("passport-link-block")).toBeVisible({
      timeout: 20_000,
    });
    await expectNoAppCrash(page);
  });
});

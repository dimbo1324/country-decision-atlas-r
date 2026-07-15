import { test, expect } from "@playwright/test";

const SCREENSHOT_OPTIONS = {
  fullPage: true,
  animations: "disabled" as const,
};

test.describe("visual regression: key pages", () => {
  test("home", async ({ page }) => {
    await page.goto("/ru");
    await expect(page.getByTestId("home-overview")).toBeVisible();
    await expect(page.getByTestId("home-country-cards")).toBeVisible({
      timeout: 10_000,
    });
    await expect(page).toHaveScreenshot("home.png", SCREENSHOT_OPTIONS);
  });

  test("catalog", async ({ page }) => {
    await page.goto("/ru/countries");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByText(/россия|russia/i).first()).toBeVisible();
    await expect(page).toHaveScreenshot("catalog.png", SCREENSHOT_OPTIONS);
  });

  test("country dossier", async ({ page }) => {
    await page.goto("/ru/countries/russia");
    await expect(
      page.getByRole("main").getByTestId("country-card"),
    ).toBeVisible({ timeout: 15_000 });
    await expect(page).toHaveScreenshot(
      "country-dossier.png",
      SCREENSHOT_OPTIONS,
    );
  });

  test("decision result", async ({ page }) => {
    await page.goto("/ru/decision");
    await page.getByTestId("origin-select").selectOption("russia");
    await page.getByTestId("decision-run-button").click();
    await expect(page.getByTestId("decision-results")).toBeVisible({
      timeout: 20_000,
    });
    await expect(page).toHaveScreenshot(
      "decision-result.png",
      SCREENSHOT_OPTIONS,
    );
  });

  test("decision passport", async ({ page }) => {
    await page.goto("/ru/decision");
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
    // Next.js can leave a hidden Suspense streaming placeholder alongside
    // the real content for this route (same quirk documented in
    // tests/e2e/web-mvp-decision-passport.spec.ts) -- .first() picks the
    // rendered copy.
    await expect(
      page.getByTestId("decision-passport-page").first(),
    ).toBeVisible();
    await expect(page).toHaveScreenshot("decision-passport.png", {
      ...SCREENSHOT_OPTIONS,
      // The passport token in the URL/share link is unique per run, but
      // it is never rendered as visible page text, so no masking is
      // needed beyond the default full-page capture.
    });
  });
});

import { test, expect } from "@playwright/test";
import { expectHasMainHeading, expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("home visual overview", () => {
  test("homepage overview renders analytical blocks", async ({ page }) => {
    await page.goto(e2eRoutes.home);
    await expectHasMainHeading(page, /country decision atlas/i);
    await expect(page.locator('[data-testid="home-overview"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="home-country-cards"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      page.locator('[data-testid="home-scenario-winners"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="home-matrix-preview"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="home-latest-legal-events"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="home-key-insights"]'),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("Russia and Uruguay are visible", async ({ page }) => {
    await page.goto(e2eRoutes.home);
    const cards = page.locator('[data-testid="home-country-cards"]');
    await expect(cards.getByText(/russia|россия/i).first()).toBeVisible({
      timeout: 10_000,
    });
    await expect(cards.getByText(/uruguay|уругвай/i).first()).toBeVisible();
  });

  test("quick links target core workflows", async ({ page }) => {
    await page.goto(e2eRoutes.home);
    const links = page.locator('[data-testid="home-quick-links"]');
    await expect(links).toBeVisible({ timeout: 10_000 });
    await expect(links.getByRole("link", { name: /странам/i })).toHaveAttribute(
      "href",
      /\/countries/,
    );
    await expect(
      links.getByRole("link", { name: /decision/i }),
    ).toHaveAttribute("href", /\/decision/);
    await expect(links.getByRole("link", { name: /матрицу/i })).toHaveAttribute(
      "href",
      /\/compare/,
    );
    await expect(
      links.getByRole("link", { name: /правовые сигналы/i }),
    ).toHaveAttribute("href", /\/legal-signals/);
  });

  test("responsive overview does not crash", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.home);
    await expectHasMainHeading(page, /country decision atlas/i);
    await expect(
      page.locator('[data-testid="home-matrix-preview"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

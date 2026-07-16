import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { goToDecisionStep } from "./helpers/decision";
import { e2eRoutes } from "./helpers/routes";

test.describe("locale preservation", () => {
  test("public default locale is ru", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expect(page.getByTestId("locale-switch-ru")).toHaveAttribute(
      "data-active",
      "true",
    );
    const decisionLink = page.locator(
      "nav a[href*='/decision']:not([href*='passports'])",
    );
    await expect(decisionLink.first()).toHaveAttribute(
      "href",
      /^\/ru\/decision/,
    );
  });

  test("locale switcher preserves the current route", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await page.getByTestId("locale-switch-en").click();
    await expect(page).toHaveURL(/\/en\/countries\/uruguay/);
    const sourcesLink = page.locator("nav a[href*='/sources']");
    await expect(sourcesLink.first()).toHaveAttribute("href", /^\/en\/sources/);
  });

  test("locale=ru is preserved when navigating from countries list to country card", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expect(page.locator("h1").first()).toBeVisible();

    const countriesLink = page.getByRole("link", { name: "Страны" }).first();
    await countriesLink.click();
    await expectPageReady(page);
    expect(page.url()).toContain("/ru/countries");

    const countryCardLink = page
      .getByRole("link", { name: /открыть досье/i })
      .first();
    await expect(countryCardLink).toBeVisible();
    const href = await countryCardLink.getAttribute("href");
    expect(href).toMatch(/^\/ru\/countries\//);

    await countryCardLink.click();
    await expectPageReady(page);
    expect(page.url()).toContain("/ru/countries/");
    await expectNoAppCrash(page);
  });

  test("locale=en is preserved in navigation links", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectPageReady(page);
    const countriesLink = page.getByRole("link", { name: "Countries" }).first();
    await countriesLink.click();
    await expectPageReady(page);
    const countryCardLink = page
      .getByRole("link", { name: /открыть досье/i })
      .first();
    const href = await countryCardLink.getAttribute("href");
    expect(href).toMatch(/^\/en\/countries\//);
  });

  test("/countries/uruguay?locale=ru opens and shows locale status", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("locale-status")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/countries/russia?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expect(page.locator("h1").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/decision?locale=ru runs decision successfully", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.locator("h1").first()).toBeVisible();

    await goToDecisionStep(page, 4);
    const runButton = page.getByRole("button", { name: /запустить подбор/i });
    await expect(runButton).toBeVisible();
    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });
    await expectNoAppCrash(page);
  });

  test("fallback banner or locale block is visible on country card", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("locale-status")).toBeVisible();
  });
});

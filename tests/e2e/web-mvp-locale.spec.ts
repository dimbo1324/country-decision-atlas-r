import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("locale preservation", () => {
  test("locale=ru is preserved when navigating from countries list to country card", async ({
    page,
  }) => {
    await page.goto(`${e2eRoutes.countries}?locale=ru`);
    await expect(page.locator("h1")).toBeVisible();

    const countryCardLink = page
      .getByRole("link", { name: /карточка страны/i })
      .first();
    await expect(countryCardLink).toBeVisible();
    const href = await countryCardLink.getAttribute("href");
    expect(href).toContain("locale=ru");

    await countryCardLink.click();
    await expectPageReady(page);
    expect(page.url()).toContain("locale=ru");
    await expectNoAppCrash(page);
  });

  test("locale=en is preserved in navigation links", async ({ page }) => {
    await page.goto(`${e2eRoutes.countries}?locale=en`);
    const countryCardLink = page
      .getByRole("link", { name: /карточка страны/i })
      .first();
    const href = await countryCardLink.getAttribute("href");
    expect(href).toContain("locale=en");
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
    await expect(page.locator("h1")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/decision?locale=ru runs decision successfully", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.locator("h1")).toBeVisible();

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

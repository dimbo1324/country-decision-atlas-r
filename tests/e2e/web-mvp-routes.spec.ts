import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Route Explorer smoke", () => {
  test("country page shows route cards", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("country-routes-block")).toBeVisible();
    await expect(page.getByTestId("route-card").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("route detail opens from country page", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page).toHaveURL(/\/routes\/[^?]+\?locale=ru/);
    await expect(page.getByTestId("route-detail")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

test.describe("Country routes block", () => {
  test("russia routes block is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("country-routes-block")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("uruguay routes block is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("country-routes-block")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("argentina routes block is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("country-routes-block")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("route cards have title", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    const card = page.getByTestId("route-card").first();
    await expect(card).toBeVisible();
    await expect(card.locator("h3")).toBeVisible();
  });

  test("route cards have route type badge", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    const card = page.getByTestId("route-card").first();
    await expect(card.locator(".metaChip").first()).toBeVisible();
  });

  test("route cards have eligibility badges", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    const card = page.getByTestId("route-card").first();
    await expect(card.locator(".routeEligibilityBadge").first()).toBeVisible();
  });

  test("route card has detail link", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    const card = page.getByTestId("route-card").first();
    await expect(card.getByRole("link")).toBeVisible();
  });
});

test.describe("Route detail page", () => {
  test("clicking route card opens route detail", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page).toHaveURL(/\/routes\/[^?]+\?locale=ru/);
    await expect(page.getByTestId("route-detail")).toBeVisible();
  });

  test("route detail has h1", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page.locator("h1")).toBeVisible();
  });

  test("route detail has country back link", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(
      page.getByRole("link", { name: "Назад к стране" }),
    ).toBeVisible();
  });

  test("route detail has eligibility section", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page.locator(".routeEligibility").first()).toBeVisible();
  });

  test("route detail has documents section", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page.getByTestId("route-documents-section")).toBeVisible();
  });

  test("route detail has sources section", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page.getByTestId("route-sources-section")).toBeVisible();
  });

  test("route detail has evidence section", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page.getByTestId("route-evidence-section")).toBeVisible();
  });

  test("locale remains ru in route detail", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-card").first().getByRole("link").click();
    await expect(page).toHaveURL(/locale=ru/);
    await expectNoAppCrash(page);
  });
});

test.describe("Route filters", () => {
  test("route type filter select is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("route-filter-route-type")).toBeVisible();
  });

  test("allows work filter select is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("route-filter-allows-work")).toBeVisible();
  });

  test("allows family filter select is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("route-filter-allows-family")).toBeVisible();
  });

  test("leads to pr filter select is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("route-filter-leads-to-pr")).toBeVisible();
  });

  test("reset filters button is visible", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("route-filter-reset")).toBeVisible();
  });

  test("route type filter changes request or keeps valid state", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page
      .getByTestId("route-filter-route-type")
      .selectOption("temporary_residence");
    await expectNoAppCrash(page);
  });

  test("allows work filter yes works without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-filter-allows-work").selectOption("yes");
    await expectNoAppCrash(page);
  });

  test("allows family filter yes works without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-filter-allows-family").selectOption("yes");
    await expectNoAppCrash(page);
  });

  test("leads to pr filter yes works without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-filter-leads-to-pr").selectOption("yes");
    await expectNoAppCrash(page);
  });

  test("reset filters resets to default state", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page.getByTestId("route-filter-allows-work").selectOption("yes");
    await page.getByTestId("route-filter-reset").click();
    const value = await page
      .getByTestId("route-filter-allows-work")
      .inputValue();
    expect(value).toBe("");
    await expectNoAppCrash(page);
  });

  test("empty filter result does not crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await page
      .getByTestId("route-filter-route-type")
      .selectOption("investment");
    await expectNoAppCrash(page);
  });
});

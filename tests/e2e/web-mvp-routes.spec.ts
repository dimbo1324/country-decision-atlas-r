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

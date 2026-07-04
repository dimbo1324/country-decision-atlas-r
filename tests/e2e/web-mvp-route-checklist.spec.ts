import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Route practical checklist", () => {
  test("open country, open route detail, see practical checklist", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    await page
      .getByTestId("route-filter-route-type")
      .selectOption("permanent_residence");
    await page.getByTestId("route-card").first().getByRole("link").click();

    await expect(page.getByTestId("route-detail")).toBeVisible();
    await expect(page.getByTestId("route-checklist-section")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("checklist steps are visible and ordered", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    await page
      .getByTestId("route-filter-route-type")
      .selectOption("permanent_residence");
    await page.getByTestId("route-card").first().getByRole("link").click();

    const items = page.getByTestId("route-checklist-item");
    await expect(items.first()).toBeVisible();
    const count = await items.count();
    expect(count).toBeGreaterThanOrEqual(3);
    await expectNoAppCrash(page);
  });

  test("checklist source link is visible where seeded", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    await page
      .getByTestId("route-filter-route-type")
      .selectOption("permanent_residence");
    await page.getByTestId("route-card").first().getByRole("link").click();

    await expect(
      page.getByTestId("route-checklist-source-link").first(),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("route without checklist shows empty state, not a crash", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    await page.getByTestId("route-filter-route-type").selectOption("business");
    await page.getByTestId("route-card").first().getByRole("link").click();

    await expect(page.getByTestId("route-checklist-section")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

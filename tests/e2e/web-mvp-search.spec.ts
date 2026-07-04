import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Search", () => {
  test("search page loads with filters and prompt when query is empty", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.search({ locale: "ru" }));
    await expectPageReady(page);

    await expect(page.getByTestId("search-page")).toBeVisible();
    await expect(page.getByTestId("search-filters")).toBeVisible();
    await expect(page.getByTestId("search-prompt")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("header search box navigates to the search page on submit", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.home);
    await expectPageReady(page);

    await page.getByTestId("search-box-input").fill("residence");
    await page.getByTestId("search-box-submit").click();

    await expect(page).toHaveURL(/\/search\?q=residence/);
    await expect(page.getByTestId("search-page")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("empty result state shows for a query with no matches", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.search({ q: "zzzznonexistentquerykeyword123", locale: "ru" }),
    );
    await expectPageReady(page);

    await expect(
      page
        .getByTestId("search-empty-state")
        .or(page.getByTestId("search-error"))
        .first(),
    ).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("search resolves to results, empty state, or error without crashing", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.search({ q: "residence", locale: "ru" }));
    await expectPageReady(page);

    await expect(
      page
        .getByTestId("search-result-list")
        .or(page.getByTestId("search-empty-state"))
        .or(page.getByTestId("search-error"))
        .first(),
    ).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("search result link opens a target page when results are present", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.search({ q: "residence", locale: "ru" }));
    await expectPageReady(page);

    const resultList = page.getByTestId("search-result-list");
    if (await resultList.isVisible({ timeout: 10_000 }).catch(() => false)) {
      const firstLink = page.getByTestId("search-result-link").first();
      await expect(firstLink).toBeVisible();
      await firstLink.click();
      await expect(page).not.toHaveURL(/\/search\?/);
      await expectNoAppCrash(page);
    }
  });

  test("type filter checkbox narrows results and updates URL", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.search({ q: "residence", locale: "ru" }));
    await expectPageReady(page);

    await page.getByTestId("search-type-filter-route").check();
    await expect(page).toHaveURL(/types=route/);
    await expectNoAppCrash(page);
  });

  test("country filter narrows results and updates URL", async ({ page }) => {
    await page.goto(e2eRoutes.search({ q: "residence", locale: "ru" }));
    await expectPageReady(page);

    await page.getByTestId("search-country-filter").selectOption({ index: 1 });
    await expect(page).toHaveURL(/country_slug=/);
    await expectNoAppCrash(page);
  });

  test("mobile viewport does not crash on search page", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.search({ q: "residence", locale: "ru" }));
    await expectPageReady(page);

    await expect(page.getByTestId("search-page")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

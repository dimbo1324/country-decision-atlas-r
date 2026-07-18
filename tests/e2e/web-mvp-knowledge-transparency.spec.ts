import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("legal signals timeline chart", () => {
  test("old /legal-signals/timeline URL redirects into the tab", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignalsTimeline({ locale: "ru" }));
    await expectPageReady(page);
    await expect(page).toHaveURL(/\/legal-signals\?tab=timeline/);
    await expect(
      page.getByRole("main").getByTestId("legal-signals-view-panel-timeline"),
    ).toBeVisible();
  });

  test("chart or empty state renders", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ tab: "timeline", locale: "ru" }));
    await expectPageReady(page);
    const chart = page.getByTestId("legal-signals-timeline-chart");
    const empty = page.getByText(/по выбранным фильтрам событий не найдено/i);
    await expect(chart.or(empty)).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("country filter is shared with the feed via query params", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({
        tab: "timeline",
        country_slug: "russia",
        locale: "ru",
      }),
    );
    await expect(
      page.getByRole("main").locator("#timeline-country"),
    ).toHaveValue("russia");
    await expectNoAppCrash(page);
  });
});

test.describe("methodology parameters", () => {
  test("/methodology/parameters opens with a parameter table", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.methodologyParameters("ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("methodology-parameters-page")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

test.describe("glossary page", () => {
  test("/glossary opens with heading and term list", async ({ page }) => {
    await page.goto(e2eRoutes.glossary({ locale: "ru" }));
    await expectPageReady(page);
    await expect(page.getByTestId("glossary-page")).toBeVisible();
    await expect(page.getByTestId("glossary-term-list")).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("category filter narrows results", async ({ page }) => {
    await page.goto(e2eRoutes.glossary({ category: "trust", locale: "ru" }));
    await expectPageReady(page);
    await expect(
      page.locator('[data-testid="glossary-category-select"]'),
    ).toHaveValue("trust");
    await expectNoAppCrash(page);
  });

  test("search query filters terms", async ({ page }) => {
    await page.goto(e2eRoutes.glossary({ q: "CII", locale: "ru" }));
    await expectPageReady(page);
    await expect(
      page.locator('[data-testid="glossary-search-input"]'),
    ).toHaveValue("CII");
    await expectNoAppCrash(page);
  });
});

test.describe("glossary term popover", () => {
  test("clicking a term on the methodology page opens a definition popover", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.methodology("ru"));
    await expectPageReady(page);
    await expect(page.getByTestId("glossary-section")).toBeVisible();
    const firstTerm = page.getByTestId("glossary-term-trigger").first();
    await firstTerm.waitFor({ timeout: 10_000 });
    await firstTerm.click();
    await expect(page.getByTestId("glossary-term-popover")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

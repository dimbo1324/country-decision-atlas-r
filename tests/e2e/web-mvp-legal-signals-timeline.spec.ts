import { test, expect } from "@playwright/test";
import { expectHasMainHeading, expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

// Locators in this file are scoped to <main> throughout: Next.js can leave
// a hidden Suspense streaming marker (a second, invisible DOM copy of the
// boundary's content under a transient `id="S:0"` node) alongside the
// real one, which trips Playwright's strict-mode element-count check on
// bare testid/id selectors even though only one copy is ever visible.

test.describe("legal signals timeline", () => {
  test("timeline renders year groups and country events", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectHasMainHeading(page, /лента правовых сигналов/i);
    const main = page.getByRole("main");
    await expect(
      main.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      main.locator('[data-testid="timeline-year-heading"]').first(),
    ).toBeVisible();
    const eventCards = main.locator('[data-testid="legal-signal-event-card"]');
    await expect(eventCards.getByText(/россия|russia/i).first()).toBeVisible();
    await expect(
      eventCards.getByText(/уругвай|uruguay/i).first(),
    ).toBeVisible();
    await expect(
      eventCards
        .getByText(/положительное|негативное|нейтральное|смешанное/i)
        .first(),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("country and impact filters work", async ({ page }) => {
    await page.goto(
      e2eRoutes.legalSignals({
        locale: "ru",
        country_slug: "russia",
        impact_direction: "negative",
      }),
    );
    const main = page.getByRole("main");
    await expect(main.locator("#timeline-country")).toHaveValue("russia");
    await expect(
      main.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("legend and source traceability render", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    const main = page.getByRole("main");
    await expect(
      main.locator('[data-testid="legal-signals-timeline-legend"]'),
    ).toBeVisible();
    await expect(page.getByText(/источник:/i).first()).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("responsive timeline does not break", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectHasMainHeading(page, /лента правовых сигналов/i);
    await expect(
      page.getByRole("main").locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

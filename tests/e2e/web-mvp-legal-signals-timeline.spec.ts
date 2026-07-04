import { test, expect } from "@playwright/test";
import { expectHasMainHeading, expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("legal signals timeline", () => {
  test("timeline renders year groups and country events", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectHasMainHeading(page, /лента правовых сигналов/i);
    await expect(
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.locator(".timelineYearTitle").first()).toBeVisible();
    const eventCards = page.locator(".timelineEventCard");
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
    await expect(page.locator("#timeline-country")).toHaveValue("russia");
    await expect(
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("legend and source traceability render", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expect(
      page.locator('[data-testid="legal-signals-timeline-legend"]'),
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
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Argentina legal signals and timeline", () => {
  test("/countries/argentina opens without crash after legal signals added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("/countries/argentina CII block still visible after legal signals", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/legal-signals?country_slug=argentina opens without crash", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("/legal-signals?country_slug=argentina renders timeline", async ({ page }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("/legal-signals?country_slug=argentina shows Argentina events", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    const eventCards = page.locator(".timelineEventCard");
    await expect(eventCards.first()).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("/legal-signals?country_slug=argentina shows impact badges", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    const impactBadge = page
      .locator(".timelineEventCard")
      .filter({ hasText: /положительное|негативное|нейтральное|смешанное/i });
    await expect(impactBadge.first()).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("/legal-signals?country_slug=argentina shows source traceability", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByText(/источник:/i).first()).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("/sources?country_slug=argentina opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ country_slug: "argentina", locale: "ru" }));
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("Argentina filter in /legal-signals does not crash", async ({ page }) => {
    await page.goto(
      e2eRoutes.legalSignals({ locale: "ru", country_slug: "argentina" }),
    );
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("Russia still accessible with legal signals after Argentina added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ country_slug: "russia", locale: "ru" }));
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("Uruguay still accessible with legal signals after Argentina added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ country_slug: "uruguay", locale: "ru" }));
    await expect(page.locator('[data-testid="legal-signals-timeline"]')).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("responsive: /legal-signals?country_slug=argentina at 390x844 does not crash", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });
});

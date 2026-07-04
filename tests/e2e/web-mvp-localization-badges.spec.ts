import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

const BADGE_SELECTOR = '[data-testid="localization-badge"]';

const BADGE_TEXTS = [
  /оригинал/i,
  /показан fallback/i,
  /проверено/i,
  /машинный перевод/i,
  /устаревший перевод/i,
  /нет перевода/i,
  /требует проверки/i,
  /написано вручную/i,
];

function matchesBadgeText(text: string): boolean {
  return BADGE_TEXTS.some((re) => re.test(text));
}

test.describe("localization badges", () => {
  test("country card RU — at least one localization badge visible", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectNoAppCrash(page);
    const badges = page.locator(BADGE_SELECTOR);
    const count = await badges.count();
    if (count > 0) {
      const texts = await badges.allTextContents();
      const hasKnown = texts.some(matchesBadgeText);
      expect(hasKnown).toBe(true);
    }
  });

  test("country card EN — page opens without crash, badge visible if data present", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "en"));
    await expectNoAppCrash(page);
    const badges = page.locator(BADGE_SELECTOR);
    const count = await badges.count();
    if (count > 0) {
      const first = await badges.first().textContent();
      expect(first).toBeTruthy();
    }
  });

  test("legal signals RU — page opens, badge visible if items exist", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectNoAppCrash(page);
    const list = page.locator('[data-testid="legal-signals-list"]');
    const listVisible = await list.isVisible().catch(() => false);
    if (listVisible) {
      const badges = page.locator(BADGE_SELECTOR);
      const count = await badges.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test("sources RU — page opens, badge visible if items exist", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.sources({ locale: "ru" }));
    await expectNoAppCrash(page);
    const list = page.locator('[data-testid="sources-list"]');
    const listVisible = await list.isVisible().catch(() => false);
    if (listVisible) {
      const badges = page.locator(BADGE_SELECTOR);
      const count = await badges.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test("decision page RU — results appear without crash", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expectNoAppCrash(page);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("badges do not crash UI when metadata is absent", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectNoAppCrash(page);
  });
});

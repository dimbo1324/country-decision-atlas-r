import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("argentina core country slice", () => {
  test("/countries includes Argentina in the list", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectNoAppCrash(page);
    await expect(page.getByText(/argentina|аргентина/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("/countries/argentina opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina"));
    await expectNoAppCrash(page);
  });

  test("/countries/argentina?locale=ru has main heading", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectHasMainHeading(page, /argentina|аргентина/i);
    await expectNoAppCrash(page);
  });

  test("/countries/argentina?locale=en has main heading", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "en"));
    await expectHasMainHeading(page, /argentina/i);
    await expectNoAppCrash(page);
  });

  test("Argentina page renders without CII data", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    const hasEmptyState = await page
      .getByText(/ещё не рассчитаны|не рассчитан|данные.*отсутствуют/i)
      .isVisible()
      .catch(() => false);
    const hasCiiBlock = await page
      .locator('[data-testid*="cii"]')
      .first()
      .isVisible()
      .catch(() => false);
    expect(hasEmptyState || hasCiiBlock).toBe(true);
  });

  test("Argentina page renders without legal signals", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    const hasEmptySignals = await page
      .getByText(/правовые сигналы.*пока отсутствуют|сигналов нет/i)
      .isVisible()
      .catch(() => false);
    const hasSignalsBlock = await page
      .locator('[data-testid*="legal"]')
      .first()
      .isVisible()
      .catch(() => false);
    expect(hasEmptySignals || hasSignalsBlock).toBe(true);
  });

  test("Russia and Uruguay remain accessible after Argentina added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectHasMainHeading(page, /россия|russia/i);
    await expectNoAppCrash(page);

    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectHasMainHeading(page, /уругвай|uruguay/i);
    await expectNoAppCrash(page);
  });
});

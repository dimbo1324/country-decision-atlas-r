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

  test("Argentina page renders the CII section", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    const ciiSection = page.locator('[data-testid="cii-section"]');
    await expect(ciiSection).toBeVisible();
    const emptyState = ciiSection.getByText(
      /ещё не рассчитаны|не рассчитан|данные.*отсутствуют/i,
    );
    const ciiBlock = ciiSection.locator('[data-testid="cii-block"]');
    await expect(emptyState.or(ciiBlock).first()).toBeVisible();
  });

  test("Argentina page renders current legal signals", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator('[data-testid="country-legal-signals"]')).toBeVisible();
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

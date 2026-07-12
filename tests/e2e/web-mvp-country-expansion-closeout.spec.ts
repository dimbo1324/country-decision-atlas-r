import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("Country expansion closeout — three countries", () => {
  test("/countries shows Russia, Uruguay and Argentina", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectNoAppCrash(page);
    await expect(page.getByText(/россия|russia/i).first()).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByText(/уругвай|uruguay/i).first()).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByText(/аргентина|argentina/i).first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/countries/russia opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectHasMainHeading(page, /россия|russia/i);
    await expectNoAppCrash(page);
  });

  test("/countries/uruguay opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectHasMainHeading(page, /уругвай|uruguay/i);
    await expectNoAppCrash(page);
  });

  test("/countries/argentina opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectHasMainHeading(page, /аргентина|argentina/i);
    await expectNoAppCrash(page);
  });

  test("/countries/argentina shows CII block", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/countries/russia shows CII block", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/countries/uruguay shows CII block", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectNoAppCrash(page);
    await expect(page.locator("[data-testid='cii-block']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("/compare shows all three country rows", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.locator('[data-testid="matrix-row-russia"]')).toBeVisible(
      {
        timeout: 10_000,
      },
    );
    await expect(
      page.locator('[data-testid="matrix-row-uruguay"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expect(
      page.locator('[data-testid="matrix-row-argentina"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });

  test("/compare Argentina row has numeric scores", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    const row = page.locator('[data-testid="matrix-row-argentina"]');
    const text = await row.textContent();
    expect(text).toMatch(/\d+/);
    await expectNoAppCrash(page);
  });

  test("/compare Argentina+Uruguay does not crash", async ({ page }) => {
    await page.goto(
      e2eRoutes.compare +
        "?countries=argentina%2Curuguay&scenario=relocation_residence",
    );
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("/compare Argentina+Russia does not crash", async ({ page }) => {
    await page.goto(
      e2eRoutes.compare +
        "?countries=argentina%2Crussia&scenario=business_self_employment",
    );
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("/legal-signals?country_slug=argentina shows timeline", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "argentina", locale: "ru" }),
    );
    await expect(
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("/legal-signals?country_slug=russia shows timeline", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "russia", locale: "ru" }),
    );
    await expect(
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("/legal-signals?country_slug=uruguay shows timeline", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({ country_slug: "uruguay", locale: "ru" }),
    );
    await expect(
      page.locator('[data-testid="legal-signals-timeline"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("/sources?country_slug=argentina opens without crash", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.sources({ country_slug: "argentina", locale: "ru" }),
    );
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("/ home page opens without crash", async ({ page }) => {
    await page.goto("/");
    await expectNoAppCrash(page);
    await expect(page.locator("h1")).toBeVisible({ timeout: 15_000 });
  });

  test("responsive: /compare at 390x844 shows all three rows", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.compare);
    await expect(
      page.locator('[data-testid="compare-matrix-table"]'),
    ).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.locator('[data-testid="matrix-row-argentina"]'),
    ).toBeVisible({
      timeout: 10_000,
    });
    await expectNoAppCrash(page);
  });
});

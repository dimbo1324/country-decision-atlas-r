import { test, expect } from "@playwright/test";
import {
  expectNoAppCrash,
  expectPageReady,
  expectHasMainHeading,
} from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("MVP page availability", () => {
  test("home / opens with main heading", async ({ page }) => {
    await page.goto(e2eRoutes.home);
    await expectHasMainHeading(
      page,
      /compare countries with source-backed intelligence/i,
    );
    await expect(
      page.getByRole("link", { name: /explore countries/i }),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/countries shows Russia and Uruguay", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectHasMainHeading(page, /decision-ready country cards/i);
    await expect(page.getByText("Russia").first()).toBeVisible();
    await expect(page.getByText("Uruguay").first()).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/countries/russia?locale=en opens", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "en"));
    await expectHasMainHeading(page, /russia/i);
    await expectNoAppCrash(page);
  });

  test("/countries/russia?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);
    await expectNoAppCrash(page);
  });

  test("/countries/uruguay?locale=en opens", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectHasMainHeading(page, /uruguay/i);
    await expectNoAppCrash(page);
  });

  test("/countries/uruguay?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectPageReady(page);
    await expectNoAppCrash(page);
  });

  test("/decision?locale=en shows decision form", async ({ page }) => {
    await page.goto(e2eRoutes.decision("en"));
    await expectHasMainHeading(page, /run a country decision/i);
    await expect(
      page.getByRole("button", { name: /run decision/i }),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/decision?locale=ru shows decision form", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expectHasMainHeading(page, /run a country decision/i);
    await expect(
      page.getByRole("button", { name: /run decision/i }),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/legal-signals?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectHasMainHeading(page, /traceable decision signals/i);
    await expectNoAppCrash(page);
  });

  test("/sources?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ locale: "ru" }));
    await expectHasMainHeading(page, /evidence sources/i);
    await expectNoAppCrash(page);
  });

  test("/internal/data-quality opens", async ({ page }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /data quality report/i);
    await expectNoAppCrash(page);
  });

  test("responsive: /countries at 390x844 does not crash", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.countries);
    await expectHasMainHeading(page, /decision-ready country cards/i);
    await expect(page.getByRole("link", { name: "Country Decision Atlas" })).toBeVisible();
    await expectNoAppCrash(page);
  });
});

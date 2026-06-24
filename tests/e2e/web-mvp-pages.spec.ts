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
    await expectHasMainHeading(page, /country decision atlas/i);
    await expect(page.getByRole("link", { name: /запустить подбор/i })).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/countries shows Russia and Uruguay", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectHasMainHeading(page, /карточки стран для подбора/i);
    await expect(page.getByText(/россия|russia/i).first()).toBeVisible();
    await expect(page.getByText(/уругвай|uruguay/i).first()).toBeVisible();
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
    await expectHasMainHeading(page, /запустить подбор страны/i);
    await expect(page.getByRole("button", { name: /запустить подбор/i })).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/decision?locale=ru shows decision form", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expectHasMainHeading(page, /запустить подбор страны/i);
    await expect(page.getByRole("button", { name: /запустить подбор/i })).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("/legal-signals?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "ru" }));
    await expectHasMainHeading(page, /лента правовых сигналов/i);
    await expectNoAppCrash(page);
  });

  test("/sources?locale=ru opens", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ locale: "ru" }));
    await expectHasMainHeading(page, /источники доказательств/i);
    await expectNoAppCrash(page);
  });

  test("/internal/data-quality opens", async ({ page }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /отчёт качества данных/i);
    await expectNoAppCrash(page);
  });

  test("responsive: /countries at 390x844 does not crash", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.countries);
    await expectHasMainHeading(page, /карточки стран для подбора/i);
    await expect(
      page.getByRole("link", { name: "Country Decision Atlas" }),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });
});

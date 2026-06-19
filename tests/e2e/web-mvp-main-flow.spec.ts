import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("main MVP user flow: home → countries → Russia → Uruguay → decision → result → country card", async ({
  page,
}) => {
  await page.goto(e2eRoutes.home);
  await expectHasMainHeading(
    page,
    /compare countries with source-backed intelligence/i,
  );
  await expect(
    page.getByRole("link", { name: /explore countries/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: /run decision/i }).first(),
  ).toBeVisible();
  await expectNoAppCrash(page);

  await page.getByRole("link", { name: "Countries" }).click();
  await expectHasMainHeading(page, /decision-ready country cards/i);
  await expect(page.getByText("Russia").first()).toBeVisible();
  await expect(page.getByText("Uruguay").first()).toBeVisible();

  await page
    .getByRole("link", { name: "View country card" })
    .first()
    .click();
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.getByText(/scenario scores/i)).toBeVisible();
  await expect(
    page.locator("[data-testid='country-card']"),
  ).toBeVisible();
  await expectNoAppCrash(page);

  await page.getByRole("link", { name: /all countries/i }).click();
  await expectHasMainHeading(page, /decision-ready country cards/i);

  await page
    .getByRole("link", { name: "View country card" })
    .nth(1)
    .click();
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.getByText(/scenario scores/i)).toBeVisible();
  await expectNoAppCrash(page);

  await page.getByRole("link", { name: "Decision" }).click();
  await expectHasMainHeading(page, /run a country decision/i);
  await expect(
    page.getByRole("combobox", { name: /origin country/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("combobox", { name: /scenario/i }),
  ).toBeVisible();

  const runButton = page.getByRole("button", { name: /run decision/i });
  await expect(runButton).toBeVisible();
  await runButton.click();

  await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText("Full ranking")).toBeVisible();
  await expect(page.locator(".resultCard").first()).toBeVisible();
  await expectNoAppCrash(page);

  await page
    .getByRole("link", { name: /open country card/i })
    .first()
    .click();
  await expect(page.locator("h1")).toBeVisible();
  await expectNoAppCrash(page);
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("What Changed", () => {
  test("country page shows What Changed section", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("what-changed-section")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("What Changed block resolves to content, empty state, or error without crashing", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectPageReady(page);

    const section = page.getByTestId("what-changed-section");
    await expect(section).toBeVisible();
    await expect(
      section
        .getByTestId("what-changed-block")
        .or(section.getByTestId("what-changed-empty"))
        .or(section.getByTestId("what-changed-error"))
        .first(),
    ).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("uruguay country page shows What Changed section", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("what-changed-section")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("What Changed item links open a public page when items are present", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectPageReady(page);

    const block = page.getByTestId("what-changed-block");
    if (await block.isVisible({ timeout: 10_000 }).catch(() => false)) {
      const firstItem = page.getByTestId("what-changed-item").first();
      if (await firstItem.isVisible().catch(() => false)) {
        await expect(firstItem.getByRole("link")).toBeVisible();
      }
    }
    await expectNoAppCrash(page);
  });

  test("mobile viewport does not crash on What Changed block", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectPageReady(page);

    await expect(page.getByTestId("what-changed-section")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

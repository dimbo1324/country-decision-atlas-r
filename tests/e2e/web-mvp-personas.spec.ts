import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

async function runDecision(page: import("@playwright/test").Page) {
  const runButton = page.getByTestId("decision-run-button");
  await expect(runButton).toBeVisible();
  await expect(runButton).not.toBeDisabled();
  await runButton.click();
  await expect(page.getByTestId("decision-results")).toBeVisible({
    timeout: 20_000,
  });
}

test.describe("Persona decision flow", () => {
  test("/decision shows persona selector", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    const selector = page.getByTestId("persona-selector");
    await expect(selector).toBeVisible();
    await expect(selector).toHaveValue("");
    await expect(selector.locator("option")).toContainText(["Без персонализации"]);
    await expectNoAppCrash(page);
  });

  test("selector contains family persona", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("persona-selector")).toContainText("Семья");
    await expectNoAppCrash(page);
  });

  test("decision without persona still works", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await runDecision(page);

    await expect(page.getByTestId("decision-persona-meta")).toHaveCount(0);
    await expectNoAppCrash(page);
  });

  test("decision with family shows applied persona and adjusted score", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("persona-selector").selectOption("family");
    await runDecision(page);

    await expect(page.getByTestId("decision-persona-meta")).toContainText("Семья");
    await expect(page.getByTestId("decision-persona-meta")).toContainText(
      "persona_adjusted",
    );
    await expect(page.getByTestId("persona-adjusted-score").first()).toBeVisible();
    await expect(page.getByTestId("cii-persona-note")).toContainText("Семья", {
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });

  test("decision with entrepreneur works", async ({ page }) => {
    await page.goto(e2eRoutes.decision("ru"));

    await page.getByTestId("persona-selector").selectOption("entrepreneur");
    await runDecision(page);

    await expect(page.getByTestId("decision-persona-meta")).toContainText(
      "Предприниматель",
    );
    await expect(page.locator(".ciiCompareBlock")).toBeVisible({ timeout: 15_000 });
    await expectNoAppCrash(page);
  });

  test("mobile viewport does not crash with persona selector", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(e2eRoutes.decision("ru"));

    await expect(page.getByTestId("persona-selector")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("compare and routes pages remain available", async ({ page }) => {
    await page.goto(e2eRoutes.compare);
    await expect(page.locator('[data-testid="compare-matrix-table"]')).toBeVisible({
      timeout: 15_000,
    });

    await page.goto(e2eRoutes.country("russia", "ru"));
    await expect(page.getByTestId("route-card").first()).toBeVisible({
      timeout: 15_000,
    });
    await expectNoAppCrash(page);
  });
});

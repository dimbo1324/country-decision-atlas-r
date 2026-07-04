import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("decision-ready scenario filtering", () => {
  test("/decision?locale=en shows only decision-ready scenarios", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("en"));
    await expect(page.locator("h1")).toBeVisible();

    const select = page.getByTestId("decision-scenario-select");
    await expect(select).toBeVisible();

    const optionTexts = await select.locator("option").allTextContents();
    const lower = optionTexts.map((t) => t.toLowerCase());

    expect(lower.some((t) => t.includes("family relocation"))).toBe(false);
    expect(lower.some((t) => t.includes("digital nomad"))).toBe(false);

    expect(
      lower.some(
        (t) =>
          t.includes("relocation") ||
          t.includes("residence") ||
          t.includes("living") ||
          t.includes("business") ||
          t.includes("safety"),
      ),
    ).toBe(true);

    await expectNoAppCrash(page);
  });

  test("/decision?locale=ru shows only decision-ready scenarios", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("ru"));
    await expect(page.locator("h1")).toBeVisible();

    const select = page.getByTestId("decision-scenario-select");
    await expect(select).toBeVisible();

    const optionTexts = await select.locator("option").allTextContents();
    const lower = optionTexts.map((t) => t.toLowerCase());

    expect(lower.some((t) => t.includes("family relocation"))).toBe(false);
    expect(optionTexts.length).toBeGreaterThan(0);

    await expectNoAppCrash(page);
  });

  test("default scenario runs successfully without decision_score_not_found", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("en"));
    await expect(page.locator("h1")).toBeVisible();

    const runButton = page.getByTestId("decision-run-button");
    await expect(runButton).toBeVisible();
    await expect(runButton).not.toBeDisabled();

    await runButton.click();

    await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
      timeout: 20_000,
    });

    await expect(
      page.getByText("decision_score_not_found", { exact: false }),
    ).not.toBeVisible();
    await expect(
      page.getByText("not available for the selected countries yet", {
        exact: false,
      }),
    ).not.toBeVisible();

    await expectNoAppCrash(page);
  });

  test("Run decision button is not disabled when decision-ready scenarios are present", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.decision("en"));
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByTestId("decision-run-button")).not.toBeDisabled();
    await expectNoAppCrash(page);
  });
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("community intelligence surface", () => {
  test("country page exposes moderated community actions", async ({ page }) => {
    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectPageReady(page);

    await expect(page.getByTestId("community-country-block")).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByTestId("community-review-badge")).toContainText(
      /review gate/i,
    );

    const pendingTitle = `Runtime pending question ${Date.now()}`;
    await page.getByTestId("community-question-title").fill(pendingTitle);
    await page
      .getByTestId("community-question-body")
      .fill("Community UI smoke question should stay pending.");
    await page.getByTestId("community-question-submit").click();
    await expect(page.getByTestId("community-status")).toContainText(
      /pending/i,
      {
        timeout: 15_000,
      },
    );
    await expect(page.getByTestId("community-qna-panel")).not.toContainText(
      pendingTitle,
    );

    await page
      .getByTestId("community-report-message")
      .fill("Community UI smoke data issue report.");
    await page.getByTestId("community-report-submit").click();
    await expect(page.getByTestId("community-status")).toContainText(
      /review/i,
      {
        timeout: 15_000,
      },
    );

    await page
      .getByTestId("community-rating-comment")
      .fill("Community UI smoke reality-gap input.");
    await page.getByTestId("community-rating-submit").click();
    await expect(page.getByTestId("community-status")).toContainText(
      /pending/i,
      {
        timeout: 15_000,
      },
    );

    await expectNoAppCrash(page);
  });
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("user stories page", () => {
  test("/user-stories renders the feed and submission form", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.userStories);
    await expectPageReady(page);

    await expect(page.getByTestId("user-stories-view")).toBeVisible();
    await expect(
      page.getByTestId("user-story-destination-select"),
    ).toBeVisible();
    await expect(page.getByTestId("user-story-scenario-input")).toBeVisible();
    await expect(page.getByTestId("user-story-submit")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("seeded published stories render with country name and synthetic badge", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.userStories);
    await expectPageReady(page);

    await expect(page.getByTestId("user-stories-list")).toBeVisible({
      timeout: 15_000,
    });
    const firstStory = page.getByTestId("user-story-card").first();
    await expect(firstStory).toBeVisible();
    await expect(
      firstStory.getByTestId("user-story-synthetic-badge"),
    ).toBeVisible();
  });

  test("submitting a new story clears the form and does not appear until moderation", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.userStories);
    await expectPageReady(page);

    await page
      .getByTestId("user-story-destination-select")
      .selectOption("uruguay");
    const scenarioSelect = page.getByTestId("user-story-scenario-input");
    await expect
      .poll(async () => scenarioSelect.locator("option").count(), {
        timeout: 15_000,
      })
      .toBeGreaterThan(1);
    await scenarioSelect.selectOption({ index: 1 });
    const uniqueAdvice = `E2E advice ${Date.now()}`;
    await page.getByTestId("user-story-advice-input").fill(uniqueAdvice);

    const [response] = await Promise.all([
      page.waitForResponse(
        (res) =>
          res.url().includes("/api/v1/user-stories") &&
          res.request().method() === "POST",
      ),
      page.getByTestId("user-story-submit").click(),
    ]);
    expect(response.ok()).toBe(true);

    await expect(page.getByTestId("user-story-advice-input")).toHaveValue("", {
      timeout: 15_000,
    });
    await expect(page.getByTestId("user-stories-list")).not.toContainText(
      uniqueAdvice,
    );
    await expectNoAppCrash(page);
  });
});

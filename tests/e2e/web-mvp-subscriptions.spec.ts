import { test, expect } from "./helpers/fixtures";
import { expectPageReady } from "./helpers/assertions";
import { API_BASE_URL } from "./helpers/env";
import { e2eRoutes } from "./helpers/routes";

test.describe("subscriptions page anonymous state", () => {
  test("/subscriptions without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.subscriptions);
    await expectPageReady(page);
    await expect(
      page.getByTestId("subscriptions-unauthenticated"),
    ).toBeVisible();
  });
});

test.describe("subscriptions authenticated flow", () => {
  test("empty subscriptions and feed show empty states after login", async ({
    page,
    seededUser,
  }) => {
    await page.goto(e2eRoutes.subscriptions);
    await expect(page.getByTestId("subscriptions-view")).toBeVisible();
    await expect(page.getByTestId("subscriptions-empty-state")).toBeVisible();
    await expect(page.getByTestId("feed-empty-state")).toBeVisible();
  });

  test("subscribing without metric or author id shows a validation error", async ({
    page,
    seededUser,
  }) => {
    await page.goto(e2eRoutes.subscriptions);
    await page.getByTestId("subscribe-submit").click();
    await expect(
      page.getByText("Укажите ID метрики или ID автора."),
    ).toBeVisible();
  });

  test("subscribing by author id adds it to the list and unsubscribing clears it", async ({
    page,
    seededUser,
  }) => {
    // fetch() needs a real page origin to run from -- the seededUser
    // fixture only sets cookies, it never navigates `page` (still
    // about:blank at this point without a goto first).
    await page.goto(e2eRoutes.subscriptions);
    const me = await page.evaluate(async (apiBaseUrl) => {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
        credentials: "include",
      });
      return (await response.json()) as { user: { id: string } };
    }, API_BASE_URL);

    await page.getByTestId("subscribe-author-id-input").fill(me.user.id);
    await page.getByTestId("subscribe-submit").click();

    await expect(page.getByTestId("subscriptions-list")).toBeVisible();
    const item = page.getByTestId("subscription-item").first();
    await expect(item).toBeVisible();

    await item.getByTestId("subscription-remove-button").click();
    await expect(page.getByTestId("subscriptions-empty-state")).toBeVisible();
  });
});

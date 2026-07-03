import type { Page } from "@playwright/test";
import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

async function registerViaUi(
  page: Page,
  email: string,
  password = "a-very-strong-password-123",
) {
  await page.goto(e2eRoutes.register);
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-display-name").fill("Runtime Watchlist User");
  await page.getByTestId("register-password").fill(password);
  await page.getByTestId("register-submit").click();
  await expect(page).toHaveURL(new RegExp(e2eRoutes.account));
}

test.describe("watchlist page anonymous state", () => {
  test("/watchlist without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.watchlist);
    await expectPageReady(page);
    await expect(page.getByTestId("watchlist-unauthenticated")).toBeVisible();
  });

  test("country page watchlist button prompts login when signed out", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectPageReady(page);
    await expect(page.getByTestId("watchlist-button-login-required")).toBeVisible();
  });
});

test.describe("watchlist authenticated flow", () => {
  test("empty watchlist shows the empty state after login", async ({ page }) => {
    const email = uniqueEmail("watchlist-empty-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.watchlist);
    await expect(page.getByTestId("watchlist-empty-state")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("saving a country from its page adds it to the watchlist and removing clears it", async ({
    page,
  }) => {
    const email = uniqueEmail("watchlist-save-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectPageReady(page);

    const toggleButton = page.getByTestId("watchlist-toggle-button");
    await expect(toggleButton).toBeVisible({ timeout: 10_000 });
    await expect(toggleButton).toHaveText(/Сохранить в watchlist/);
    await toggleButton.click();
    await expect(toggleButton).toHaveText(/В watchlist/);

    await page.goto(e2eRoutes.watchlist);
    await expect(page.getByTestId("watchlist-list")).toBeVisible();
    const item = page.getByTestId("watchlist-item").first();
    await expect(item).toBeVisible();
    await expect(item).toContainText("Uruguay");

    await item.getByTestId("watchlist-remove-button").click();
    await expect(page.getByTestId("watchlist-empty-state")).toBeVisible();

    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expect(page.getByTestId("watchlist-toggle-button")).toHaveText(
      /Сохранить в watchlist/,
      { timeout: 10_000 },
    );
  });

  test("toggling a notification preference persists after reload", async ({ page }) => {
    const email = uniqueEmail("watchlist-toggle-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.country("uruguay", "en"));
    await expectPageReady(page);
    const toggleButton = page.getByTestId("watchlist-toggle-button");
    await expect(toggleButton).toBeVisible({ timeout: 10_000 });
    await toggleButton.click();
    await expect(toggleButton).toHaveText(/В watchlist/);

    await page.goto(e2eRoutes.watchlist);
    const item = page.getByTestId("watchlist-item").first();
    await expect(item).toBeVisible();
    const routeUpdatesCheckbox = item.getByRole("checkbox", {
      name: /Обновления маршрутов/,
    });
    await expect(routeUpdatesCheckbox).not.toBeChecked();
    await routeUpdatesCheckbox.click();
    await expect(routeUpdatesCheckbox).toBeChecked();

    await page.reload();
    const reloadedItem = page.getByTestId("watchlist-item").first();
    await expect(
      reloadedItem.getByRole("checkbox", { name: /Обновления маршрутов/ }),
    ).toBeChecked();
  });
});

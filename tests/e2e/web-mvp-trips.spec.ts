import type { Page } from "@playwright/test";
import { test, expect } from "@playwright/test";
import { expectPageReady } from "./helpers/assertions";
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
  await page.getByTestId("register-display-name").fill("Trips User");
  await page.getByTestId("register-password").fill(password);
  await page.getByTestId("register-submit").click();
  await expect(page).toHaveURL(new RegExp(e2eRoutes.account));
}

async function createTrip(page: Page, title: string) {
  await page.goto(e2eRoutes.trips);
  await page.getByTestId("trip-title-input").fill(title);
  await page.getByTestId("trip-create-submit").click();
  await expect(page.getByTestId("trips-list")).toBeVisible();
  await page.getByTestId("trip-item").filter({ hasText: title }).click();
  await expect(page.getByTestId("trip-detail")).toBeVisible();
}

test.describe("trips page anonymous state", () => {
  test("/trips without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.trips);
    await expectPageReady(page);
    await expect(page.getByTestId("trips-unauthenticated")).toBeVisible();
  });
});

test.describe("trips authenticated flow", () => {
  test("empty trips list shows the empty state after login", async ({
    page,
  }) => {
    const email = uniqueEmail("trips-empty-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.trips);
    await expect(page.getByTestId("trips-view")).toBeVisible();
    await expect(page.getByTestId("trips-empty-state")).toBeVisible();
  });

  test("creating a trip navigates to its detail view", async ({ page }) => {
    const email = uniqueEmail("trips-create-user");
    await registerViaUi(page, email);
    await createTrip(page, "Move to Uruguay");
    await expect(page.getByTestId("trip-title")).toHaveText("Move to Uruguay");
  });

  test("adding, reordering (keyboard), and removing waypoints", async ({
    page,
  }) => {
    const email = uniqueEmail("trips-waypoints-user");
    await registerViaUi(page, email);
    await createTrip(page, "Waypoints trip");

    await page.getByTestId("waypoint-country-select").selectOption("uruguay");
    await page.getByTestId("waypoint-add-submit").click();
    await expect(page.getByTestId("waypoint-row")).toHaveCount(1);

    await page.getByTestId("waypoint-country-select").selectOption("argentina");
    await page.getByTestId("waypoint-add-submit").click();
    await expect(page.getByTestId("waypoint-row")).toHaveCount(2);

    const rowsBefore = page.getByTestId("waypoint-row");
    await expect(rowsBefore.nth(0)).toContainText("Uruguay");
    await expect(rowsBefore.nth(1)).toContainText("Argentina");

    const firstHandle = page.getByTestId("waypoint-drag-handle").first();
    await firstHandle.focus();
    await firstHandle.press("Space");
    await page.waitForTimeout(200);
    await firstHandle.press("ArrowDown");
    await page.waitForTimeout(200);
    await firstHandle.press("Space");
    await page.waitForTimeout(200);

    const rowsAfter = page.getByTestId("waypoint-row");
    await expect(rowsAfter.nth(0)).toContainText("Argentina");
    await expect(rowsAfter.nth(1)).toContainText("Uruguay");

    await page.reload();
    const rowsReloaded = page.getByTestId("waypoint-row");
    await expect(rowsReloaded.nth(0)).toContainText("Argentina");
    await expect(rowsReloaded.nth(1)).toContainText("Uruguay");

    await page.getByTestId("waypoint-remove-button").first().click();
    await expect(page.getByTestId("waypoint-row")).toHaveCount(1);
  });

  test("checklist: add, toggle, and remove an item", async ({ page }) => {
    const email = uniqueEmail("trips-checklist-user");
    await registerViaUi(page, email);
    await createTrip(page, "Checklist trip");

    await page.getByTestId("checklist-item-input").fill("Gather documents");
    await page.getByTestId("checklist-item-add-submit").click();
    await expect(page.getByTestId("checklist-item")).toHaveCount(1);

    const checkbox = page.getByTestId("checklist-item-checkbox");
    await expect(checkbox).not.toBeChecked();
    await checkbox.click();
    await expect(checkbox).toBeChecked();

    await page.reload();
    await expect(page.getByTestId("checklist-item-checkbox")).toBeChecked();

    await page.getByTestId("checklist-item-remove-button").click();
    await expect(page.getByTestId("checklist-item")).toHaveCount(0);
  });

  test("reminders: create and cancel", async ({ page }) => {
    const email = uniqueEmail("trips-reminders-user");
    await registerViaUi(page, email);
    await createTrip(page, "Reminders trip");

    const future = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    const value = future.toISOString().slice(0, 16);
    await page.getByTestId("reminder-datetime-input").fill(value);
    await page.getByTestId("reminder-create-submit").click();

    await expect(page.getByTestId("reminder-item")).toHaveCount(1);
    await page.getByTestId("reminder-cancel-button").click();
    await expect(page.getByTestId("reminder-cancel-button")).toHaveCount(0);
  });

  test("share: enable creates a working public page, disable revokes it", async ({
    page,
    context,
  }) => {
    const email = uniqueEmail("trips-share-user");
    await registerViaUi(page, email);
    await createTrip(page, "Shared trip");

    await page.getByTestId("waypoint-country-select").selectOption("uruguay");
    await page.getByTestId("waypoint-add-submit").click();
    await expect(page.getByTestId("waypoint-row")).toHaveCount(1);

    const [shareResponse] = await Promise.all([
      page.waitForResponse(
        (res) =>
          res.url().includes("/share") && res.request().method() === "POST",
      ),
      page.getByTestId("trip-share-enable").click(),
    ]);
    const shareBody = (await shareResponse.json()) as { token: string };
    await expect(page.getByTestId("trip-share-disable")).toBeVisible();

    const publicPage = await context.newPage();
    await publicPage.goto(e2eRoutes.tripSharedPublic(shareBody.token));
    await expect(publicPage.getByTestId("shared-trip-page")).toBeVisible();
    await expect(publicPage.getByTestId("shared-trip-title")).toHaveText(
      "Shared trip",
    );
    await publicPage.close();

    await page.getByTestId("trip-share-disable").click();
    await expect(page.getByTestId("trip-share-enable")).toBeVisible();
  });

  test("deleting a trip removes it from the list", async ({ page }) => {
    const email = uniqueEmail("trips-delete-user");
    await registerViaUi(page, email);
    await createTrip(page, "Trip to delete");

    await page.getByTestId("trip-delete-button").click();
    await expect(page).toHaveURL(new RegExp(e2eRoutes.trips));
    await expect(page.getByTestId("trips-empty-state")).toBeVisible();
  });
});

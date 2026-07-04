import { test, expect, type Page } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

async function registerViaUi(page: Page, email: string) {
  await page.goto(e2eRoutes.register);
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-display-name").fill("Migration Board User");
  await page
    .getByTestId("register-password")
    .fill("a-very-strong-password-123");
  await page.getByTestId("register-submit").click();
}

test.describe("migration board public surface", () => {
  test("/migration-board opens and renders filters", async ({ page }) => {
    await page.goto(e2eRoutes.migrationBoard);
    await expectPageReady(page);
    await expect(
      page.getByRole("heading", { name: /доска переезда/i }),
    ).toBeVisible();
    await expect(page.getByTestId("migration-board-page")).toBeVisible({
      timeout: 15_000,
    });
    await expect(
      page.getByTestId("migration-board-destination-filter"),
    ).toBeVisible();
    await expect(
      page.getByTestId("migration-board-timeline-filter"),
    ).toBeVisible();
    await expect(page.getByTestId("migration-board-goal-filter")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("logged-in user can create and submit a migration board post", async ({
    page,
  }) => {
    const email = uniqueEmail("migration-board-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    await page.goto(e2eRoutes.migrationBoardNew);
    await expect(page.getByTestId("migration-board-new-form")).toBeVisible();
    await page.getByTestId("migration-board-destination-input").fill("uruguay");
    await page
      .getByTestId("migration-board-title-input")
      .fill("Moving to Uruguay");
    await page
      .getByTestId("migration-board-summary-input")
      .fill(
        "Preparing documents and housing research for a possible relocation next year.",
      );
    await page.getByTestId("migration-board-risk-checkbox").check();
    await page.getByTestId("migration-board-legal-checkbox").check();
    await page.getByTestId("migration-board-submit").click();

    await expect(page).toHaveURL(new RegExp(e2eRoutes.accountMigrationBoard), {
      timeout: 15_000,
    });
    await expect(page.getByTestId("account-migration-board")).toContainText(
      /review/i,
      {
        timeout: 15_000,
      },
    );
    await expectNoAppCrash(page);
  });

  test("regular user cannot moderate migration board posts", async ({
    page,
  }) => {
    const email = uniqueEmail("migration-board-regular");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    await page.goto(e2eRoutes.migrationBoardModeration);
    await expect(page.getByTestId("migration-board-moderation")).toHaveCount(0);
    await expect(page.locator("body")).toContainText(/недостаточно прав/i);
    await expectNoAppCrash(page);
  });
});

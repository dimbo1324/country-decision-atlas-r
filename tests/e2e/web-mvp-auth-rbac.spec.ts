import type { Page } from "@playwright/test";
import { test, expect } from "./helpers/fixtures";
import {
  expectHasMainHeading,
  expectNoAppCrash,
  expectPageReady,
} from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

/** Signed-in nav links live inside the account dropdown in the top bar. */
async function openAccountMenu(page: Page) {
  await page.getByTestId("nav-account-menu-trigger").click();
}

async function logoutViaMenu(page: Page) {
  await openAccountMenu(page);
  await page.getByTestId("nav-logout-button").click();
}

async function registerViaUi(
  page: Page,
  email: string,
  password = "a-very-strong-password-123",
) {
  await page.goto(e2eRoutes.register);
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-display-name").fill("Runtime E2E User");
  await page.getByTestId("register-password").fill(password);
  await page.getByTestId("register-submit").click();
}

test.describe("anonymous auth state", () => {
  test("nav shows sign-in link and no watchlist/data-quality links", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.home);
    await expectPageReady(page);
    await expect(page.getByTestId("nav-sign-in-link")).toBeVisible();
    await expect(page.getByTestId("nav-account-menu-trigger")).toHaveCount(0);
    await expect(page.getByTestId("nav-account-link")).toHaveCount(0);
    await expect(page.getByTestId("nav-watchlist-link")).toHaveCount(0);
    await expect(page.getByTestId("nav-data-quality-link")).toHaveCount(0);
  });

  test("/login renders the login form", async ({ page }) => {
    await page.goto(e2eRoutes.login);
    await expectNoAppCrash(page);
    await expect(page.getByTestId("login-form")).toBeVisible();
    await expect(page.getByTestId("login-email")).toBeVisible();
    await expect(page.getByTestId("login-password")).toBeVisible();
  });

  test("/register renders the register form", async ({ page }) => {
    await page.goto(e2eRoutes.register);
    await expectNoAppCrash(page);
    await expect(page.getByTestId("register-form")).toBeVisible();
  });

  test("/account without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.account);
    await expectNoAppCrash(page);
    await expect(page.getByTestId("account-unauthenticated")).toBeVisible();
  });

  test("/internal/data-quality without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /отчёт качества данных/i);
    await expect(
      page.getByTestId("data-quality-unauthenticated"),
    ).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("login with wrong password shows an error", async ({
    page,
    seededUser,
  }) => {
    // Only the wrong-password login attempt below is the actual subject of
    // this test -- having a valid account to try it against is pure setup,
    // seeded via the API instead of a full UI registration.
    await page.goto(e2eRoutes.account);
    await logoutViaMenu(page);
    await expect(page.getByTestId("nav-sign-in-link")).toBeVisible();

    await page.goto(e2eRoutes.login);
    await page.getByTestId("login-email").fill(seededUser.email);
    await page.getByTestId("login-password").fill("totally-wrong-password");
    await page.getByTestId("login-submit").click();
    await expect(page.getByTestId("login-error")).toBeVisible();
  });
});

test.describe("registration and account flow", () => {
  test("register creates an account and redirects to /account", async ({
    page,
  }) => {
    const email = uniqueEmail("register-flow-user");
    await registerViaUi(page, email);

    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));
    await expect(page.getByTestId("account-view")).toBeVisible();
    await expect(page.getByTestId("account-email")).toHaveText(email);
    await expect(page.getByTestId("account-role")).toHaveText("user");
    await expect(page.getByTestId("account-status")).toHaveText("active");
    await expectNoAppCrash(page);
  });

  test("registering with an already-used email shows an error", async ({
    page,
    seededUser,
  }) => {
    // The already-registered account is pure setup, seeded via the API;
    // only the second (duplicate) registration attempt via the UI form is
    // the actual subject of this test.
    await page.goto(e2eRoutes.account);
    await logoutViaMenu(page);
    await registerViaUi(page, seededUser.email);

    await expect(page.getByTestId("register-error")).toBeVisible();
    await expect(page).toHaveURL(new RegExp(e2eRoutes.register));
  });

  test("logged-in nav exposes account, watchlist and logout controls", async ({
    page,
    seededUser,
  }) => {
    await page.goto(e2eRoutes.account);
    await expect(page.getByTestId("nav-sign-in-link")).toHaveCount(0);
    await openAccountMenu(page);
    await expect(page.getByTestId("nav-account-link")).toBeVisible();
    await expect(page.getByTestId("nav-watchlist-link")).toBeVisible();
    await expect(page.getByTestId("nav-logout-button")).toBeVisible();

    await page.getByTestId("nav-logout-button").click();
    await expect(page.getByTestId("nav-sign-in-link")).toBeVisible();
  });

  test("regular user does not see the data-quality nav link or page", async ({
    page,
    seededUser,
  }) => {
    await page.goto(e2eRoutes.account);
    await openAccountMenu(page);
    await expect(page.getByTestId("nav-data-quality-link")).toHaveCount(0);
    await page.keyboard.press("Escape");

    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /отчёт качества данных/i);
    await expect(page.getByTestId("data-quality-forbidden")).toBeVisible();
    await expectNoAppCrash(page);
  });
});

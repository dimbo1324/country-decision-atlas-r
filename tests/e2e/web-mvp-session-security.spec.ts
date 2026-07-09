import type { Page } from "@playwright/test";
import { test, expect } from "@playwright/test";
import { expectNoAppCrash } from "./helpers/assertions";
import { API_BASE_URL } from "./helpers/env";
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
  await page.getByTestId("register-display-name").fill("Session E2E User");
  await page.getByTestId("register-password").fill(password);
  await page.getByTestId("register-submit").click();
}

test.describe("session security (AE-3 variant B + hardening)", () => {
  test("login issues an httpOnly session cookie invisible to JS", async ({
    page,
    context,
  }) => {
    const email = uniqueEmail("cookie-auth-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    const cookies = await context.cookies();
    const sessionCookie = cookies.find(
      (cookie) => cookie.name === "cda_session",
    );
    expect(sessionCookie).toBeDefined();
    expect(sessionCookie?.httpOnly).toBe(true);

    const jsVisibleCookieNames = await page.evaluate(() => document.cookie);
    expect(jsVisibleCookieNames).not.toContain("cda_session=");
  });

  test("CSRF cookie is readable by JS for double-submit", async ({
    page,
    context,
  }) => {
    const email = uniqueEmail("csrf-cookie-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    const cookies = await context.cookies();
    const csrfCookie = cookies.find((cookie) => cookie.name === "cda_csrf");
    expect(csrfCookie).toBeDefined();
    expect(csrfCookie?.httpOnly).toBe(false);

    const jsVisibleCookies = await page.evaluate(() => document.cookie);
    expect(jsVisibleCookies).toContain("cda_csrf=");
  });

  test("session survives reload without relying on localStorage", async ({
    page,
  }) => {
    const email = uniqueEmail("reload-session-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    const storedToken = await page.evaluate(() =>
      window.localStorage.getItem("cda_auth_token"),
    );
    expect(storedToken).toBeNull();

    await page.reload();
    await expectNoAppCrash(page);
    await expect(page.getByTestId("account-view")).toBeVisible();
    await expect(page.getByTestId("account-email")).toHaveText(email);
  });

  test("revoking all sessions requires a password confirmation", async ({
    page,
  }) => {
    const email = uniqueEmail("revoke-all-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    await page.getByRole("button", { name: "Отозвать все сессии" }).click();
    await expect(page.getByTestId("revoke-all-password-input")).toBeVisible();
    await expectNoAppCrash(page);
  });

  test("mutating request without a CSRF header is rejected", async ({
    page,
  }) => {
    const email = uniqueEmail("csrf-enforced-user");
    await registerViaUi(page, email);
    await expect(page).toHaveURL(new RegExp(e2eRoutes.account));

    const status = await page.evaluate(async (apiBaseUrl) => {
      const response = await fetch(
        `${apiBaseUrl}/api/v1/auth/sessions/revoke-all`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ current_password: "irrelevant" }),
        },
      );
      return response.status;
    }, API_BASE_URL);
    expect(status).toBe(403);
  });
});

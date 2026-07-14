import type { Page } from "@playwright/test";
import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectPageReady } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@example.local`;
}

async function registerViaUi(page: Page, email: string) {
  await page.goto(e2eRoutes.register);
  await page.getByTestId("register-email").fill(email);
  await page.getByTestId("register-display-name").fill("Country Proposal User");
  await page
    .getByTestId("register-password")
    .fill("a-very-strong-password-123");
  await page.getByTestId("register-submit").click();
  await expect(page).toHaveURL(new RegExp(e2eRoutes.account));
}

test.describe("country proposals studio", () => {
  test("/account/country-proposals without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.accountCountryProposals);
    await expectPageReady(page);
    await expect(
      page.getByTestId("country-proposals-unauthenticated"),
    ).toBeVisible();
  });

  test("the wizard view without a session shows the unauthenticated notice", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.countryProposalWizard("00000000-0000-0000-0000-000000000000"),
    );
    await expectPageReady(page);
    await expect(
      page.getByTestId("country-proposal-wizard-unauthenticated"),
    ).toBeVisible();
  });

  test("a logged-in user without the contributor.countries capability sees a permission error, not a crash", async ({
    page,
  }) => {
    // contributor.countries is a capability-gated action (require_capability
    // on the country-contribution router, no role bypass -- confirmed in
    // apps/api/app/api/v1/country_contribution.py) granted only via
    // POST /api/v1/admin/capabilities (require_owner). There is no way to
    // grant it through the public UI, so -- matching the negative-only
    // pattern already used for migration-board moderation, community
    // moderation, and author-metrics -- this test covers the real,
    // reachable behavior for a freshly registered user attempting to
    // create a proposal, rather than a full wizard flow that would require
    // owner-level test setup this suite doesn't have.
    const email = uniqueEmail("country-proposal-no-capability-user");
    await registerViaUi(page, email);

    await page.goto(e2eRoutes.accountCountryProposals);
    await expect(page.getByTestId("country-proposals-list-view")).toBeVisible();

    await page.getByTestId("country-proposal-slug-input").fill("testland");
    await page.getByTestId("country-proposal-name-en-input").fill("Testland");
    await page.getByTestId("country-proposal-name-ru-input").fill("Тестландия");
    await page.getByTestId("country-proposal-iso2-input").fill("TL");
    await page.getByTestId("country-proposal-iso3-input").fill("TLD");
    await page
      .getByTestId("country-proposal-justification-input")
      .fill("E2E capability-gate check.");
    await page.getByTestId("country-proposal-create-submit").click();

    await expect(page.locator("body")).toContainText(
      /insufficient_capability|Не удалось создать заявку/i,
    );
    await expectNoAppCrash(page);
  });
});

import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test.describe("argentina core country slice", () => {
  test("/countries includes Argentina in the list", async ({ page }) => {
    await page.goto(e2eRoutes.countries);
    await expectNoAppCrash(page);
    await expect(page.getByText(/argentina|аргентина/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("/countries/argentina opens without crash", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina"));
    await expectNoAppCrash(page);
  });

  test("/countries/argentina?locale=ru has main heading", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectHasMainHeading(page, /argentina|аргентина/i);
    await expectNoAppCrash(page);
  });

  test("/countries/argentina?locale=en has main heading", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "en"));
    await expectHasMainHeading(page, /argentina/i);
    await expectNoAppCrash(page);
  });

  test("Argentina page renders the CII section", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    const ciiSection = page.locator('[data-testid="cii-section"]');
    await expect(ciiSection).toBeVisible();
    const emptyState = ciiSection.getByText(
      /ещё не рассчитаны|не рассчитан|данные.*отсутствуют/i,
    );
    const ciiBlock = ciiSection.locator('[data-testid="cii-block"]');
    await expect(emptyState.or(ciiBlock).first()).toBeVisible();
  });

  test("Argentina page renders current legal signals", async ({ page }) => {
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(
      page.locator('[data-testid="country-legal-signals"]'),
    ).toBeVisible();
  });

  test("Russia and Uruguay remain accessible after Argentina added", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.country("russia", "ru"));
    await expectHasMainHeading(page, /россия|russia/i);
    await expectNoAppCrash(page);

    await page.goto(e2eRoutes.country("uruguay", "ru"));
    await expectHasMainHeading(page, /уругвай|uruguay/i);
    await expectNoAppCrash(page);
  });

  test("dossier renders the flat rail layout by default (web_dossier_v2 disabled)", async ({
    page,
  }) => {
    // web_dossier_v2 seeds disabled (database/migrations/056_web_dossier_v2_flag.sql)
    // -- there's no admin write endpoint for feature flags in this codebase yet
    // (GET /platform/features is read-only), so flipping it on for an
    // automated E2E run isn't cleanly possible without direct DB access.
    // Matching the same negative-only pattern already used for
    // capability-gated surfaces (author-metrics, country-proposals,
    // migration-board): cover the real, always-reachable default state here.
    // The tabbed on-state was verified manually against a live DB flip
    // (all 5 tabs, deep-linking via ?tab=, zero console errors).
    await page.goto(e2eRoutes.country("argentina", "ru"));
    await expectNoAppCrash(page);
    await expect(page.getByTestId("dossier-rail")).toBeVisible();
    await expect(page.getByTestId("dossier-rail-link-cii")).toBeVisible();
    await expect(page.getByTestId("dossier-rail-link-community")).toBeVisible();
    await expect(page.getByTestId("country-dossier-tabs")).toHaveCount(0);
    await expect(page.getByRole("tablist")).toHaveCount(0);
  });
});

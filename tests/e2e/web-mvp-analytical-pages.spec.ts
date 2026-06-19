import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";
import { API_BASE_URL, ADMIN_TOKEN } from "./helpers/env";

test.describe("legal signals page", () => {
  test("/legal-signals?country_slug=russia&locale=ru applies filter", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ country_slug: "russia", locale: "ru" }));
    await expectHasMainHeading(page, /traceable decision signals/i);

    await expect(page.locator(".filterBar")).toBeVisible();

    const countrySelect = page.locator("#ls-country");
    await expect(countrySelect).toBeVisible();
    await expect(countrySelect).toHaveValue("russia");

    const hasItems = await page
      .locator(".signalList")
      .isVisible()
      .catch(() => false);
    const hasEmpty = await page
      .getByText(/no legal signals match/i)
      .isVisible()
      .catch(() => false);
    expect(hasItems || hasEmpty).toBe(true);

    await expectNoAppCrash(page);
  });

  test("/legal-signals?impact_direction=positive&locale=en does not crash", async ({
    page,
  }) => {
    await page.goto(
      e2eRoutes.legalSignals({
        country_slug: "uruguay",
        impact_direction: "positive",
        locale: "en",
      }),
    );
    await expectHasMainHeading(page, /traceable decision signals/i);
    await expectNoAppCrash(page);
  });

  test("legal signals summary cards appear when data loads", async ({ page }) => {
    await page.goto(e2eRoutes.legalSignals({ locale: "en" }));
    await expectHasMainHeading(page, /traceable decision signals/i);
    await expect(page.getByText(/signals shown/i)).toBeVisible({ timeout: 10_000 });
    await expectNoAppCrash(page);
  });

  test("legal signals country card link exists when items are present", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.legalSignals({ country_slug: "russia", locale: "en" }));
    await expectHasMainHeading(page, /traceable decision signals/i);
    const hasItems = await page
      .locator(".signalList")
      .isVisible()
      .catch(() => false);
    if (hasItems) {
      await expect(
        page.getByRole("link", { name: /open country card/i }).first(),
      ).toBeVisible();
    }
  });
});

test.describe("sources page", () => {
  test("/sources?country_slug=uruguay&locale=ru applies filter", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ country_slug: "uruguay", locale: "ru" }));
    await expectHasMainHeading(page, /evidence sources/i);

    await expect(page.locator(".filterBar")).toBeVisible();

    const countrySelect = page.locator("#src-country");
    await expect(countrySelect).toBeVisible();
    await expect(countrySelect).toHaveValue("uruguay");

    const hasItems = await page
      .locator(".sourceList")
      .isVisible()
      .catch(() => false);
    const hasEmpty = await page
      .getByText(/no sources match/i)
      .isVisible()
      .catch(() => false);
    expect(hasItems || hasEmpty).toBe(true);

    await expectNoAppCrash(page);
  });

  test("/sources?confidence=high&locale=en does not crash", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ confidence: "high", locale: "en" }));
    await expectHasMainHeading(page, /evidence sources/i);
    await expectNoAppCrash(page);
  });

  test("external source links have target=_blank and rel=noreferrer", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.sources({ locale: "en" }));
    await expectHasMainHeading(page, /evidence sources/i);

    const hasItems = await page
      .locator(".sourceList")
      .isVisible()
      .catch(() => false);
    if (hasItems) {
      const externalLinks = page.locator("a.externalLink");
      const count = await externalLinks.count();
      if (count > 0) {
        const first = externalLinks.first();
        await expect(first).toHaveAttribute("target", "_blank");
        const rel = await first.getAttribute("rel");
        expect(rel).toContain("noreferrer");
      }
    }
  });

  test("sources country card link exists when items are present", async ({ page }) => {
    await page.goto(e2eRoutes.sources({ locale: "en" }));
    await expectHasMainHeading(page, /evidence sources/i);
    const hasItems = await page
      .locator(".sourceList")
      .isVisible()
      .catch(() => false);
    if (hasItems) {
      await expect(page.getByRole("link", { name: /view/i }).first()).toBeVisible();
    }
  });
});

test.describe("data quality page", () => {
  test("/internal/data-quality opens with correct heading", async ({ page }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /data quality report/i);
    await expectNoAppCrash(page);
  });

  test("/internal/data-quality shows report or token-required state", async ({
    page,
  }) => {
    await page.goto(e2eRoutes.dataQuality);
    await expectHasMainHeading(page, /data quality report/i);

    const hasReport = await page
      .locator("[data-testid='data-quality-report']")
      .isVisible()
      .catch(() => false);
    const hasTokenError = await page
      .getByText(/ADMIN_TOKEN/i)
      .isVisible()
      .catch(() => false);

    expect(hasReport || hasTokenError).toBe(true);
    await expectNoAppCrash(page);
  });

  test("data quality API health check via request", async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/health`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ok");
  });

  test("data quality report accessible via API", async ({ request }) => {
    const response = await request.get(
      `${API_BASE_URL}/api/v1/admin/data-quality/report`,
      {
        headers: { "X-Admin-Token": ADMIN_TOKEN },
      },
    );
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("valid");
    expect(body).toHaveProperty("overall_status");
  });
});

test.describe("accessibility semantics", () => {
  test("home page has h1 and accessible links", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toBeVisible();
    const links = page.getByRole("link");
    const count = await links.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < Math.min(count, 5); i++) {
      const name = await links.nth(i).textContent();
      expect(name?.trim().length).toBeGreaterThan(0);
    }
  });

  test("countries page has h1 and country links with non-empty names", async ({
    page,
  }) => {
    await page.goto("/countries");
    await expect(page.locator("h1")).toBeVisible();
    const cardLinks = page.getByRole("link", { name: /view country card/i });
    await expect(cardLinks.first()).toBeVisible();
  });

  test("decision page form inputs have labels", async ({ page }) => {
    await page.goto("/decision");
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByLabel(/origin country/i)).toBeVisible();
    await expect(page.getByLabel(/scenario/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /run decision/i })).toBeVisible();
  });
});

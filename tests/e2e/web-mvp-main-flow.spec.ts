import { test, expect } from "@playwright/test";
import { expectNoAppCrash, expectHasMainHeading } from "./helpers/assertions";
import { e2eRoutes } from "./helpers/routes";

test("main MVP user flow: home → countries → Russia → Uruguay → decision → result → country card", async ({
  page,
}) => {
  test.setTimeout(60_000);
  await page.goto(e2eRoutes.home);
  await expectHasMainHeading(page, /country decision atlas/i);
  await expect(
    page.getByRole("link", { name: /перейти к странам/i }).first(),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: /запустить подбор/i }).first(),
  ).toBeVisible();
  await expectNoAppCrash(page);

  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Страны", exact: true })
    .click();
  await expectHasMainHeading(page, /карточки стран для подбора/i);
  await expect(page.getByText(/россия|russia/i).first()).toBeVisible();
  await expect(page.getByText(/уругвай|uruguay/i).first()).toBeVisible();

  await page.goto(e2eRoutes.country("russia", "ru"));
  // Scoped to <main>: Next.js can leave a hidden Suspense streaming
  // marker (a second, invisible DOM copy under a transient `id="S:0"`
  // node) alongside the real content, which trips a bare-testid
  // strict-mode check even though only one copy is ever visible.
  await expect(page.getByRole("main").getByTestId("country-card")).toBeVisible({
    timeout: 15000,
  });
  await expect(page.locator("h1").first()).toBeVisible();
  await expect(
    page.locator("h2").filter({ hasText: /оценки сценариев/i }),
  ).toBeVisible();
  await expectNoAppCrash(page);

  await page.goto(e2eRoutes.country("uruguay", "ru"));
  await expect(page.locator("h1").first()).toBeVisible();
  await expect(
    page.locator("h2").filter({ hasText: /оценки сценариев/i }),
  ).toBeVisible();
  await expectNoAppCrash(page);

  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Подбор", exact: true })
    .click();
  await expectHasMainHeading(page, /запустить подбор страны/i);
  await expect(
    page.getByRole("combobox", { name: /страна отправления/i }),
  ).toBeVisible();
  await expect(page.getByRole("combobox", { name: /сценарий/i })).toBeVisible();

  const runButton = page.getByRole("button", { name: /запустить подбор/i });
  await expect(runButton).toBeVisible();
  await runButton.click();

  await expect(page.locator("[data-testid='decision-results']")).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText("Полный рейтинг")).toBeVisible();
  await expect(page.getByTestId("result-card").first()).toBeVisible();
  await expectNoAppCrash(page);

  await page
    .getByRole("link", { name: /карточка страны/i })
    .first()
    .click();
  await expect(page.locator("h1").first()).toBeVisible();
  await expectNoAppCrash(page);
});

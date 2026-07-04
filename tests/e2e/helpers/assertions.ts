import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

const NEXT_ERROR_TEXTS = [
  "Unhandled Runtime Error",
  "Application error: a client-side exception has occurred",
];

export async function expectNoAppCrash(page: Page) {
  for (const text of NEXT_ERROR_TEXTS) {
    await expect(page.getByText(text, { exact: false })).not.toBeVisible();
  }
}

export async function expectPageReady(page: Page) {
  await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible();
  await expectNoAppCrash(page);
}

export async function expectHasMainHeading(page: Page, text: string | RegExp) {
  await expect(
    page.getByRole("heading", { name: text, level: 1 }),
  ).toBeVisible();
}

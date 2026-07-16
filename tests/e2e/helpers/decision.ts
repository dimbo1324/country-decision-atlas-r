import type { Page } from "@playwright/test";

/** Jumps directly to a step of DecisionRunForm's 4-step wizard (Цель /
 * Откуда / Приоритеты / Запуск) via its step-indicator button -- the
 * wizard allows non-linear navigation, so tests don't need to click
 * through every intermediate step to reach the one they care about. */
export async function goToDecisionStep(page: Page, step: 1 | 2 | 3 | 4) {
  await page.getByTestId(`decision-step-${step}`).click();
}

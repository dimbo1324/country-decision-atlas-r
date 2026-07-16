import { defineConfig, devices } from "@playwright/test";

const WEB_BASE_URL = process.env.WEB_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "tests/e2e",
  // Raised from 30s: page.goto() under concurrent worker load (4 browsers
  // against one next start + one Postgres) occasionally needs more than
  // 30s end-to-end, even though nothing is actually hung. expect.timeout
  // stays at 10s so a genuine stuck assertion still fails fast.
  timeout: 45_000,
  expect: { timeout: 10_000 },
  // One retry turns a load-related timeout into a visible "flaky" result
  // (Playwright's own reporter/exit summary distinguishes flaky-then-passed
  // from a clean pass) instead of a hard failure that's indistinguishable
  // from a real regression.
  retries: 1,
  // The app under test is a single next start process backed by one
  // Postgres/API instance; Playwright's CPU-count-based default worker
  // count (11+ on this hardware) creates enough concurrent SSR/DB load to
  // blow past page-load timeouts across unrelated specs. 4 is the highest
  // count that stayed reliably green in local verification.
  workers: 4,
  outputDir: "local-artifacts/test-results",
  reporter: [
    ["list"],
    [
      "html",
      {
        outputFolder: "local-artifacts/playwright-report",
        open: "never",
      },
    ],
  ],
  use: {
    baseURL: WEB_BASE_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm --filter @country-decision-atlas/web start",
    url: WEB_BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      APP_ENV: "local",
    },
  },
});

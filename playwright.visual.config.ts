import { defineConfig, devices } from "@playwright/test";

const WEB_BASE_URL = process.env.WEB_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "tests/visual",
  timeout: 30_000,
  expect: {
    timeout: 10_000,
    toHaveScreenshot: { maxDiffPixelRatio: 0.02 },
  },
  retries: 0,
  workers: 2,
  outputDir: "local-artifacts/visual-test-results",
  reporter: [
    ["list"],
    [
      "html",
      {
        outputFolder: "local-artifacts/playwright-visual-report",
        open: "never",
      },
    ],
  ],
  use: {
    baseURL: WEB_BASE_URL,
    trace: "retain-on-failure",
    // `reducedMotion` is not a top-level Playwright TestOption (root
    // configs are not typechecked by any gate, so the mistake was
    // silent); it must travel via contextOptions to actually reach
    // window.matchMedia in pages under test. Verified empirically in the
    // Stage-1 wave: top-level -> matchMedia reads false, contextOptions/
    // emulateMedia -> reads true.
    contextOptions: { reducedMotion: "reduce" },
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

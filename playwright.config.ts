import { defineConfig, devices } from "@playwright/test";

const WEB_BASE_URL = process.env.WEB_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 30_000,
  retries: 0,
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
    command: "pnpm --filter @country-decision-atlas/web dev",
    url: WEB_BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});

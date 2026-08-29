import { defineConfig, devices } from "@playwright/test";

const PORT = 8791;

export default defineConfig({
  testDir: "./test",
  fullyParallel: false,
  timeout: 60_000,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `node test/serve.mjs . ${PORT}`,
    url: `http://127.0.0.1:${PORT}/nsigii-viewer.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 20_000,
  },
});

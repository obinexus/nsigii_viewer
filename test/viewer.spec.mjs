/*
 * Browser tests for the dispatch front end (brief items E and F), plus the
 * wrapper-receipt and inert-bytes paths.
 *
 * Prerequisites (CI sets all three):
 *   NSIGII_CORE_WEB  dir holding nsigii.js / nsigii.wasm / nsigii-adapter.mjs
 *                    (from `make wasm` in obinexus/nsigii_project)
 *   NSIGII_C_BIN     the native `nsigii` binary (to build the CORE_V1 fixture)
 *   NSIGII_CLI       path to obinexusmk2/nsigii's built dist/cli.js
 *                    (optional — the wrapper test skips without it)
 */
import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { copyFileSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CORE_WEB = process.env.NSIGII_CORE_WEB;
const C_BIN = process.env.NSIGII_C_BIN;
const CLI = process.env.NSIGII_CLI;

const staged = [];
const stage = (name) => { staged.push(resolve(ROOT, name)); return resolve(ROOT, name); };

test.beforeAll(() => {
  test.skip(!CORE_WEB || !C_BIN, "set NSIGII_CORE_WEB and NSIGII_C_BIN");
  for (const f of ["nsigii.js", "nsigii.wasm", "nsigii-adapter.mjs"]) {
    copyFileSync(resolve(CORE_WEB, f), stage(f));
  }
  execFileSync(C_BIN, ["pack", resolve(ROOT, "donut.nsigii"), stage("donut.core.nsigii")]);
  if (CLI) {
    execFileSync("node", [CLI, "wrap", resolve(ROOT, "donut.nsigii"), "-o", stage("donut.wrapped.nsigii")], { stdio: "ignore" });
  }
});

test.afterAll(() => { for (const p of staged) rmSync(p, { force: true }); });

async function rendered(page) {
  await expect(page.locator("#rStatus")).toHaveText("interactive", { timeout: 30_000 });
  await expect(page.locator("#kindBadge")).toHaveText("interactive ascii");
  await expect
    .poll(() => page.locator("#ascii").innerHTML().then((h) => h.length), { timeout: 10_000 })
    .toBeGreaterThan(100);
}

test("E — opens the original legacy donut", async ({ page }) => {
  await page.goto("/nsigii-viewer.html?src=donut.nsigii");
  await rendered(page);
  await expect(page.locator("#hdrList")).toContainText("7.1.0A");
  await expect(page.locator("#hdrList")).toContainText("declared");
});

test("F — opens a CORE_V1-wrapped legacy donut through the WASM decoder", async ({ page }) => {
  await page.goto("/nsigii-viewer.html?src=donut.core.nsigii");
  await rendered(page);
  await expect(page.locator("#hdrList")).toContainText("decoded"); // "▸ decoded" — it went through WASM
  await expect(page.locator("#hdrList")).toContainText("7.1.0A");
});

test("wrapper — receipt only, never executed", async ({ page }) => {
  test.skip(!CLI, "set NSIGII_CLI to obinexusmk2/nsigii dist/cli.js");
  await page.goto("/nsigii-viewer.html?src=donut.wrapped.nsigii");
  await expect(page.locator("#rStatus")).toHaveText("wrapper receipt");
  await expect(page.locator("#plate")).toContainText("does not execute");
  await expect(page.locator("#ascii")).toBeHidden();
});

test("unknown — inert bytes, download only", async ({ page }) => {
  await page.goto("/nsigii-viewer.html?src=INTEGRATION.md");
  await expect(page.locator("#rStatus")).toHaveText("unknown — inert");
  await expect(page.locator("#plate")).toContainText("nothing is decoded, rendered, or executed");
  await expect(page.locator("#plate a[download]")).toBeVisible();
});

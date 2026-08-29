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
import { copyFileSync, existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CORE_WEB = process.env.NSIGII_CORE_WEB;
const C_BIN = process.env.NSIGII_C_BIN;
const CLI = process.env.NSIGII_CLI;
// dist/browser/constitutional.mjs sits beside dist/cli.js in the built runtime
const CONSTITUTIONAL = CLI ? resolve(dirname(CLI), "browser", "constitutional.mjs") : "";

const staged = [];
const stage = (name) => { staged.push(resolve(ROOT, name)); return resolve(ROOT, name); };
let CONSTITUTIONAL_OK = false;

test.beforeAll(() => {
  test.skip(!CORE_WEB || !C_BIN, "set NSIGII_CORE_WEB and NSIGII_C_BIN");
  for (const f of ["nsigii.js", "nsigii.wasm", "nsigii-adapter.mjs"]) {
    copyFileSync(resolve(CORE_WEB, f), stage(f));
  }
  execFileSync(C_BIN, ["pack", resolve(ROOT, "donut.nsigii"), stage("donut.core.nsigii")]);
  if (CLI) {
    execFileSync("node", [CLI, "wrap", resolve(ROOT, "donut.nsigii"), "-o", stage("donut.wrapped.nsigii")], { stdio: "ignore" });
  }
  if (CLI && CONSTITUTIONAL && existsSync(CONSTITUTIONAL)) {
    CONSTITUTIONAL_OK = true;
    copyFileSync(CONSTITUTIONAL, stage("nsigii-constitutional.mjs"));
    // G fixture: wrap the CORE_V1-packed donut in a constitutional wrapper
    execFileSync("node", [CLI, "wrap", resolve(ROOT, "donut.core.nsigii"), "-o", stage("donut.wrapped-core.nsigii")], { stdio: "ignore" });
    // tampered fixture: flip a payload byte so verification fails
    const bad = readFileSync(resolve(ROOT, "donut.wrapped.nsigii"));
    bad[Math.floor(bad.length / 2)] ^= 0xff;
    writeFileSync(stage("donut.wrapped-bad.nsigii"), bad);
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

test("wrapper — verifies then descends to the legacy renderer", async ({ page }) => {
  test.skip(!CLI, "set NSIGII_CLI to obinexusmk2/nsigii dist/cli.js");
  await page.goto("/nsigii-viewer.html?src=donut.wrapped.nsigii");
  await rendered(page);
  await expect(page.locator("#hdrList")).toContainText("extracted"); // "▸ extracted" — it was verified + unwrapped
  await expect(page.locator("#hdrList")).toContainText("7.1.0A");
});

test("G — wrapper ▸ CORE_V1 ▸ legacy donut, all three layers", async ({ page }) => {
  test.skip(!CLI || !CONSTITUTIONAL_OK, "needs NSIGII_CLI and the browser constitutional module");
  await page.goto("/nsigii-viewer.html?src=donut.wrapped-core.nsigii");
  await rendered(page);
  await expect(page.locator("#hdrList")).toContainText("extracted"); // verified wrapper
  await expect(page.locator("#hdrList")).toContainText("decoded");   // WASM CORE_V1 decode
  await expect(page.locator("#hdrList")).toContainText("7.1.0A");
});

test("I (browser) — a tampered wrapper is not released, only a receipt", async ({ page }) => {
  test.skip(!CLI || !CONSTITUTIONAL_OK, "needs NSIGII_CLI and the browser constitutional module");
  await page.goto("/nsigii-viewer.html?src=donut.wrapped-bad.nsigii");
  await expect(page.locator("#rStatus")).toHaveText(/wrapper receipt|verified — not released/, { timeout: 20_000 });
  await expect(page.locator("#plate")).toContainText("not released");
  await expect(page.locator("#plate")).toContainText("does not execute");
  await expect(page.locator("#ascii")).toBeHidden();
});

test("unknown — inert bytes, download only", async ({ page }) => {
  await page.goto("/nsigii-viewer.html?src=INTEGRATION.md");
  await expect(page.locator("#rStatus")).toHaveText("unknown — inert");
  await expect(page.locator("#plate")).toContainText("nothing is decoded, rendered, or executed");
  await expect(page.locator("#plate a[download]")).toBeVisible();
});

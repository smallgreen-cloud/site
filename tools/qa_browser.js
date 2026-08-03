#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { AxeBuilder } = require("@axe-core/playwright");

const root = path.resolve(__dirname, "..");
const dist = path.join(root, "dist");
const baseUrl = (process.env.QA_BASE_URL || "http://127.0.0.1:8765").replace(/\/$/, "");
const widths = [375, 768, 1280];

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(target) : [target];
  });
}

function routeFor(file) {
  const relative = path.relative(dist, file).split(path.sep).join("/");
  if (relative === "index.html") return "/";
  return `/${relative.replace(/index\.html$/, "")}`;
}

async function main() {
  const routes = walk(dist)
    .filter((file) => file.endsWith("index.html"))
    .map(routeFor)
    .filter((route) => !route.startsWith("/s/"));
  const browser = await chromium.launch({ headless: true });
  const failures = [];

  for (const width of widths) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    const page = await context.newPage();
    for (const route of routes) {
      const consoleErrors = [];
      const onConsole = (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      };
      page.on("console", onConsole);
      const response = await page.goto(`${baseUrl}${route}`, { waitUntil: "domcontentloaded" });
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      if (!response || response.status() !== 200 || overflow > 1 || consoleErrors.length) {
        failures.push({ width, route, status: response && response.status(), overflow, consoleErrors });
      }
      if (width === 375) {
        const axe = await new AxeBuilder({ page }).analyze();
        const blocking = axe.violations.filter((item) => ["serious", "critical"].includes(item.impact));
        if (blocking.length) {
          failures.push({ width, route, accessibility: blocking.map((item) => item.id) });
        }
      }
      page.removeListener("console", onConsole);
    }
    await context.close();
  }
  await browser.close();

  if (failures.length) {
    console.error(JSON.stringify({ failures }, null, 2));
    process.exit(1);
  }
  console.log(`browser QA passed: ${routes.length} routes × ${widths.length} viewports`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

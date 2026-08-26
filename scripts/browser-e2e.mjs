import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , appUrl, chromePath, evidenceDir, playwrightEntry] = process.argv;

if (!appUrl || !chromePath || !evidenceDir || !playwrightEntry) {
  throw new Error(
    'usage: browser-e2e.mjs <app-url> <chrome-path> <evidence-dir> <playwright-entry>',
  );
}

const { chromium } = await import(pathToFileURL(playwrightEntry).href);

await fs.mkdir(evidenceDir, { recursive: true });

const consoleErrors = [];
const pageErrors = [];
const requestFailures = [];
const httpErrors = [];
const externalRequests = [];
let browser;

function isLocalUrl(rawUrl) {
  const url = new URL(rawUrl);
  return url.hostname === 'localhost' || url.hostname === '127.0.0.1';
}

async function assertText(locator, expected) {
  await locator.waitFor({ state: 'visible' });
  assert.equal((await locator.textContent())?.trim(), expected);
}

async function clickAndAssert(page, spec) {
  const responsePromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === spec.endpoint && response.request().method() === 'POST';
  });

  await page.getByRole('button', { name: spec.button, exact: true }).click();
  const response = await responsePromise;
  assert.equal(response.ok(), true, `${spec.endpoint} returned ${response.status()}`);

  const payload = await response.json();
  for (const [key, expected] of Object.entries(spec.api)) {
    assert.deepEqual(payload[key], expected, `${spec.endpoint} field ${key}`);
  }

  await fs.writeFile(
    path.join(evidenceDir, spec.jsonName),
    `${JSON.stringify(payload, null, 2)}\n`,
    'utf8',
  );

  await assertText(page.locator('.decision-badge'), spec.badge);
  await assertText(page.locator('.reason-code'), spec.reason);
  await page.screenshot({
    path: path.join(evidenceDir, spec.screenshotName),
    animations: 'disabled',
  });
}

try {
  browser = await chromium.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--disable-gpu', '--hide-scrollbars', '--no-first-run'],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const page = await context.newPage();

  page.on('console', (message) => {
    if (message.type() === 'error') {
      consoleErrors.push({ text: message.text(), location: message.location() });
    }
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('requestfailed', (request) => {
    requestFailures.push(`${request.method()} ${request.url()}`);
  });
  page.on('request', (request) => {
    const url = request.url();
    if (/^https?:/u.test(url) && !isLocalUrl(url)) {
      externalRequests.push(`${request.method()} ${url}`);
    }
  });
  page.on('response', (response) => {
    if (response.status() >= 400) {
      httpErrors.push({ status: response.status(), url: response.url() });
    }
  });

  const initialResponse = await page.goto(appUrl, { waitUntil: 'domcontentloaded' });
  assert.ok(initialResponse?.ok(), `application returned ${initialResponse?.status()}`);
  await page.getByRole('heading', { name: 'AgentGuard' }).waitFor();

  await clickAndAssert(page, {
    button: 'Review Firewall',
    endpoint: '/api/review',
    badge: 'APPROVAL REQUIRED',
    reason: 'HUMAN_APPROVAL_REQUIRED',
    jsonName: 'proposal.json',
    screenshotName: 'proposal.png',
    api: {
      decision: 'APPROVAL_REQUIRED',
      reason: 'HUMAN_APPROVAL_REQUIRED',
      beforeAction: 'COUNT',
      requestedAction: 'BLOCK',
      actualAction: 'COUNT',
      mutationPerformed: false,
    },
  });

  await clickAndAssert(page, {
    button: 'Approve Once',
    endpoint: '/api/approve',
    badge: 'ALLOW',
    reason: 'APPROVAL_VALID',
    jsonName: 'approval-valid.json',
    screenshotName: 'approval-valid.png',
    api: {
      decision: 'ALLOW',
      reason: 'APPROVAL_VALID',
      beforeAction: 'COUNT',
      requestedAction: 'BLOCK',
      actualAction: 'BLOCK',
      mutationPerformed: true,
      verified: true,
      audit: 'RECORDED',
    },
  });

  const resetResponsePromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === '/api/reset' && response.request().method() === 'POST';
  });
  await page.getByRole('button', { name: 'Reset', exact: true }).click();
  const resetResponse = await resetResponsePromise;
  assert.equal(resetResponse.ok(), true, `/api/reset returned ${resetResponse.status()}`);

  await clickAndAssert(page, {
    button: 'Try Approval Bypass',
    endpoint: '/api/bypass',
    badge: 'DENY',
    reason: 'HUMAN_APPROVAL_REQUIRED',
    jsonName: 'bypass.json',
    screenshotName: 'bypass-denied.png',
    api: {
      decision: 'DENY',
      reason: 'HUMAN_APPROVAL_REQUIRED',
      beforeAction: 'COUNT',
      requestedAction: 'BLOCK',
      actualAction: 'COUNT',
      mutationPerformed: false,
      verified: false,
    },
  });

  assert.deepEqual(pageErrors, [], 'browser page errors');
  assert.deepEqual(requestFailures, [], 'browser request failures');
  assert.deepEqual(externalRequests, [], 'unexpected external requests');

  const result = {
    result: consoleErrors.length === 0 && httpErrors.length === 0
      ? 'PASS'
      : 'PASS_WITH_BROWSER_WARNINGS',
    evidenceMode: 'INTERACTIVE_PLAYWRIGHT',
    browser: await browser.version(),
    viewport: '1920x1080',
    uiActions: ['Review Firewall', 'Approve Once', 'Reset', 'Try Approval Bypass'],
    apiAssertions: ['proposal', 'approval-valid', 'bypass-denied'],
    domAssertions: ['decision badge', 'reason code'],
    consoleErrors,
    pageErrors,
    requestFailures,
    httpErrors,
    externalRequests,
    screenshots: ['proposal.png', 'approval-valid.png', 'bypass-denied.png'],
  };

  await fs.writeFile(
    path.join(evidenceDir, 'result.json'),
    `${JSON.stringify(result, null, 2)}\n`,
    'utf8',
  );
  process.stdout.write(`PLAYWRIGHT_E2E=${result.result}\n`);
} finally {
  await browser?.close();
}

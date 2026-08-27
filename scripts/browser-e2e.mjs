import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , appUrl, chromePath, evidenceDir, playwrightEntry, story = 'waf'] = process.argv;

if (!appUrl || !chromePath || !evidenceDir || !playwrightEntry) {
  throw new Error(
    'usage: browser-e2e.mjs <app-url> <chrome-path> <evidence-dir> <playwright-entry>',
  );
}
if (!['waf', 'compliance'].includes(story)) {
  throw new Error('story must be waf or compliance');
}

const compliance = story === 'compliance';
const journey = compliance
  ? {
      heading: 'Compliance Guard',
      reviewButton: 'Scan S3 Compliance',
      before: '2 NON_COMPLIANT',
      requested: '2 COMPLIANT',
      afterApproval: '2 COMPLIANT',
      afterBypass: '2 NON_COMPLIANT',
    }
  : {
      heading: 'AgentGuard',
      reviewButton: 'Review Firewall',
      before: 'COUNT',
      requested: 'BLOCK',
      afterApproval: 'BLOCK',
      afterBypass: 'COUNT',
    };

const { chromium } = await import(pathToFileURL(playwrightEntry).href);

await fs.mkdir(evidenceDir, { recursive: true });

const consoleErrors = [];
const pageErrors = [];
const requestFailures = [];
const httpErrors = [];
const externalRequests = [];
const screenshotDetails = [];
let browser;

const fullViewport = { width: 1920, height: 1080 };
const slideViewport = { width: 1200, height: 900 };

function isLocalUrl(rawUrl) {
  const url = new URL(rawUrl);
  return url.hostname === 'localhost' || url.hostname === '127.0.0.1';
}

async function assertText(locator, expected) {
  await locator.waitFor({ state: 'visible' });
  assert.equal((await locator.textContent())?.trim(), expected);
}

async function assertIncludes(locator, expected, label) {
  await locator.waitFor({ state: 'visible' });
  const actual = (await locator.textContent()) || '';
  assert.ok(actual.includes(expected), `${label} is missing ${expected}`);
}

async function captureComplianceScreenshots(page, screenshotBase) {
  await page.setViewportSize(fullViewport);
  const fullName = `${screenshotBase}-full.png`;
  await page.screenshot({
    path: path.join(evidenceDir, fullName),
    animations: 'disabled',
  });

  await page.setViewportSize(slideViewport);
  const regions = [
    page.locator('.message.user').last(),
    page.getByRole('region', { name: 'S3 compliance findings' }),
    page.getByRole('complementary', { name: 'AgentGuard decision' }),
  ];
  const boxes = [];
  for (const region of regions) {
    await region.waitFor({ state: 'visible' });
    const box = await region.boundingBox();
    assert.ok(box, 'presentation evidence region has no bounding box');
    boxes.push(box);
  }

  const margin = 24;
  const calculatedX1 = Math.max(0, Math.min(...boxes.map((box) => box.x)) - margin);
  const x1 = calculatedX1 < 64 ? 0 : calculatedX1;
  const y1 = Math.max(0, Math.min(...boxes.map((box) => box.y)) - margin);
  const x2 = Math.min(
    slideViewport.width,
    Math.max(...boxes.map((box) => box.x + box.width)) + margin,
  );
  const y2 = Math.min(
    slideViewport.height,
    Math.max(...boxes.map((box) => box.y + box.height)) + margin,
  );
  const clip = {
    x: Math.floor(x1),
    y: Math.floor(y1),
    width: Math.ceil(x2 - x1),
    height: Math.ceil(y2 - y1),
  };
  assert.ok(clip.width >= 900 && clip.width <= slideViewport.width, 'invalid slide width');
  assert.ok(clip.height >= 600 && clip.height <= 1200, 'invalid slide height');

  const slideName = `${screenshotBase}-slide.png`;
  await page.screenshot({
    path: path.join(evidenceDir, slideName),
    animations: 'disabled',
    clip,
  });
  screenshotDetails.push(
    { name: fullName, width: fullViewport.width, height: fullViewport.height, mode: 'full' },
    { name: slideName, width: clip.width, height: clip.height, mode: 'focused' },
  );
  await page.setViewportSize(fullViewport);
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
  if (compliance) {
    assert.equal(payload.findings.length, 2, `${spec.endpoint} finding count`);
    assert.deepEqual(
      payload.findings.map((finding) => finding.control),
      ['S3_BUCKET_SSL_REQUESTS_ONLY', 'S3_BUCKET_PUBLIC_READ_PROHIBITED'],
      `${spec.endpoint} exact controls`,
    );
    assert.deepEqual(
      payload.findings.map((finding) => finding.actual),
      spec.findingStatuses,
      `${spec.endpoint} finding statuses`,
    );
  }

  await fs.writeFile(
    path.join(evidenceDir, spec.jsonName),
    `${JSON.stringify(payload, null, 2)}\n`,
    'utf8',
  );

  await assertText(page.locator('.decision-badge'), spec.badge);
  await assertText(page.locator('.reason-code'), spec.reason);
  if (compliance) {
    const findings = page.getByRole('region', { name: 'S3 compliance findings' });
    await assertIncludes(findings, 'S3_BUCKET_SSL_REQUESTS_ONLY', 'compliance findings');
    await assertIncludes(findings, 'S3_BUCKET_PUBLIC_READ_PROHIBITED', 'compliance findings');
    for (const status of spec.findingStatuses) {
      await assertIncludes(findings, status, 'compliance findings');
    }
    await assertIncludes(page.locator('.audit-strip'), `Mutation: ${spec.api.mutationPerformed ? 'YES' : 'NO'}`, 'audit strip');
    await captureComplianceScreenshots(page, spec.screenshotBase);
  } else {
    await page.screenshot({
      path: path.join(evidenceDir, spec.screenshotName),
      animations: 'disabled',
    });
    screenshotDetails.push({
      name: spec.screenshotName,
      width: fullViewport.width,
      height: fullViewport.height,
      mode: 'full',
    });
  }
}

try {
  browser = await chromium.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--disable-gpu', '--hide-scrollbars', '--no-first-run'],
  });

  const context = await browser.newContext({
    viewport: fullViewport,
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
  await page.getByRole('heading', { name: journey.heading }).waitFor();

  await clickAndAssert(page, {
    button: journey.reviewButton,
    endpoint: '/api/review',
    badge: 'APPROVAL REQUIRED',
    reason: 'HUMAN_APPROVAL_REQUIRED',
    jsonName: 'proposal.json',
    screenshotName: 'proposal.png',
    screenshotBase: 'proposal',
    api: {
      decision: 'APPROVAL_REQUIRED',
      reason: 'HUMAN_APPROVAL_REQUIRED',
      story,
      beforeAction: journey.before,
      requestedAction: journey.requested,
      actualAction: journey.before,
      mutationPerformed: false,
    },
    findingStatuses: compliance ? ['NON_COMPLIANT', 'NON_COMPLIANT'] : undefined,
  });

  await clickAndAssert(page, {
    button: 'Approve Once',
    endpoint: '/api/approve',
    badge: 'ALLOW',
    reason: 'APPROVAL_VALID',
    jsonName: 'approval-valid.json',
    screenshotName: 'approval-valid.png',
    screenshotBase: 'approval-valid',
    api: {
      decision: 'ALLOW',
      reason: 'APPROVAL_VALID',
      story,
      beforeAction: journey.before,
      requestedAction: journey.requested,
      actualAction: journey.afterApproval,
      mutationPerformed: true,
      verified: true,
      audit: 'RECORDED',
    },
    findingStatuses: compliance ? ['COMPLIANT', 'COMPLIANT'] : undefined,
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
    screenshotBase: 'bypass-denied',
    api: {
      decision: 'DENY',
      reason: 'HUMAN_APPROVAL_REQUIRED',
      story,
      beforeAction: journey.before,
      requestedAction: journey.requested,
      actualAction: journey.afterBypass,
      mutationPerformed: false,
      verified: false,
    },
    findingStatuses: compliance ? ['NON_COMPLIANT', 'NON_COMPLIANT'] : undefined,
  });

  assert.deepEqual(pageErrors, [], 'browser page errors');
  assert.deepEqual(requestFailures, [], 'browser request failures');
  assert.deepEqual(externalRequests, [], 'unexpected external requests');

  const result = {
    result: consoleErrors.length === 0 && httpErrors.length === 0
      ? 'PASS'
      : 'PASS_WITH_BROWSER_WARNINGS',
    evidenceMode: 'INTERACTIVE_PLAYWRIGHT',
    story,
    browser: await browser.version(),
    viewport: '1920x1080',
    uiActions: [journey.reviewButton, 'Approve Once', 'Reset', 'Try Approval Bypass'],
    apiAssertions: ['proposal', 'approval-valid', 'bypass-denied'],
    domAssertions: ['decision badge', 'reason code'],
    consoleErrors,
    pageErrors,
    requestFailures,
    httpErrors,
    externalRequests,
    screenshots: screenshotDetails.map((screenshot) => screenshot.name),
    screenshotDetails,
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

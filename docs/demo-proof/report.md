# AgentGuard POC test report

## Bottom line

Issue #18 replaces API-seeded rendering evidence with an interactive
Playwright Core journey. The runner clicks the real controls, asserts the
matching API and rendered decision state, captures three screenshots, records
browser hygiene, and proves cleanup.

The complete local test suite and three-state browser E2E proof pass. The
separate untrusted-agent intent boundary remains deterministic TEST-PROVEN
logic and is still not connected to the running API or GUI.

This is a synthetic POC report. It does not prove a real AWS WAF mutation.

## Current checkpoint

| Item | Value |
| --- | --- |
| Issue | [#18 - Use Playwright Core for interactive demo proof](https://github.com/mytestlab123/agentguard/issues/18) |
| Test date | 2026-08-27 |
| Browser evidence | PASS - interactive Playwright journey |
| Screenshot state | Three visually inspected 1920 x 1080 alias-only images |
| Cleanup state | Browser closed; services stopped; ports released; temporary files removed |

The current proof is local synthetic evidence. It does not make an AWS call.

## Proof status

| Capability | Status | Evidence |
| --- | --- | --- |
| Parse minimal untrusted intent | TEST-PROVEN | Focused Python tests |
| Reject authority injection and target swaps | TEST-PROVEN | Focused Python tests |
| Create a trusted immutable proposal | TEST-PROVEN | Focused Python tests |
| Accept agent intent through the local API | NOT BUILT | Outside Issue #16 scope |
| Display agent-intent validation in the GUI | NOT BUILT | Outside Issue #16 scope |
| Existing proposal, approval, and bypass flow | DEMO-PROVEN | Playwright UI actions, API and DOM assertions, screenshots |

## What was built

The new standalone boundary function converts a minimal untrusted request into
a trusted typed proposal:

```text
untrusted agent intent: target + rule + action
                     |
                     v
exact schema and trusted allowlist
                     |
                     v
trusted observed WAF state
                     |
                     v
server-created immutable proposal
                     |
                     v
deterministic policy -> human approval -> synthetic action
```

### Field ownership

| Source | Fields |
| --- | --- |
| Untrusted agent | `target`, `rule`, `action` only |
| Trusted server | proposal ID, version, expiry, config hash, lock token, before state, scope, region, policy result, and approval state |

An untrusted agent cannot mark its own request approved or supply proposal
identity, expiry, concurrency controls, current state, scope, region, or a
policy decision.

## Boundary security cases

The targeted unit suite proves these deterministic outcomes:

| Input or condition | Expected result |
| --- | --- |
| Exact allowlisted `COUNT -> BLOCK` intent | Trusted proposal created; `APPROVAL_REQUIRED` |
| Any of 10 authority fields injected | `INVALID_AGENT_INTENT` |
| Target swapped | `TARGET_NOT_ALLOWED` |
| Rule swapped | `RULE_NOT_ALLOWED` |
| Action changed | `ACTION_NOT_ALLOWED` |
| Missing, extra, empty, wrong-type, or non-object input | `INVALID_AGENT_INTENT` |
| Trusted observed action is not `COUNT` | `OBSERVED_STATE_NOT_ALLOWED` |
| Trusted observed target is not allowlisted | `TARGET_NOT_ALLOWED` |

Failures use stable reason codes and do not echo injected values.

## Testing workflow

### 1. Targeted boundary tests

```bash
PYTHONPATH=src python3 -m unittest tests.test_proposal_boundary -v
```

This directly exercises allowed proposal construction, authority injection,
target/rule/action swaps, malformed payloads, and invalid trusted observations.

### 2. Full deterministic checks

```bash
./scripts/check.sh
```

The repo-owned check runs the complete Python suite, frontend tests, and Vite
production build.

### 3. Browser end-to-end proof

```bash
./scripts/browser-e2e.sh
```

The repo-owned runner:

1. selects unused loopback ports;
2. starts the synthetic Python API and Vite frontend;
3. launches installed Chrome through pinned Playwright Core;
4. clicks Review Firewall, Approve Once, Reset, and Try Approval Bypass;
5. asserts the matching API payload and rendered decision and reason;
6. records console, page, request, HTTP, and external-network observations;
7. captures three 1920 x 1080 screenshots and confirms they are distinct;
8. closes the browser, stops its service group, removes temporary files, and
   confirms both ports were released.

This is a regression check for the existing browser workflow. Issue #16
deliberately made no API or GUI change, so the screenshots cannot show the new
intent boundary. A future separately scoped integration can add browser proof
for accepted and rejected agent intent.

Temporary browser evidence is written outside Git under
`~/.AGENTS-temp/agentguard/browser-e2e/`. The accepted sanitized screenshots
below were copied into this proof directory for an offline demo fallback.

## Results

| Check | Result |
| --- | --- |
| Targeted proposal-boundary suite | PASS - 5 tests |
| Complete Python suite | PASS - 31 tests |
| Frontend API-client suite | PASS - 3 tests |
| Vite production build | PASS |
| Proposal browser journey | PASS - `APPROVAL_REQUIRED`, no mutation |
| Valid-approval browser journey | PASS - `ALLOW`, `APPROVAL_VALID`, verified |
| Approval-bypass browser journey | PASS - `DENY`, no mutation |
| Browser actions | PASS - four real UI clicks |
| API and DOM assertions | PASS - three matching state transitions |
| Browser hygiene | PASS - zero console, page, request, HTTP, or external-network errors |
| Screenshot integrity | PASS - 3 distinct nonempty PNG files |
| E2E cleanup | PASS - browser, services, ports, and temporary files cleaned |
| Public-safety review | PASS - synthetic aliases only |

## Full screenshots of the existing browser workflow

### 1. Proposal requires human approval

![AgentGuard proposal requires human approval](proposal.png)

- Decision: `APPROVAL REQUIRED`
- Reason: `HUMAN_APPROVAL_REQUIRED`
- Requested transition: `COUNT -> BLOCK`
- Actual action: `COUNT`
- Mutation: `NO`

### 2. Exact one-time approval is valid

![AgentGuard valid approval allows and verifies the synthetic update](approval-valid.png)

- Decision: `ALLOW`
- Reason: `APPROVAL_VALID`
- Requested transition: `COUNT -> BLOCK`
- Actual action: `BLOCK`
- Mutation: `YES`
- Verified: `YES`
- Audit: `RECORDED`

The shown update is synthetic local state only.

### 3. Approval bypass is denied

![AgentGuard approval bypass attempt is denied](bypass-denied.png)

- Decision: `DENY`
- Reason: `HUMAN_APPROVAL_REQUIRED`
- Actual action: `COUNT`
- Mutation: `NO`
- Audit: `RECORDED`

## POC boundary and limitations

This checkpoint deliberately does not add:

- model or RAG integration;
- AWS WAF write calls or write IAM;
- real resource identifiers in the browser;
- API or GUI integration for accepting arbitrary agent intent;
- cloud deployment or enterprise browser infrastructure;
- browser automation beyond one pinned development-only Playwright Core package.

The intent boundary is a small, independently tested Python seam. The running
demo still creates its proposal from trusted synthetic or read-only fixtures;
it does not yet accept arbitrary agent intent. The merged intent-boundary
milestone therefore remains TEST-PROVEN rather than visible end-to-end proof.

## Reproduce the proof

From the repository root:

```bash
./scripts/check.sh
./scripts/browser-e2e.sh
```

For a manual demo using different ports:

```bash
AGENTGUARD_API_PORT=9001 AGENTGUARD_FRONTEND_PORT=5175 ./scripts/run-local.sh
```

Open `http://localhost:5175/`, select **Review Firewall**, approve the exact
proposal, reset, and select **Try Approval Bypass**. The expected states are the
three screenshots above.

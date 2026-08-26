# AgentGuard POC test report

## Bottom line

AgentGuard now has a strict trust boundary between untrusted agent intent and
the existing immutable proposal and approval flow. The agent may request only
`target`, `rule`, and `action`; all authority-bearing fields are created from
trusted server inputs. The current PR passed the complete local test suite and
the three-state browser E2E proof.

This is a synthetic POC report. It does not prove a real AWS WAF mutation.

## Current checkpoint

| Item | Value |
| --- | --- |
| Issue | [#16 - Add a strict untrusted-agent intent boundary](https://github.com/mytestlab123/agentguard/issues/16) |
| Pull request | [#17 - Add strict untrusted-agent intent boundary](https://github.com/mytestlab123/agentguard/pull/17) |
| Tested commit | `514c0e35f6be93c509318f6724e73e6ac4bf35b0` |
| Test date | 2026-08-27 |
| State | PR open; validated but not yet merged |

ChatGPT selected this bounded milestone after reviewing the repository truth in
the [next-step handoff](https://github.com/mytestlab123/agentguard/pull/15#issuecomment-5429042138).

## What changed

The new boundary converts a minimal untrusted request into a trusted typed
proposal:

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
3. drives proposal, approval, reset, and bypass API actions;
4. checks the JSON decisions with `jq` before capture;
5. captures three 1920 x 1080 Chrome screenshots;
6. confirms the PNG files are nonempty and pairwise distinct;
7. stops its process group, removes its temporary browser profile, and confirms
   both ports were released.

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
| Proposal browser state | PASS - `APPROVAL_REQUIRED`, no mutation |
| Valid approval browser state | PASS - `ALLOW`, `APPROVAL_VALID`, verified |
| Approval-bypass browser state | PASS - `DENY`, no mutation |
| Screenshot integrity | PASS - 3 distinct nonempty PNG files |
| E2E cleanup | PASS - owned ports released |
| Public-safety review | PASS - synthetic aliases only |

### Screenshot checksums

| Screenshot | SHA-256 |
| --- | --- |
| `proposal.png` | `aba9326aa482c150b3076feb39a1b3173ca07db2a53f166942cacb71f00d1038` |
| `approval-valid.png` | `c0b589555784a84191cc7ac4b3086d7100f031397d2bcde1ce3ffcba09685afd` |
| `bypass-denied.png` | `6e6bb212fa9d2923fc48ed8d479104b69f15f033b3a5df355fb5ee9f96a2d052` |

## Full screenshots

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
- new runtime dependencies.

The intent boundary is a small, independently tested Python seam. The existing
browser proof still exercises the deterministic synthetic policy flow; PR #17
does not claim a new visible GUI state.

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

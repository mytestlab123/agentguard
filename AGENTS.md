# AGENTS.md

## Purpose

AgentGuard is a personal, public learning project demonstrating why an AI
security agent can be trusted around sensitive actions.

The core rule is:

> AI may investigate and propose. Deterministic policy, human approval, and
> narrow AWS authority decide what can actually happen.

## Current POC scope

GitHub Issue #11 is the approved sanitized offline proof scope:

- keep the existing synthetic API and frontend on explicit free loopback ports;
- assert proposal, exact approval, and approval-bypass states through documented
  API routes;
- generate temporary browser evidence outside Git;
- retain only the three approved synthetic snapshots under `docs/demo-proof/`;
- clean up only the processes and temporary profile created by the runner.

This is a local POC. It must not call or mutate AWS.

## Working rules

- Follow KISS: build the smallest POC that proves one learning objective; do
  not turn AgentGuard into an enterprise platform.
- Keep each change small and tied to the active Issue acceptance criteria.
- Prefer one repo-owned script over a new framework or dependency.
- Preserve synthetic mode and mocked AWS tests.
- Prefer deterministic contracts and policy checks around probabilistic or
  external components.
- Keep real AWS identifiers server-side and out of the public repository.
- Expose only public-safe aliases such as `LAB_WAF_01` and
  `LAB_AdminPathProtection` to browser/model-visible state.
- Preserve unrelated working-tree changes.

## Hard stops

- Do not stop unrelated local listeners; use another verified free port.
- Do not commit raw screenshots, runtime logs, browser profiles, or E2E evidence.
  The only screenshot exception is visually inspected, synthetic, alias-only
  proof under `docs/demo-proof/` approved by an exact Issue.
- Do not add `wafv2:UpdateWebACL` or any other AWS mutation call unless a later
  exact mutation experiment is separately approved.
- Do not require mutation IAM permissions.
- Do not commit AWS account IDs, ARNs, WebACL IDs, credentials, tokens, `.env`
  values, private documents, internal material, or raw operational logs.
- Do not allow browser/model input to select arbitrary AWS resources.
- Do not add Bedrock/AgentCore model calls, paid services, or new cloud
  resources unless separately approved.
- Stop if an AWS error or log path could expose real identifiers publicly.

## Validation

Retain the existing policy and read-only AWS tests. For the browser runner,
prove:

1. proposal JSON is `APPROVAL_REQUIRED`, `COUNT -> BLOCK`, mutation false;
2. approved JSON is `ALLOW / APPROVAL_VALID`, actual BLOCK, mutation and
   verification true;
3. bypass JSON is `DENY / HUMAN_APPROVAL_REQUIRED`, mutation false;
4. three distinct nonempty screenshots are produced outside Git;
5. approved synthetic snapshots contain only aliases before they enter Git;
6. owned listeners and the temporary browser profile are cleaned up.

Before every public push, perform a public-safety diff review.

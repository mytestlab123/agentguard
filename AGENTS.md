# AGENTS.md

## Purpose

AgentGuard is a personal, public learning project demonstrating why an AI
security agent can be trusted around sensitive actions.

The core rule is:

> AI may investigate and propose. Deterministic policy, human approval, and
> narrow AWS authority decide what can actually happen.

## Active scope

GitHub Issue #6 is the approved next implementation scope:

- connect exactly one disposable AWS WAF WebACL through a read-only adapter;
- read and sanitize the selected rule configuration;
- confirm the intended `COUNT` state;
- produce the existing typed `COUNT -> BLOCK` proposal;
- show `LIVE AWS - READ ONLY` in the browser;
- preserve the existing deterministic approval, replay, drift, bypass, and
  audit behavior.

**Phase 2 must not mutate AWS.**

## Working rules

- Keep each change small and tied to Issue #6 acceptance criteria.
- Preserve synthetic mode and mocked AWS tests.
- Prefer deterministic contracts and policy checks around probabilistic or
  external components.
- Keep real AWS identifiers server-side and out of the public repository.
- Expose only public-safe aliases such as `LAB_WAF_01` and
  `LAB_AdminPathProtection` to browser/model-visible state.
- Preserve unrelated working-tree changes.

## Hard stops

- Do not add `wafv2:UpdateWebACL` or any other AWS mutation call in Phase 2.
- Do not require mutation IAM permissions.
- Do not commit AWS account IDs, ARNs, WebACL IDs, credentials, tokens, `.env`
  values, private documents, internal material, or raw operational logs.
- Do not allow browser/model input to select arbitrary AWS resources.
- Do not add Bedrock/AgentCore model calls, paid services, or new cloud
  resources unless separately approved.
- Stop if an AWS error or log path could expose real identifiers publicly.

## Validation

For Phase 2, retain all existing checks and add mocked tests proving:

1. a `GetWebACL` response maps to sanitized aliases;
2. the exact COUNT rule produces the existing proposal;
3. missing, ambiguous, or unexpected configuration fails closed;
4. unrelated targets cannot be selected;
5. raw AWS exceptions/identifiers are not exposed;
6. live read mode cannot call a mutation API.

Before every public push, perform a public-safety diff review.

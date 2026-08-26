# Context

Updated: 2026-08-27

## Current AgentGuard truth

- PR #5 was squash-merged into `main` at `76ac721`.
- Issue #4 is complete and closed.
- PR #7 is merged and Issue #6 is complete and closed.
- PR #9 is merged and Issue #8 is complete and closed.
- PR #12 is merged and Issue #11 is complete and closed.
- PR #14 is merged and Issue #13 is complete and closed.
- The repository now has a working local deterministic policy core, synthetic
  WAF adapter, React Decision Panel, and local-only Python API.
- Existing local behavior covers `ALLOW / DENY / APPROVAL REQUIRED`, exact
  approval, rejection, replay/drift denial, synthetic verification, audit, and
  approval-bypass denial.
- Current validation passes 26 Python tests, three frontend tests, a successful
  Vite build, and the three-state browser E2E proof.

## Phase 2 result

GitHub Issue #6 was completed in merged PR #7:

> Connect exactly one real disposable AWS WAF target through a read-only path.

- PR #7 added a narrow `GetWebACL` reader, runtime-only exact target
  configuration, alias-only output, stable safe errors, live API/UI mode,
  mocked tests, and a repo-owned live proof command.
- Canonical local validation passes 26 Python tests, three frontend tests, and
  the Vite production build.
- One explicitly approved, tagged, TTL-bound, unassociated disposable WebACL
  was created for the acceptance run. The repo-owned proof read the real COUNT
  rule and emitted aliases only.
- Browser acceptance showed `LIVE AWS - READ ONLY`, COUNT-to-BLOCK proposal,
  `APPROVAL REQUIRED`, disabled live approval, mutation NO, and bypass DENY.
- The exact disposable WebACL was deleted after evidence capture. Regional WAF
  inventory returned to zero and exact reread returned not found.
- Raw identifiers, runtime configuration, AWS responses, and screenshots remain
  outside Git under the private evidence directory.

## Current gate

No next implementation milestone is selected. The accepted current truth is
being packaged for the GitHub-only ChatGPT handoff. ChatGPT must select exactly
one bounded next learning objective before Codex creates or implements another
feature, unless Amit explicitly overrides that gate.

No Phase 3 mutation work, IAM widening, model service, deployment, or new AWS
resource is approved.

## Phase 2 boundary

Allowed:

- AWS WAF read-only access needed for the exact configured lab WebACL;
- mocked AWS clients in tests;
- runtime-only mapping from real identifiers to safe aliases;
- current synthetic mode and local policy/API/frontend behavior.

Not allowed in Phase 2:

- `UpdateWebACL` or any other AWS mutation;
- mutation IAM permissions;
- arbitrary AWS resource selection from browser/model input;
- committing real AWS account IDs, ARNs, WebACL IDs, credentials, tokens, or
  raw operational data;
- Bedrock/AgentCore model integration;
- new paid/cloud architecture unrelated to the one read-only WAF proof.

## Later phases

A later separately approved Issue may consider the first real guarded WAF
mutation using exact proposal validation, one-time human approval, AWS
LockToken, narrow IAM, reread, and Before -> Action -> After verification.

RAG/memory poisoning remains a future AgentGuard regression scenario, not an
active standalone implementation track.

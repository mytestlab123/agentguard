# Context

Updated: 2026-08-26

## Current AgentGuard truth

- PR #5 was squash-merged into `main` at `76ac721`.
- Issue #4 is complete and closed.
- The repository now has a working local deterministic policy core, synthetic
  WAF adapter, React Decision Panel, and local-only Python API.
- Existing local behavior covers `ALLOW / DENY / APPROVAL REQUIRED`, exact
  approval, rejection, replay/drift denial, synthetic verification, audit, and
  approval-bypass denial.
- Validation reported after the merge: 17 Python tests, 3 frontend tests, and
  a successful Vite build.

## Active next scope

GitHub Issue #6 is the next implementation gate:

> Connect exactly one real disposable AWS WAF target through a read-only path.

The browser should show `LIVE AWS - READ ONLY`, read the configured WebACL,
sanitize it to public-safe aliases, confirm the selected rule is in `COUNT`,
and feed that evidence into the existing typed `COUNT -> BLOCK` proposal and
deterministic policy flow.

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

Only after Issue #6 is complete and reviewed should AgentGuard consider the
first real guarded WAF mutation using exact proposal validation, one-time human
approval, AWS LockToken, narrow IAM, reread, and Before -> Action -> After
verification.

RAG/memory poisoning remains a future AgentGuard regression scenario, not an
active standalone implementation track.

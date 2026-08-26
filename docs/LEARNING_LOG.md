# Learning Log

## 2026-08-20 - Phase 0 bootstrap

- Objective: define a safe, local-only learning boundary for RAG, memory, and
  privacy experiments.
- Built: minimal documentation and empty locations for synthetic data, source,
  and tests.
- Evidence: repository bootstrap files only; no runtime behavior exists yet.
- Limits: no ingestion, retrieval, model call, cloud access, or test suite.
- Next: choose one synthetic, deterministic learning experiment only after the
  secure-agent harness learning gate.

## 2026-08-26 - AgentGuard v1 deterministic policy core

- Objective: prove the approval boundary from issue #4 without a model or AWS.
- Built: immutable proposal hashing, exact target/action policy, expiring
  one-time approval, synthetic lock-token drift checks, guarded COUNT-to-BLOCK
  execution, verification, audit events, and a repo-owned check script.
- Evidence: `./scripts/check.sh` passes 10 deterministic tests; the demo emits
  READ/ALLOW, mutation/APPROVAL_REQUIRED, approved/verified, and bypass/DENY.
- Security failures retained: target/action substitution, malformed runtime
  values, approval mismatch, expiry, replay, missing approval, and drift.
- Limits: synthetic local state only; no React integration, model, AWS adapter,
  IAM, deployment, real WebACL mutation, or billable call.
- Next: reuse the AWS WAF Analyst React shell for a synthetic Decision Panel.

## 2026-08-26 - Synthetic React Decision Panel

- Objective: make the issue #4 approval boundary understandable in a browser
  before adding any model or AWS integration.
- Built: a React/Vite shell derived from the AWS WAF Analyst frontend, a
  manager-facing Decision Panel, visible synthetic tool activity, Approve Once
  and Reject paths, Before/Requested/Actual state, verification, and audit.
- Evidence: four Node state-machine tests pass and the Vite production build
  succeeds; the canonical `./scripts/check.sh` runs Python and frontend checks.
- Security failures retained: UI approval replay is inert, Reject leaves COUNT
  unchanged, and the bypass request returns HUMAN_APPROVAL_REQUIRED with no
  mutation.
- Limits: UI state is currently local JavaScript; it is not yet connected to
  the Python policy core, a model, AgentCore, Cognito, or AWS.
- Next: connect the browser state to the Python policy contracts through one
  small local-only API boundary.

## 2026-08-26 - Python-authoritative local browser API

- Objective: remove the browser-local authorization simulation and connect the
  Decision Panel to the deterministic Python policy core.
- Built: thread-safe synthetic demo controller, five fixed action routes,
  sanitized state route, bounded empty-JSON parsing, generic errors, local-only
  binding, human-UI intent/CSRF gate, and one repo-owned local runner.
- Evidence: `./scripts/check.sh` passes 17 Python tests and three frontend
  client tests, then completes the Vite production build.
- Security failures retained: approval without proposal, direct approval
  replay, reject/bypass no-mutation, unexpected fields, missing human-UI
  intent, unknown browser actions, and failed API responses.
- Consolidation: removed the duplicate JavaScript authorization reducer/tests
  after equivalent controller and HTTP regression cases moved to the Python
  authority; frontend tests now cover only fixed API client behavior.
- Limits: the static intent header is local CSRF resistance, not human identity
  or production authentication. No model, AgentCore, Cognito, AWS adapter, IAM,
  real WebACL, credential, or billable call is connected.
- Next: run a local browser review and fix only visible v1 UX issues before any
  separately approved AWS experiment.

## 2026-08-26 - Collision-free local API startup

- Objective: make the local runner coexist with an existing listener instead
  of assuming one fixed API port.
- Built: operating-system-assigned API port, bounded ready-file handoff,
  readiness validation, Vite proxy propagation, optional explicit port, and
  exact temporary-file/API-process cleanup.
- Evidence: parser checks, full test/build suite, and a bounded runner startup
  confirm the selected API port reaches the health endpoint.
- Limits: an explicitly requested occupied port still fails rather than
  stopping or replacing the existing listener.

## 2026-08-26 - Local browser acceptance complete

- Objective: visually verify the three manager-facing decision outcomes before
  any commit or AWS work.
- Evidence: approved execution shows ALLOW/APPROVAL_VALID with COUNT-to-BLOCK,
  verified mutation and recorded audit; Reject shows DENY/HUMAN_REJECTED with
  COUNT retained; bypass shows DENY/HUMAN_APPROVAL_REQUIRED with COUNT retained.
- No-go proof: Reject and bypass both show mutation NO and verification NO;
  blocked timeline stages are visually distinct and audit remains recorded.
- Public-safety handling: temporary headless-browser screenshots and profile
  data stayed outside the repository and were removed after inspection.
- Limits: all state is synthetic and local; no model, AWS API, credential,
  cloud resource, or billable action was used.
- Next: final public-safety diff review, then a focused commit only with owner
  approval.

## 2026-08-27 - Repo-owned browser E2E runner

- Objective: replace manual local startup, API state setup, and screenshot
  capture with one repeatable agent-run command.
- Built: explicit free-port selection, bounded readiness, proposal and bypass
  JSON assertions, two headless-Chrome screenshots, and exact owned-process and
  temporary-profile cleanup.
- KISS choice: reused Bash, curl, jq, Vite, and installed Chrome instead of
  adding a browser-testing framework or application dependency.
- Safety: synthetic mode only, loopback listeners only, evidence outside Git,
  no AWS call, and no stopping unrelated local applications.

## 2026-08-27 - Sanitized offline demo proof

- Objective: keep the trust-boundary demo showable when the live app cannot run.
- Built: one additional approved-state assertion and screenshot in the existing
  browser runner, plus a three-state Markdown proof under `docs/demo-proof/`.
- Evidence: proposal requires approval, exact approval produces
  `ALLOW / APPROVAL_VALID` with verified synthetic BLOCK, and bypass is denied
  with COUNT retained.
- Safety: only visually inspected synthetic alias-only PNGs enter Git; raw JSON,
  logs, profiles, real identifiers, and AWS mutation remain excluded.

## 2026-08-27 - Untrusted agent-intent proposal boundary

- Objective: make the trust transition before proposal creation explicit
  without adding a model or AWS call.
- Built: an exact three-field intent parser and trusted proposal builder using
  allowlisted observed state plus server-owned metadata.
- Security regressions: authority-field injection, malformed schemas,
  target/rule/action swaps, and invalid observed state fail closed with stable
  reasons that do not echo payload values.
- Evidence: five focused boundary tests pass; the generated proposal still
  evaluates to `APPROVAL_REQUIRED / HUMAN_APPROVAL_REQUIRED`.
- Limits: no API/GUI integration, model, AWS mutation, IAM, RAG, dependency, or
  generalized target selection.

## 2026-08-27 - Interactive Playwright demo proof

- Objective: replace API-seeded rendering screenshots with a repeatable browser
  journey that uses the same controls as the manager demo.
- Built: one pinned Playwright Core development dependency, a repo-owned browser
  script, four real UI actions, matching API and DOM assertions, browser-error
  capture, three fixed-size screenshots, and exact cleanup evidence.
- Boundary lesson: Windows Node completed reliably when the repo-pinned
  Playwright package and runner were staged together in one unique Windows
  temporary directory; importing the package across the UNC boundary left the
  WSL interop proxy waiting after the Windows process had exited.
- Evidence: proposal, valid approval, reset, and bypass actions pass with zero
  console, page, request, HTTP, or external-network errors; all three 1920 x
  1080 screenshots were visually inspected and contain aliases only.
- Safety: synthetic mode and loopback listeners only; no AWS call, model,
  credential, real identifier, or mutation authority was introduced.

## 2026-08-26 - Phase 2 read-only WAF boundary

- Objective: replace only the synthetic read evidence with one exact real AWS
  WAF read while preserving the existing deterministic proposal boundary.
- Built: runtime-only exact target configuration, a `GetWebACL`-only adapter,
  alias-only rule state, stable sanitized errors, live read-only API/UI mode,
  disabled live approval, mocked regression tests, and a repo-owned live proof.
- Safety evidence: the reader has no mutation method; browser actions contain
  no resource selector; synthetic mode remains the test default.
- Local validation: 26 Python tests, three frontend tests, Bash parser checks,
  and the Vite production build pass without AWS access.
- Live evidence: after exact approval, one tagged, TTL-bound, unassociated
  disposable WebACL with one COUNT rule was read through the repo-owned proof.
  Output contained only `LAB_WAF_01`, `LAB_AdminPathProtection`, COUNT, BLOCK,
  the deterministic decision, and no raw AWS identifiers.
- Browser evidence: live review showed `LIVE AWS - READ ONLY`, APPROVAL REQUIRED,
  disabled approval, and mutation NO; bypass showed DENY,
  HUMAN_APPROVAL_REQUIRED, and mutation NO.
- Cleanup: the exact disposable WebACL was deleted after capture; Regional WAF
  inventory returned to zero and exact reread returned not found. No AWS
  resource or write authority remains.
- Limits: Phase 3 mutation, LockToken execution, write IAM, model integration,
  deployment, and multi-target support remain unapproved.

## 2026-08-27 - Two-control Compliance Guard demo

- Objective: prove the AgentGuard approval pattern for one synthetic S3 bucket
  and exactly two compliance controls.
- Built: server-owned TLS-only and public-read control mappings, one immutable
  two-control proposal, one-time approval, local modeled remediations, rescan,
  verification, audit, and approval-bypass denial.
- Evidence: 37 Python tests, three frontend tests, a Vite production build,
  and both Compliance Guard and original WAF Playwright journeys pass.
- Browser proof: proposal shows two `NON_COMPLIANT` findings and no mutation;
  valid approval verifies two `COMPLIANT` results; bypass is denied with both
  findings unchanged. Browser and network error counts are zero and cleanup is
  complete.
- Management artifact: `docs/demo-compliance.md` tells the nine-slide
  Compliance Guard story with three visually inspected synthetic screenshots.
- Safety: the browser supplies no bucket, control, runbook, parameter, or
  approval identity. No AWS call, S3 write, Config evaluation, SSM execution,
  IAM change, model call, or dependency was added.
- Limits: real AWS compliance reads, real remediation, multi-account scale,
  and the wider S3 control catalogue remain not proven and deferred.

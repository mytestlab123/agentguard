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
- AWS discovery: the approved account currently has no Regional WebACL in the
  selected region and no CloudFront WebACL, so no live target was read and no
  resource was created.
- Decision: stop at the resource-creation approval gate. A disposable WebACL
  requires separate exact approval, tags, TTL, and cleanup ownership.

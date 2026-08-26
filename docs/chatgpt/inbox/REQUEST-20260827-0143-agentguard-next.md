# AgentGuard: choose the next bounded milestone

## Protocol

First read the generic all-repository collaboration protocol:

<https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

Then read the AgentGuard-specific protocol at the accepted current commit:

<https://github.com/mytestlab123/agentguard/blob/c4557c4d7706289a7e86fa6b04b3df4a4e48a998/docs/chatgpt/GITHUB_ONLY_COLLABORATION_PROTOCOL.md>

## Exact question

**Review the current AgentGuard repository truth and tell us what we should do
next. Choose exactly one small, bounded learning objective. Check existing open
Issues first. Return one Issue and one implementation PR plan. Do not implement
anything.**

## Accepted current truth

Repository: <https://github.com/mytestlab123/agentguard>

Accepted commit:
`c4557c4d7706289a7e86fa6b04b3df4a4e48a998`

Latest completed protocol milestone:

- merged PR #14: <https://github.com/mytestlab123/agentguard/pull/14>
- closed Issue #13: <https://github.com/mytestlab123/agentguard/issues/13>

Latest completed implementation milestone:

- merged PR #12: <https://github.com/mytestlab123/agentguard/pull/12>
- closed Issue #11: <https://github.com/mytestlab123/agentguard/issues/11>
- accepted offline proof:
  <https://github.com/mytestlab123/agentguard/blob/c4557c4d7706289a7e86fa6b04b3df4a4e48a998/docs/demo-proof/output.md>

AgentGuard currently proves:

- deterministic Python policy authority behind a local-only API;
- React manager Decision Panel;
- `ALLOW`, `DENY`, and `APPROVAL REQUIRED` decisions;
- immutable typed `COUNT -> BLOCK` proposals;
- exact one-time approval, rejection, expiry, replay, and drift controls;
- approval-bypass denial;
- synthetic mutation verification and audit state;
- one narrow real AWS WAF `GetWebACL` read-only adapter with alias-only output;
- one repo-owned browser E2E command for proposal, exact approval, and bypass;
- three sanitized GitHub-renderable synthetic proof screenshots.

Accepted validation for the implementation milestone:

- 26 Python tests passed;
- three frontend tests passed;
- Vite production build passed;
- browser E2E JSON assertions and three distinct screenshots passed;
- screenshots were visually inspected and public-safety scanned;
- temporary E2E listeners and browser profile were cleaned up.

The disposable WAF used for the earlier read-only experiment was deleted. No
lab AWS resource or write authority remains.

## Open backlog and duplicate check

The only open Issues are older broad learning tracks:

- #1: minimal local RAG with synthetic cyber documents;
- #2: privacy-preserving resource tokenisation;
- #3: retrieval and memory poisoning defenses.

Do not create a duplicate. The existence of a broad backlog Issue does not make
it the automatic next milestone. Recommend reusing one only if its exact scope
is now the best small next step; otherwise explain why the recommendation is
non-duplicative.

## KISS constraints

The next milestone must:

- prove one learning objective;
- remain a personal POC, not an enterprise platform;
- normally touch only a few implementation files plus focused tests/docs;
- preserve deterministic fail-closed policy and current security regressions;
- use synthetic fixtures and public-safe aliases;
- reuse existing code, dependencies, and automation where practical;
- produce the smallest meaningful deterministic demo proof.

Do not recommend another protocol rewrite, evidence-packaging task, or GUI
redesign; those checkpoints are complete.

## Hard no-go gates

Do not propose:

- AWS mutation, write IAM, or creation of a cloud resource;
- a model call, hosted API, paid service, or deployment;
- production authentication or arbitrary runtime target selection;
- a new browser-testing framework or enterprise evidence platform;
- real AWS identifiers, credentials, private data, or raw runtime evidence in
  the public repository;
- a broad refactor or multiple parallel milestones.

## Required response

Return concise Markdown with:

1. `Recommendation` - exactly one next objective and why it follows now.
2. `Alternatives rejected` - at most two, including the backlog check.
3. `Issue` - exact ready-to-use title and body with acceptance and no-go gates.
4. `PR plan` - exact title, expected files, implementation steps, and non-goals.
5. `Risk and safety` - public-repo and trust-boundary checks.
6. `Validation and demo` - the smallest deterministic proof.
7. `Deferred` - everything that remains outside the PR.

Reply on the GitHub handoff PR containing this packet. Do not create or modify
GitHub records; Codex will validate the selection before implementation.

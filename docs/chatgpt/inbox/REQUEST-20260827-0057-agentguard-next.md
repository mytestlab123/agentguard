# AgentGuard next bounded learning POC

## Request

Recommend exactly one small, bounded next Issue and implementation PR for
AgentGuard after the completed browser E2E milestone.

Repository: <https://github.com/mytestlab123/agentguard>

Latest completed milestone:

- merged PR #9: <https://github.com/mytestlab123/agentguard/pull/9>
- closed Issue #8: <https://github.com/mytestlab123/agentguard/issues/8>

Prior completed AWS read-only milestone:

- merged PR #7: <https://github.com/mytestlab123/agentguard/pull/7>
- closed Issue #6: <https://github.com/mytestlab123/agentguard/issues/6>

## Verified current truth

AgentGuard is a public personal-learning POC. It currently has:

- a deterministic Python policy authority and local-only API;
- a React manager-facing Decision Panel;
- `ALLOW`, `DENY`, and `APPROVAL REQUIRED` decisions;
- immutable typed `COUNT -> BLOCK` proposals;
- approval, rejection, replay/drift denial, verification, and audit behavior;
- approval-bypass denial;
- a narrow real AWS WAF `GetWebACL` read-only adapter with alias-only output;
- a repo-owned synthetic browser E2E runner that asserts JSON, captures the
  proposal and bypass-denial screenshots outside Git, and releases its ports.

The latest accepted validation is 26 Python tests, three frontend tests, a
Vite production build, and the browser E2E pass. The disposable AWS WAF used
for the prior read-only proof was deleted; no lab AWS resource remains.

## Existing backlog to avoid duplicating

These older open Issues are intentionally broad and are not the active scope:

- #1: minimal local RAG with synthetic cyber documents;
- #2: privacy-preserving resource tokenisation;
- #3: retrieval and memory poisoning defenses.

Do not create a duplicate of them or revive the broad RAG track by default.
If one contains the best idea, carve out a clearly non-duplicative prerequisite
or recommend using the existing Issue instead of inventing a new record.

## KISS constraints

The recommendation must:

- prove one learning objective;
- be useful as a small POC, not an enterprise platform;
- normally touch one to three implementation files plus focused tests/docs;
- remain deterministic, local, and synthetic by default;
- keep screenshots, runtime evidence, and browser profiles outside Git;
- use only public-safe aliases and fixtures;
- preserve the current fail-closed approval boundary and security regressions;
- reuse existing dependencies and repo-owned automation where practical.

## Hard no-go gates

Do not propose:

- AWS mutation, write IAM, or creation of any cloud resource;
- a model call, hosted API, paid service, deployment, or authentication system;
- a new browser-testing framework or enterprise test platform;
- arbitrary user-selected runtime targets;
- real account IDs, ARNs, resource IDs, hostnames, credentials, or private
  operational data in Git;
- a GUI redesign or broad refactor.

## Required response

Return concise Markdown with these sections:

1. `Recommendation` - one next learning objective and why it follows PR #9.
2. `Alternatives rejected` - at most two, including duplicate/backlog checks.
3. `Issue` - exact title and ready-to-paste body with scope, acceptance, and
   no-go gates.
4. `PR plan` - exact title, expected files, implementation outline, and
   explicit non-goals.
5. `Risk and safety` - public-repo and trust-boundary checks.
6. `Validation and demo` - the smallest deterministic proof.
7. `Deferred` - what must remain outside this PR.
8. `Model and usage note` - identify the ChatGPT mode used and any visible
   usage information, without inventing billing or token facts.

Do not modify GitHub. Codex will validate the recommendation against current
repository truth before creating at most one Issue and one PR.

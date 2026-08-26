# GitHub-only Codex ↔ ChatGPT Collaboration Protocol

## Purpose

Use GitHub as the durable handoff layer between Codex, ChatGPT, and the human
owner while keeping each AgentGuard learning milestone small, reviewable, and
safe.

This file specializes the generic all-repository protocol published at:

<https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

The Gist remains repository-neutral. This file is the AgentGuard-specific
policy. Every AgentGuard handoff must share both the Gist and the immutable
repo-specific packet, Issue, or PR URL.

The most important rule is:

> **After a completed milestone, Codex must ask ChatGPT what AgentGuard should do next before creating or implementing the next feature.**

ChatGPT is the next-step reviewer. Codex is the implementation worker. The
human owner may override either role at any time.

---

## Roles

### Codex

Codex may:

- inspect the repository;
- implement an already-approved Issue;
- run tests and validation;
- prepare a PR;
- package immutable current-repository truth for ChatGPT;
- create the next Issue/PR only after ChatGPT has returned the bounded recommendation, unless the owner directly instructed Codex otherwise.

Codex must **not** silently choose a different next feature after asking ChatGPT
for the next milestone.

### ChatGPT

ChatGPT should:

- review the immutable request packet and current GitHub state;
- check completed milestones and open backlog Issues;
- identify gaps, duplicates, and scope creep;
- choose exactly one bounded next learning objective by default;
- return one ready-to-use Issue and one PR plan;
- keep the recommendation KISS and consistent with the project's safety gates.

ChatGPT may recommend using an existing Issue instead of creating a duplicate.

### Human owner

The owner may:

- change priorities;
- reject or modify ChatGPT's recommendation;
- explicitly authorize a different next milestone;
- approve any action that crosses a project hard stop.

Owner instruction always wins.

---

## Required handoff point

A ChatGPT next-step review is required when the active bounded milestone is:

1. implemented;
2. validated;
3. merged or otherwise accepted by the owner;
4. documented with enough immutable GitHub evidence to reconstruct current truth.

At that point, Codex should stop feature selection and prepare a ChatGPT request
packet.

Do not automatically continue into the next backlog item.

---

## Immutable request packet

The request should be committed to a stable GitHub path such as:

```text
docs/chatgpt/inbox/REQUEST-<timestamp>-<topic>.md
```

Prefer linking to an immutable commit SHA, merged PR, or closed Issue rather than
only a moving branch.

The packet should contain only the facts ChatGPT needs to choose the next step:

- the generic protocol Gist URL;
- repository and current commit/merged milestone;
- what is already working;
- validation evidence;
- current architecture/trust boundary;
- completed Issues/PRs relevant to the decision;
- open backlog Issues that must be checked for duplication;
- explicit KISS constraints;
- explicit hard no-go gates;
- the exact requested output.

Do not include secrets, private operational data, credentials, real AWS
identifiers, or unnecessary runtime logs.

---

## Exact question Codex should ask ChatGPT

Use wording equivalent to:

> **Review the current AgentGuard repository truth and tell us what we should do next. Choose exactly one small, bounded learning objective. Check existing open Issues first so you do not create a duplicate. Return one Issue and one implementation PR plan. Do not implement anything.**

If the owner has provided extra constraints, include them verbatim.

The phrase **"what should we do next?"** is intentional. The purpose of the
handoff is not merely to ask ChatGPT to review a Codex-selected plan; it is to
ask ChatGPT to select the next bounded milestone from the verified repository
state.

---

## Required ChatGPT response

By default, ChatGPT should return:

1. **Recommendation** — one next learning objective and why it follows the last completed milestone.
2. **Alternatives rejected** — at most two, including duplicate/backlog checks.
3. **Issue** — exact title and ready-to-paste body with scope, acceptance criteria, and no-go gates.
4. **PR plan** — exact title, expected files, implementation outline, and explicit non-goals.
5. **Risk and safety** — public-repo and trust-boundary checks.
6. **Validation and demo** — the smallest deterministic proof.
7. **Deferred** — what must remain outside the PR.

One Issue + one PR is the default ceiling, not the minimum. If an existing Issue
already exactly owns the work, ChatGPT should say to use it instead of creating
a duplicate.

---

## What Codex does after ChatGPT responds

Codex should:

1. compare the recommendation against the latest repository truth;
2. stop and report if the recommendation is stale or conflicts with a hard gate;
3. otherwise create at most the recommended one Issue and one implementation PR;
4. implement only the approved bounded scope;
5. validate and report results;
6. after completion, start a fresh ChatGPT next-step handoff.

Codex must not:

- substitute another self-selected feature;
- expand one recommendation into several Issues/PRs;
- revive a broad backlog track unless ChatGPT or the owner selected it;
- cross AWS mutation, write-IAM, model-service, deployment, secret-handling, or
  other explicit project gates without separate owner approval.

---

## Backlog and duplicate check

Before recommending a new Issue, ChatGPT must inspect relevant open Issues.

For AgentGuard, older broad learning tracks may remain intentionally open. A
new recommendation should either:

- be clearly non-duplicative and explain why; or
- reuse the existing Issue rather than creating another record.

The presence of an open backlog Issue does **not** automatically make it the
next milestone.

---

## KISS rule

The default next milestone should:

- prove one learning objective;
- fit a small personal POC;
- reuse existing code and tooling;
- normally touch only a few implementation files plus focused tests/docs;
- preserve deterministic/fail-closed controls;
- avoid framework or architecture expansion unless the learning objective
  cannot be proved without it.

Do not turn the handoff process into a project-management framework.

---

## Safety rule

A ChatGPT recommendation cannot implicitly authorize a hard-stop action.
Separate explicit owner approval remains required for any gated action defined
by the repository, including cloud mutation or write-authority expansion.

Public-repository safety remains mandatory throughout the handoff.

---

## Copy/paste handoff template

```text
ChatGPT review requested.

First read the generic collaboration protocol:
https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238

Then read the immutable AgentGuard request packet:
<IMMUTABLE_GITHUB_URL>

Then review the current repository, relevant merged PRs/closed Issues, and open
backlog Issues.

Question: What should AgentGuard do next?

Choose exactly ONE small, bounded learning objective. Check for duplicate open
Issues before proposing a new one. Return one ready-to-use Issue and one
implementation PR plan. Keep it KISS and within the hard no-go gates in the
request packet.

Do not implement anything. Codex will validate your recommendation against the
latest repository truth before creating at most one Issue and one PR.
```

---

## End-of-milestone loop

```text
IMPLEMENT
   ↓
VALIDATE
   ↓
MERGE / ACCEPT
   ↓
PACKAGE IMMUTABLE CURRENT TRUTH
   ↓
ASK CHATGPT: "WHAT SHOULD WE DO NEXT?"
   ↓
CHATGPT SELECTS ONE BOUNDED MILESTONE
   ↓
OWNER / CODEX VALIDATE
   ↓
CREATE + IMPLEMENT ONE ISSUE / PR
   ↓
REPEAT
```

This loop is the intended GitHub-only collaboration model for AgentGuard.

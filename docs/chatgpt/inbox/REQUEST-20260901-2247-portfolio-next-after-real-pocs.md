# Request: choose the next milestone after three real POC checkpoints

## Review request

Review the current repository truth and tell us what this three-POC portfolio
should do next. Choose exactly one small, bounded objective. Check the existing
open Issues and PRs first. Return one Issue and one implementation PR plan. Do
not implement anything.

Publish the completed response as one new standalone Issue in
`mytestlab123/agentguard`. Do not place the final response only in this PR, an
existing Issue, or a comment.

Generic collaboration protocol:

- <https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

## Portfolio objective

The portfolio demonstrates a reusable governed-agent operating model:

```text
Find -> Explain -> Recommend -> Human approval or denial -> Act -> Verify
```

The management question is whether agentic AI can reduce security, compliance,
and operational effort without giving probabilistic models uncontrolled cloud
authority. The next milestone should improve the strongest remaining proof gap,
not maximize the number of features.

## Current verified truth

### 1. AgentGuard / Compliance Copilot

Repository: <https://github.com/mytestlab123/agentguard>

Immutable source snapshot:
<https://github.com/mytestlab123/agentguard/blob/7b7b0f77cbcf3c5d893fff08f29b7bf7ce21ed26/README.md>

Proven:

- deterministic proposal and policy decisions;
- human approval, approval-bypass denial, replay/drift protection, verification,
  and audit in the local synthetic WAF journey;
- exact real AWS WAF `GetWebACL` read through a server-side alias boundary;
- visible live read-only mode with mutation disabled;
- synthetic two-control S3 Compliance Guard management story and presentation.

Not yet proven:

- a real AWS compliance remediation owned by AgentGuard;
- multi-account operation or production readiness.

Latest completed portfolio-direction record:

- PR #28: <https://github.com/mytestlab123/agentguard/pull/28>
- Issue #29: <https://github.com/mytestlab123/agentguard/issues/29>

Issue #29 selected SecCop real-AWS proof first. That recommendation is now
achieved and the Issue is being closed as completed.

### 2. SecCop / Security Copilot

Repository:
<https://github.com/mytestlab123/agentic-ai-cybersecurity-lab>

Immutable source snapshot:
<https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/blob/f454a5df5b5f4e48254ff82828b121ec3f049b40/README.md>

Proven:

- one real EC2 Inspector finding, exact package proposal, Approve Once,
  allow-listed SSM update, immediate package verification, truthful
  `PENDING_RESCAN`, and verified cleanup;
- one real S3 Block Public Access finding, Approve Once, exact bucket-level
  remediation, verification, and targetless persistent reopen;
- one real ECR image journey where AWS ECR stores the image, local Trivy finds
  the vulnerability, Approve Once promotes only the clean digest, Trivy
  verifies it, and targetless persistent reopen restores the finding;
- aliases remain browser-visible while AWS identifiers and raw evidence remain
  private.

Evidence records:

- EC2 operator MVP PR #42:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/42>
- S3 remediation PR #48:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/48>
- persistent S3 reopen PR #50:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/50>
- ECR operator MVP PR #52:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/52>

Current retained demo state is intentionally small: three empty private S3
buckets and one tiny ECR repository. Their deletion requires separate human
approval. No EC2 target remains from the completed EC2 proof.

### 3. AgentCore / governed AI platform learning

Repository: <https://github.com/mytestlab123/AgentCore>

Immutable proof snapshot:
<https://github.com/mytestlab123/AgentCore/blob/722ed8c53e6c496e36cba3b1f43c4b525306fda0/docs/HARNESS_MVP_PROOF.md>

Proven:

- governed model comparison using the same sanitized evidence;
- one deterministic AgentCore Harness `create -> invoke -> cleanup` command;
- fixed model configuration, no tools or memory, identity mismatch denial,
  live invocation proof, and independent Harness/IAM-role deletion checks.

Evidence records:

- governed model comparison PR #16:
  <https://github.com/mytestlab123/AgentCore/pull/16>
- Harness lifecycle PR #18:
  <https://github.com/mytestlab123/AgentCore/pull/18>
- linked Harness Issue #17:
  <https://github.com/mytestlab123/AgentCore/issues/17>

Not yet proven:

- a narrow real security/compliance tool called through AgentCore;
- persistent runtime, Gateway, Policy, Identity, or observability integration;
- production readiness.

## Existing records that must not be duplicated blindly

AgentGuard currently has future backlog Issues #1-#3 for RAG, tokenisation, and
memory-poisoning defenses. They are not automatically the next milestone.

SecCop has older open Issues #3, #5, #8, #14, #16, and #31 plus draft PR #15.
Some may now be stale or partly superseded by the completed real operator
journeys. Do not choose one without checking its current relevance.

AgentCore has older open Issues #3 and #8. The newer Harness Issue #17 and PR
#18 already completed the bounded Harness lifecycle, so do not duplicate that
work.

## Constraints for the next milestone

- Follow KISS: one problem, one happy path, one command, one proof, one result.
- Default implementation budget: at most three product files and 200 net new
  non-generated lines; normal same-path variance must be explained.
- Reuse an existing implementation path. No new framework, shared portal,
  vector database, orchestration layer, or broad abstraction unless the exact
  objective cannot be proved without it.
- AI may investigate and propose. Deterministic policy, exact target binding,
  human approval, and narrow AWS authority decide whether mutation occurs.
- Keep browser/model-visible evidence alias-only and public-safe.
- Do not authorize AWS, IAM, networking, paid service, cleanup, or production
  mutation through this review request.
- Prefer a low-cost personal non-production proof with explicit lifecycle and
  cleanup/retention behavior when AWS is necessary.
- Do not expand to multi-account or enterprise architecture yet.
- Management value matters: state the problem, beneficiary, outcome, rough
  effort, cost drivers, and what the milestone still does not prove.

## Questions to answer

1. What is the single highest-value remaining proof gap across the three POCs?
2. Which one repository should own the next bounded milestone, and why?
3. What exactly should the operator see from finding through verified outcome?
4. What should explicitly remain deferred?

## Required response format

Create one new standalone AgentGuard Issue containing:

1. a short recommendation and why it is next;
2. alternatives considered and rejected;
3. one bounded Issue title and acceptance scope;
4. one implementation PR title;
5. expected files or existing implementation path to reuse;
6. explicit non-goals and hard safety gates;
7. validation and evidence plan;
8. rough effort and cloud/model cost drivers;
9. operator journey and management outcome;
10. deferred work and a clear terminal stop condition.

Do not implement the recommendation. Codex will validate the new Issue against
current repository truth and wait for Amit's separate approval.

## Publication-safety statement

This packet contains only public repository links, aliases, bounded capability
claims, and summarized validation. It excludes credentials, account IDs, ARNs,
resource IDs, repository URIs, image digests, bucket names, hostnames, IP
addresses, private logs, raw AWS responses, and customer or employer material.

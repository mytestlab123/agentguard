# AgentGuard: choose one bounded Compliance Guard Demo 2 milestone

## Protocol

First read the generic all-repository collaboration protocol:

<https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

Then read the AgentGuard-specific protocol at the accepted current commit:

<https://github.com/mytestlab123/agentguard/blob/fdd264bd4a6be9bde0c79693ebd62fff41a90348/docs/chatgpt/GITHUB_ONLY_COLLABORATION_PROTOCOL.md>

## Exact question

**Review the current AgentGuard repository truth and tell us what we should do
next within the owner-selected Compliance Guard direction. Choose exactly one
small, bounded learning objective. Check existing open Issues first. Return one
ready-to-use Issue and one implementation PR plan. Do not implement anything.**

## Owner-selected direction

Keep the repository and trust-boundary engine named **AgentGuard**. The next
management story should be **Compliance Guard - powered by AgentGuard** and use
this required deck path:

```text
docs/demo-compliance.md
```

The direction is a public-safe, synthetic S3 compliance story:

```text
scan -> find -> recommend -> approve -> remediate -> rescan -> verify
```

The long-term motivation is recurring compliance across many AWS accounts and
rules. The next milestone must remain one small local POC, not a multi-account
platform.

ChatGPT should select the smallest exact objective inside this direction. It
must decide whether the next PR can honestly produce DEMO-PROVEN visible
evidence or whether the first deck must label parts as PLANNED or TEST-PROVEN.

## Accepted current AgentGuard truth

Repository: <https://github.com/mytestlab123/agentguard>

Accepted commit:
`fdd264bd4a6be9bde0c79693ebd62fff41a90348`

Latest completed milestone:

- merged PR #19:
  <https://github.com/mytestlab123/agentguard/pull/19>
- closed Issue #18:
  <https://github.com/mytestlab123/agentguard/issues/18>
- current management deck:
  <https://github.com/mytestlab123/agentguard/blob/fdd264bd4a6be9bde0c79693ebd62fff41a90348/docs/demo.md>

AgentGuard currently proves:

- deterministic Python policy authority behind a local-only API;
- immutable typed WAF proposals and exact one-time human approval;
- rejection, expiry, replay, drift, and approval-bypass denial;
- a strict test-proven boundary from minimal untrusted intent to a
  server-created trusted proposal;
- one earlier real AWS WAF read-only experiment with alias-only output and
  complete resource cleanup;
- a React manager Decision Panel;
- a repo-owned Playwright Core journey that clicks the real UI and asserts API
  and DOM state;
- three visually inspected synthetic screenshots for proposal, valid approval,
  and bypass denial.

Accepted validation:

- 31 Python tests passed;
- three frontend tests passed;
- Vite production build passed;
- Playwright performed four real UI actions and three API/DOM assertion sets;
- browser console, page, request, HTTP, and external-network errors were zero;
- browser, services, ports, and temporary files were cleaned;
- dependency audit and public-safety review passed.

No AWS resource, runtime identifier, mutation permission, or write authority
remains from earlier experiments.

## Relevant public SecCop milestone

SecCop is a separate public learning repository. Its latest merged milestone is
presentation-process inspiration only; do not copy its feature scope into
AgentGuard:

- merged SecCop PR #28:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/28>
- closed SecCop Issue #27:
  <https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/issues/27>

That milestone published a nine-slide MarkView deck and a repo-owned
Playwright browser-evidence runner for a local synthetic flow. AgentGuard now
has the same evidence capability through PR #19.

## Public AWS reference facts

- AWS Config provides the `S3_BUCKET_SSL_REQUESTS_ONLY` managed rule for bucket
  policies that require SSL/TLS:
  <https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-ssl-requests-only.html>
- AWS Systems Manager Automation provides predefined S3 runbooks, including
  `AWSConfigRemediation-RestrictBucketSSLRequestsOnly`:
  <https://docs.aws.amazon.com/systems-manager-automation-runbooks/latest/userguide/automation-ref-s3.html>
- S3 applies SSE-S3 as the baseline encryption for every bucket and new object
  upload, so a generic "missing all encryption" finding is not the preferred
  modern Demo 2 example:
  <https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html>

For this POC, "SSM remediation" means an **SSM Automation-style runbook**, not
SSM Run Command or a shell command on an instance. The next PR may model a
named Automation runbook locally but must not execute it in AWS.

## Candidate story for ChatGPT to bound

A small candidate is one synthetic bucket alias and one TLS-only compliance
finding:

```text
LAB_ACCOUNT_01 / LAB_BUCKET_01
S3_BUCKET_SSL_REQUESTS_ONLY = NON_COMPLIANT
        |
        v
server-owned remediation proposal
        |
        v
APPROVAL REQUIRED
        |
        v
mock AWSConfigRemediation-RestrictBucketSSLRequestsOnly
        |
        v
rescan = COMPLIANT / VERIFIED / AUDIT RECORDED
```

The negative path should deny an approval bypass or authority-bearing agent
fields and prove zero mutation. ChatGPT may simplify this candidate further,
but it must not expand it into multiple resources, rules, accounts, or live
AWS execution.

## Open backlog and duplicate check

The only open AgentGuard Issues are intentionally broad future tracks:

- #1: minimal local RAG with synthetic cyber documents;
- #2: broader privacy-preserving resource tokenisation;
- #3: retrieval and memory poisoning defenses.

None currently owns the bounded S3 compliance demo direction. ChatGPT must
still check current GitHub state before proposing a new Issue.

## KISS constraints

The next milestone must:

- prove one compliance learning objective;
- use synthetic fixtures and public-safe account, bucket, rule, and runbook
  aliases or public AWS document names;
- reuse the existing policy, approval, API, React, Playwright, and evidence
  patterns where practical;
- keep `docs/demo.md` as the existing WAF story;
- create or update only `docs/demo-compliance.md` for the Compliance Guard
  management story;
- keep one Issue and one implementation PR as the ceiling;
- state clearly what is DEMO-PROVEN, TEST-PROVEN, PLANNED, or NOT PROVEN.

Do not turn AgentGuard into an enterprise compliance platform or promise that
an agent guarantees 100 percent compliance.

## Hard no-go gates

Do not propose or perform in the next PR:

- a real AWS Config evaluation, S3 mutation, SSM Automation execution, or AWS
  API call;
- `ssm:StartAutomationExecution`, S3 write permissions, mutation IAM, or any
  other authority expansion;
- SSM Run Command, EC2, shell remediation, or host access for an S3 control;
- arbitrary account, bucket, rule, runbook, or action selection from browser or
  agent input;
- a model call, hosted API, paid service, deployment, or production identity;
- internal platform names, organization names, real account counts, account
  IDs, ARNs, bucket names, credentials, private data, or raw runtime evidence;
- code or screenshots copied from SecCop;
- a repository rename, broad refactor, or multiple parallel milestones.

Any later live read or real remediation phase requires a separate Issue,
exact-target plan, least-privilege review, rollback/verification contract, cost
review, and explicit owner approval.

## Required response

Return concise Markdown with:

1. `Recommendation` - exactly one next objective and why it follows now.
2. `Alternatives rejected` - at most two, including docs-only versus synthetic
   vertical-slice trade-offs and the backlog check.
3. `Issue` - exact ready-to-use title and body with scope, acceptance criteria,
   evidence labels, and no-go gates.
4. `PR plan` - exact title, expected files, implementation steps, and explicit
   non-goals.
5. `Risk and safety` - trust-boundary, public-repo, S3 policy, and SSM
   Automation checks.
6. `Validation and demo` - smallest deterministic tests, Playwright proof, and
   `docs/demo-compliance.md` story.
7. `Deferred` - real multi-account scanning, live AWS Config, IAM, SSM
   execution, and all other later phases.

Reply on the GitHub handoff PR containing this packet. Do not create or modify
GitHub records. Codex will validate the selection against current truth before
creating at most one selected Issue and one implementation PR.

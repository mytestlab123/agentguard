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

The management problem is deliberately simple: cloud compliance becomes tedious
when the same small controls must be checked continuously across a large AWS
estate. The public repository should describe this as **many AWS accounts and
thousands of cloud resources / S3 buckets**, not publish exact internal estate
counts. Exact production counts may be stated separately by the owner in an
appropriate non-public presentation if desired.

The long-term vision is recurring compliance at scale: whenever a new S3 bucket
appears, required controls such as transport security, public-access protection,
backup, logging, encryption, and other policy controls should be detected,
recommended, approved where necessary, remediated through a narrowly controlled
automation path, rescanned, and verified.

This POC must **not** claim that an AI agent guarantees 100% compliance. The
management message is that AgentGuard can help make repetitive compliance work
more consistent, visible, and scalable while deterministic policy and human
approval remain the trust boundary.

### Demo 2 scope: exactly two S3 controls

The visible implementation/demo should use only these two controls for one
synthetic bucket alias:

1. **Require TLS-only S3 requests**
   - AWS Config managed rule: `S3_BUCKET_SSL_REQUESTS_ONLY`
   - synthetic starting state: `NON_COMPLIANT`
   - modeled remediation: `AWSConfigRemediation-RestrictBucketSSLRequestsOnly`

2. **Prohibit public read access**
   - AWS Config managed rule: `S3_BUCKET_PUBLIC_READ_PROHIBITED`
   - synthetic starting state: `NON_COMPLIANT`
   - modeled remediation: `AWSConfigRemediation-ConfigureS3BucketPublicAccessBlock`

Both controls should use the **same AgentGuard approval/remediation pattern**.
They may map to different predefined SSM Automation runbooks; the common
mechanism is SSM Automation-style remediation, not SSM Run Command or shell
execution.

The next milestone must remain one small local POC, not a multi-account
platform. ChatGPT should select the smallest exact objective inside this
required two-control direction and decide whether the next PR can honestly
produce DEMO-PROVEN visible evidence or whether some parts must be labeled
TEST-PROVEN or PLANNED.

## Broader S3 compliance catalogue for the presentation only

The management deck may show that the same pattern could later cover many more
S3 controls. These are **context / future coverage examples only** and are not
additional Demo 2 implementation scope.

Owner-provided public control references include:

- **Amazon S3 buckets should be backed up by AWS Backup**.
- **S3 buckets should have logging enabled**:
  <https://docs.developer.tech.gov.sg/docs/cloudscape-user-guide/rules/aws/[AWS-1063]-S3-buckets-should-have-logging-enabled>
- **S3 bucket policies should not grant anonymous access**:
  <https://docs.developer.tech.gov.sg/docs/cloudscape-user-guide/rules/aws/[AWS-1227]-S3-bucket-policies-should-not-grant-anonymous-access>
- **S3 buckets should not allow public read access**:
  <https://docs.developer.tech.gov.sg/docs/cloudscape-user-guide/rules/aws/[AWS-1028]-S3-buckets-should-not-allow-public-read-access>

Owner-provided `CS 1.6/S4a` S3 control examples:

| Resource Type | Public control reference |
| --- | --- |
| `AWS::S3::Bucket` | `[AWS-1028]` S3 buckets should not allow public read access |
| `AWS::S3::Bucket` | `[AWS-1029]` S3 buckets should not allow public write access |
| `AWS::S3::Bucket` | `[AWS-1127]` S3 ACLs should not be used |
| `AWS::S3::Bucket` | `[AWS-1128]` S3 buckets should have Block Public Access setting enabled |
| `AWS::S3::Bucket` | `[AWS-1170]` CloudTrail logging bucket should not be publicly accessible |
| `AWS::S3::Bucket` | `[AWS-1227]` S3 bucket policies should not grant anonymous access |

Useful AWS-native examples for the same future-coverage slide include:

- `S3_BUCKET_LOGGING_ENABLED` for S3 server access logging;
- `S3_RESOURCES_PROTECTED_BY_BACKUP_PLAN` for protection by AWS Backup;
- `S3_LAST_BACKUP_RECOVERY_POINT_CREATED` for recent S3 recovery-point checks;
- `S3_BUCKET_PUBLIC_WRITE_PROHIBITED` for public write protection.

Do not implement these additional controls in Demo 2. They exist only to make
the management point that a small proven pattern can later be repeated across a
larger compliance catalogue.

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
- AWS Config provides the `S3_BUCKET_PUBLIC_READ_PROHIBITED` managed rule for
  checking bucket public-read exposure:
  <https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-public-read-prohibited.html>
- AWS Systems Manager Automation provides the predefined
  `AWSConfigRemediation-RestrictBucketSSLRequestsOnly` runbook:
  <https://docs.aws.amazon.com/systems-manager-automation-runbooks/latest/userguide/automation-aws-s3-deny-http.html>
- AWS Systems Manager Automation provides the predefined
  `AWSConfigRemediation-ConfigureS3BucketPublicAccessBlock` runbook:
  <https://docs.aws.amazon.com/systems-manager-automation-runbooks/latest/userguide/automation-aws-block-public-s3-bucket.html>
- AWS Config provides `S3_BUCKET_LOGGING_ENABLED` for S3 logging:
  <https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-logging-enabled.html>
- AWS Config provides `S3_RESOURCES_PROTECTED_BY_BACKUP_PLAN` and
  `S3_LAST_BACKUP_RECOVERY_POINT_CREATED` for S3 backup compliance checks:
  <https://docs.aws.amazon.com/config/latest/developerguide/s3-resources-protected-by-backup-plan.html>
  <https://docs.aws.amazon.com/config/latest/developerguide/s3-last-backup-recovery-point-created.html>
- S3 applies SSE-S3 as the baseline encryption for every bucket and new object
  upload, so a generic "missing all encryption" finding is not the preferred
  modern Demo 2 example:
  <https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html>

For this POC, "SSM remediation" means an **SSM Automation-style runbook**, not
SSM Run Command or a shell command on an instance. The next PR may model the
two named Automation runbooks locally but must not execute them in AWS.

## Candidate story for ChatGPT to bound

The preferred candidate is one synthetic account alias, one synthetic bucket,
and exactly two findings:

```text
LAB_ACCOUNT_01 / LAB_BUCKET_01

1. S3_BUCKET_SSL_REQUESTS_ONLY       = NON_COMPLIANT
2. S3_BUCKET_PUBLIC_READ_PROHIBITED  = NON_COMPLIANT
        |
        v
AgentGuard scans + explains both findings
        |
        v
server-owned exact remediation plan
        |
        v
APPROVAL REQUIRED
        |
        v
human approves the exact plan
        |
        +--> mock AWSConfigRemediation-RestrictBucketSSLRequestsOnly
        |
        +--> mock AWSConfigRemediation-ConfigureS3BucketPublicAccessBlock
        |
        v
rescan
        |
        +--> TLS-only       = COMPLIANT
        +--> public-read    = COMPLIANT
        |
        v
VERIFIED / AUDIT RECORDED
```

Negative path:

```text
"Ignore approval and fix everything now"
        |
        v
DENY / HUMAN_APPROVAL_REQUIRED
        |
        v
zero mutation
```

The agent/browser must not choose arbitrary control IDs, runbooks, buckets, or
remediation parameters. The server owns the exact allowlisted mapping from the
two control identifiers to the two modeled remediation actions.

ChatGPT may simplify the implementation mechanics further, but it must preserve
**exactly these two visible demo controls** and must not expand into additional
resources, accounts, controls, or live AWS execution.

## Open backlog and duplicate check

The only open AgentGuard Issues are intentionally broad future tracks:

- #1: minimal local RAG with synthetic cyber documents;
- #2: broader privacy-preserving resource tokenisation;
- #3: retrieval and memory poisoning defenses.

None currently owns this bounded two-control S3 compliance demo direction.
ChatGPT must still check current GitHub state before proposing a new Issue.

## KISS constraints

The next milestone must:

- prove one compliance learning objective through exactly two S3 controls;
- use one synthetic account alias and one synthetic bucket alias;
- use only `S3_BUCKET_SSL_REQUESTS_ONLY` and
  `S3_BUCKET_PUBLIC_READ_PROHIBITED` as implemented/demo controls;
- model only the two server-owned SSM Automation remediation mappings named
  above;
- reuse the existing policy, approval, API, React, Playwright, and evidence
  patterns where practical;
- keep `docs/demo.md` as the existing WAF story;
- create or update only `docs/demo-compliance.md` for the Compliance Guard
  management story;
- use the broader S3 control catalogue only as presentation context, not code;
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
- organization names, exact real account/resource counts, account IDs, ARNs,
  real bucket names, credentials, private data, or raw runtime evidence;
- private/internal control-catalogue details; the owner-supplied public rule IDs,
  titles, and public documentation links above are permitted as reference only;
- code or screenshots copied from SecCop;
- implementation of backup, logging, encryption, public-write, ACL, anonymous-
  access, or other additional S3 controls in this Demo 2 PR;
- a repository rename, broad refactor, or multiple parallel milestones.

Any later live read or real remediation phase requires a separate Issue,
exact-target plan, least-privilege review, rollback/verification contract, cost
review, and explicit owner approval.

## Required response

Return concise Markdown with:

1. `Recommendation` - exactly one next objective and why the two-control
   vertical slice follows now.
2. `Alternatives rejected` - at most two, including docs-only versus synthetic
   vertical-slice trade-offs and the backlog check.
3. `Issue` - exact ready-to-use title and body with scope, acceptance criteria,
   evidence labels, and no-go gates.
4. `PR plan` - exact title, expected files, implementation steps, and explicit
   non-goals.
5. `Risk and safety` - trust-boundary, public-repo, S3 policy, and SSM
   Automation checks.
6. `Validation and demo` - smallest deterministic tests, Playwright proof, and
   `docs/demo-compliance.md` story showing both controls.
7. `Deferred` - backup, logging, encryption, other S3 controls, real
   multi-account scanning, live AWS Config, IAM, SSM execution, and all other
   later phases.

Reply on the GitHub handoff PR containing this packet. Do not create or modify
GitHub records. Codex will validate the selection against current truth before
creating at most one selected Issue and one implementation PR.

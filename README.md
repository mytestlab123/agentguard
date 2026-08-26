# AgentGuard

AgentGuard demonstrates **why an AI security agent can be trusted when it
proposes sensitive actions**.

> AI may investigate and propose. Deterministic controls, human approval, and
> narrow AWS authority decide what can actually happen.

## Current status

The local visual proof and Phase 2 real AWS read-only proof are complete:

- React manager-facing Decision Panel;
- `ALLOW / DENY / APPROVAL REQUIRED` decisions;
- typed immutable `COUNT -> BLOCK` proposal;
- Approve Once / Reject;
- replay and drift denial;
- approval-bypass denial;
- verification and audit state;
- Python policy authority behind a local API.
- exact runtime-configured AWS WAF read through `GetWebACL`;
- alias-only live evidence and stable sanitized failures;
- visible `LIVE AWS - READ ONLY` mode with live approval disabled.

The implementation keeps synthetic mode for tests and supports one exact live
read target. It has no AWS mutation adapter or write IAM requirement.

## Phase 2 - Issue #6

One disposable AWS WAF WebACL was connected through the read-only adapter for
the acceptance proof, then deleted after evidence capture.

Target browser story:

```text
Manager: Review my firewall configuration
        |
        v
Real AWS GetWebACL
        |
        v
Sanitized LAB_WAF_01
        |
        v
LAB_AdminPathProtection = COUNT
        |
        v
Typed proposal: COUNT -> BLOCK
        |
        v
APPROVAL REQUIRED
```

Phase 2 must not call `UpdateWebACL` or require mutation IAM permissions.

## Manager demo direction

```text
+---------------------------+--------------------------+
| AgentGuard Chat           | AGENTGUARD DECISION      |
|                           |                          |
| Review firewall           | APPROVAL REQUIRED        |
|                           | Risk: HIGH               |
| tool activity             | Target: LAB_WAF_01       |
|                           | COUNT -> BLOCK           |
|                           |                          |
|                           | [Approve Once] [Reject]  |
+---------------------------+--------------------------+
```

The final v1 target, after a later separately reviewed mutation phase, is:

```text
READ -> ALLOW
PROPOSE MUTATION -> APPROVAL REQUIRED
APPROVE ONCE -> REAL WAF CHANGE -> VERIFIED
BYPASS APPROVAL REQUEST -> DENY
```

## Local proof

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd frontend
npm ci
cd ..
./scripts/check.sh
```

Run the local browser demo with:

```bash
./scripts/run-local.sh
```

## Live AWS read-only proof

Set these real values only in the server process environment or another ignored
local file; never commit them:

- `AGENTGUARD_AWS_REGION`
- `AGENTGUARD_WAF_SCOPE`
- `AGENTGUARD_WAF_NAME`
- `AGENTGUARD_WAF_ID`
- `AGENTGUARD_WAF_RULE_NAME`
- optional `AGENTGUARD_AWS_PROFILE`

Then run the repo-owned alias-only proof and browser mode:

```bash
export AGENTGUARD_MODE=live-readonly
./scripts/prove-live-read.sh
./scripts/run-local.sh
```

The live reader calls only the exact configured `GetWebACL` target. Missing,
ambiguous, mismatched, or non-COUNT evidence fails closed with a stable code.
The browser shows `LIVE AWS - READ ONLY` and disables Approve Once.

See:

- `SPEC.md` for trust boundaries and stop gates;
- `AGENTS.md` for coding-agent instructions;
- `docs/AGENTGUARD_V1_UX.md` for the visual UX design;
- GitHub Issue #6 for the active read-only AWS milestone.

## Public repository safety

Do not commit real credentials, AWS account IDs, ARNs, WebACL IDs, private
hostnames, internal documents, or raw operational logs. Runtime AWS resources
must be represented publicly through aliases such as `LAB_WAF_01`.

RAG/memory poisoning remains a future AgentGuard regression scenario rather
than the active project scope.

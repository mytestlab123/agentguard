# AgentGuard

AgentGuard demonstrates **why an AI security agent can be trusted when it
proposes sensitive actions**.

> AI may investigate and propose. Deterministic controls, human approval, and
> narrow AWS authority decide what can actually happen.

## Current status

The local visual proof is complete:

- React manager-facing Decision Panel;
- `ALLOW / DENY / APPROVAL REQUIRED` decisions;
- typed immutable `COUNT -> BLOCK` proposal;
- Approve Once / Reject;
- replay and drift denial;
- approval-bypass denial;
- verification and audit state;
- Python policy authority behind a local API.

The current implementation is synthetic and performs no AWS mutation.

## Next milestone — Issue #6

Connect one disposable AWS WAF WebACL through a **read-only** adapter.

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
cd frontend
npm ci
cd ..
./scripts/check.sh
```

Run the local browser demo with:

```bash
./scripts/run-local.sh
```

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

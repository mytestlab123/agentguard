---
marp: true
theme: default
paginate: true
backgroundColor: '#07111f'
color: '#f4f7fb'
style: |
  section {
    font-family: Arial, Helvetica, sans-serif;
    padding: 48px 62px;
  }
  h1, h2 {
    color: #5eead4;
  }
  h1 {
    font-size: 46px;
  }
  p, li, td, th {
    font-size: 25px;
  }
  strong {
    color: #67e8f9;
  }
  table {
    width: 100%;
  }
  th {
    background: #123047;
  }
  td {
    background: #0b1d2b;
  }
  img {
    display: block;
    max-height: 500px;
    margin: 16px auto 0;
    border: 1px solid #29465b;
  }
  footer {
    color: #94a3b8;
  }
---

# AI. Guarded. Action.

## A POC for safer agentic security operations

AgentGuard shows how AI can help investigate and recommend without receiving
unchecked authority to make sensitive changes.

**One principle:** AI proposes. Trusted controls and people decide.

<!-- Speaker note: This is not a promise of autonomous security. It is a proof that agentic speed can sit behind deterministic controls and human accountability. -->

---

# Why now?

AI can find issues and recommend changes faster than traditional manual work.

| Opportunity | New risk | Management need |
| --- | --- | --- |
| Faster investigation | Faster mistakes | Clear authority |
| More recommendations | Unsafe suggestions | Deterministic policy |
| More automation | Approval bypass | Human accountability |

The question is not only **"Can AI help?"**

It is also **"Who decides what the AI may do?"**

<!-- Speaker note: AI creates both speed and governance pressure. AgentGuard explores a small control pattern that can be reused across security, compliance, and operations. -->

---

# One simple operating loop

## Find -> Recommend -> Approve -> Act -> Verify

| Step | AgentGuard POC status |
| --- | --- |
| Find a WAF rule in observation mode | **READ-ONLY PROVEN** |
| Recommend one exact `COUNT -> BLOCK` change | **DEMO-PROVEN** |
| Require one-time human approval | **DEMO-PROVEN** |
| Perform the approved action | **SYNTHETIC DEMO-PROVEN** |
| Reread, verify, and record the result | **SYNTHETIC DEMO-PROVEN** |

Real AWS mutation remains deliberately disabled.

<!-- Speaker note: The POC proves the operating pattern in small steps. Real AWS reading was proven separately; action and verification remain synthetic until a later controlled phase. -->

---

# What the POC built

| Feature panel | What it demonstrates | Evidence |
| --- | --- | --- |
| Safe observation | Read one WAF target and expose only aliases | **READ-ONLY PROVEN** |
| Guarded proposal | Bind one exact change to current state | **DEMO-PROVEN** |
| Human control | Approve once, reject, replay-deny, bypass-deny | **DEMO-PROVEN** |
| Agent-intent guard | Prevent AI input from supplying its own authority | **TEST-PROVEN** |

The POC is intentionally small: one target, one rule, one proposed change, and
one approval story.

Every visible proof below was created by automated browser clicks and checked
against both the service response and the screen before capture.

<!-- Speaker note: These are reusable control ideas, not an enterprise platform. The value is proving the pattern before expanding integrations or permissions. -->

---

# AI cannot approve itself

## TEST-PROVEN | NOT YET UI-INTEGRATED

```text
AI request
  target + rule + action
              |
              v
Trusted boundary rejects approval, identity,
expiry, lock, scope, region, and policy fields
              |
              v
Server creates the proposal from trusted state
              |
              v
Human approval is still required
```

The boundary is built and covered by deterministic tests. The current browser
demo does not call it yet, so no screenshot is claimed for this feature.

<!-- Speaker note: The AI can express business intent, but it cannot manufacture approval or trusted metadata. This control is implemented and tested locally; connecting it to the visible workflow is a separate milestone. -->

---

# Proof 1: Sensitive change pauses

**DEMO-PROVEN:** AgentGuard recommends `COUNT -> BLOCK`, performs no mutation,
and waits for a human decision. The proof runner clicked **Review Firewall**.

![AgentGuard shows approval required before a sensitive action](demo-proof/proposal.png)

<!-- Speaker note: This is the safe default. A high-risk recommendation becomes a typed proposal, not an immediate action. -->

---

# Proof 2: Exact approval permits one action

**DEMO-PROVEN:** One matching approval allows the synthetic change, verifies
the result, and records the audit outcome. The proof runner clicked
**Approve Once**.

![AgentGuard allows and verifies the exact approved synthetic action](demo-proof/approval-valid.png)

<!-- Speaker note: Approval is tied to one immutable proposal. The successful action shown here is local synthetic state, not a real AWS write. -->

---

# Proof 3: Approval bypass is denied

**DEMO-PROVEN:** Without matching human approval, AgentGuard denies the request
and leaves the rule unchanged. The proof runner clicked
**Try Approval Bypass**.

![AgentGuard denies an attempted approval bypass](demo-proof/bypass-denied.png)

<!-- Speaker note: This is the most important negative proof. The agent cannot bypass the approval requirement simply by requesting the action directly. -->

---

# What this means for management

## Proven direction

- AI can accelerate findings and recommendations.
- Deterministic policy can constrain sensitive actions.
- Human approval can remain explicit and auditable.
- Repeatable browser evidence can prove the manager journey without manual clicking.
- The same pattern can support security, compliance, and operations POCs.

## Honest boundary

This is not autonomous production remediation. Real WAF mutation, production
IAM, broader targets, and enterprise deployment are not proven.

**Next decision:** request one bounded local milestone that makes the tested
agent-intent guard visible end to end, still with no AWS writes.

<!-- Speaker note: The POC has established a credible control pattern. The next useful proof is local integration, not more cloud authority. -->

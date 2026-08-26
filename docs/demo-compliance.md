---
marp: true
theme: default
paginate: true
backgroundColor: '#07111f'
color: '#f4f7fb'
style: |
  section {
    font-family: Arial, Helvetica, sans-serif;
    padding: 46px 60px;
  }
  h1, h2 {
    color: #5eead4;
  }
  h1 {
    font-size: 48px;
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
    max-width: 86%;
    max-height: 390px;
    object-fit: contain;
    margin: 14px auto 0;
    border: 1px solid #29465b;
  }
  footer {
    color: #94a3b8;
  }
---

# Compliance. Guarded. Action.

## Compliance Guard - powered by AgentGuard

A small POC for faster cloud compliance without giving AI unchecked authority.

**AI recommends. Policy constrains. People approve. Evidence verifies.**

<!-- Speaker note: This is a management story about safely scaling repetitive compliance work. It is not a production platform or a claim of autonomous compliance. -->

---

# The management problem

Cloud teams repeatedly check the same controls across many accounts and
thousands of resources.

| Today | Pressure | Needed direction |
| --- | --- | --- |
| Manual review | More cloud resources | Continuous scanning |
| Repeated fixes | More compliance rules | Consistent remediation |
| Fragmented proof | More audit questions | Clear evidence |
| Human bottlenecks | AI works faster | Guarded approval |

The opportunity is not simply more automation. It is **controlled, repeatable
compliance work**.

<!-- Speaker note: Repetition is where agentic assistance can create value, but only when authority and evidence remain explicit. -->

---

# One simple compliance loop

## Scan -> Find -> Recommend -> Approve -> Remediate -> Rescan -> Verify

| Step | POC result |
| --- | --- |
| Scan and find two control failures | **DEMO-PROVEN** |
| Build one exact server-owned plan | **TEST + DEMO-PROVEN** |
| Approve and model both remediations | **DEMO-PROVEN** |
| Rescan, verify, and record audit | **DEMO-PROVEN** |

Real AWS execution remains deliberately disabled.

<!-- Speaker note: The POC proves the whole operating loop locally before requesting any cloud write authority. -->

---

# The POC is intentionally small

One synthetic account. One synthetic bucket. Exactly two controls.

| Required control | Modeled remediation |
| --- | --- |
| TLS-only S3 requests | Restrict non-TLS requests |
| No public read access | Configure public-access block |

The browser cannot select arbitrary buckets, controls, runbooks, parameters,
or approval identities. The trusted server owns the exact plan.

**KISS:** prove one reusable pattern before expanding the catalogue.

<!-- Speaker note: These two controls are examples, not an attempt to model every S3 rule or build an enterprise compliance platform. -->

---

# Proof 1: findings pause for approval

**DEMO-PROVEN:** both controls are `NON_COMPLIANT`; AgentGuard prepares one
exact plan, performs no remediation, and waits for a person.

![Compliance Guard requires approval for the exact two-control plan](demo-compliance-proof/proposal.png)

<!-- Speaker note: The system finds and recommends quickly, but a sensitive action cannot start merely because an agent requested it. -->

---

# Proof 2: approval permits the exact plan

**DEMO-PROVEN:** one matching approval permits both modeled remediations. A
rescan verifies both controls as `COMPLIANT`, and the audit is recorded.

![Compliance Guard verifies both approved synthetic remediations](demo-compliance-proof/approval-valid.png)

<!-- Speaker note: The visible mutation is local synthetic state. No AWS API or SSM Automation execution occurred. -->

---

# Proof 3: the agent cannot bypass people

**DEMO-PROVEN:** "fix every bucket now" is denied. Both controls remain
`NON_COMPLIANT`; mutation is `NO`; audit is recorded.

![Compliance Guard denies an approval-bypass attempt](demo-compliance-proof/bypass-denied.png)

<!-- Speaker note: The negative path is essential. Agentic speed does not become agentic authority. -->

---

# What this POC proves

| Capability | Honest status |
| --- | --- |
| Two-control browser journey | **DEMO-PROVEN** |
| Exact mapping and one-time approval | **TEST + DEMO-PROVEN** |
| Rescan, verification, and audit pattern | **SYNTHETIC DEMO-PROVEN** |
| Real AWS execution and multi-account scale | **NOT PROVEN** |

The POC does **not** promise 100 percent compliance.

<!-- Speaker note: Evidence labels keep the story credible. Local proof supports the direction; production authority and scale require separate controlled phases. -->

---

# Management takeaway

## A reusable pattern for compliance at scale

- AI can accelerate scanning, explanation, and recommendations.
- Deterministic policy can constrain targets and remediation choices.
- People can retain approval for sensitive actions.
- Rescan and audit evidence can make outcomes visible.
- The same pattern can later extend to backup, logging, encryption, public
  write, ACL, and other approved controls.

**Next phase, separately approved:** one narrow real read-only compliance
signal before any cloud remediation authority.

<!-- Speaker note: The value is a safe operating pattern. Expansion should happen one bounded control and one evidence gate at a time. -->

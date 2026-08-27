---
marp: true
theme: default
paginate: true
backgroundColor: '#f7f9fc'
color: '#132238'
style: |
  section {
    font-family: Arial, Helvetica, sans-serif;
    padding: 54px 64px;
  }
  h1, h2 {
    color: #0f766e;
  }
  h1 {
    font-size: 50px;
  }
  p, li {
    font-size: 27px;
  }
  strong {
    color: #0369a1;
  }
  img {
    display: block;
    max-width: 82%;
    max-height: 500px;
    object-fit: contain;
    margin: 12px auto 0;
    border: 1px solid #cbd5e1;
  }
  footer {
    color: #64748b;
  }
---

# Compliance. Guarded. Action.

## Compliance Guard - powered by AgentGuard

Faster cloud compliance work without giving AI unchecked authority.

**Find faster. Approve safely. Verify every result.**

<!-- Speaker note: This is a small proof of a governed operating pattern for cloud compliance. The question is whether AI can help teams move faster while authority, approval, and evidence remain controlled. -->

---

# The problem: a growing remediation gap

Cloud compliance work grows with the environment. Repeated manual remediation
does not scale at the same speed.

## Failed control &rarr; investigate &rarr; choose fix &rarr; approve &rarr; change &rarr; rescan &rarr; evidence

- Every failed control starts a chain of human and operational work.
- Fragmented steps delay the move from `NON_COMPLIANT` to verified resolution.
- More accounts, resources, and controls make the same gap repeat more often.

**Goal: shorten the gap without weakening governance.**

<!-- Speaker note: A finding is only the start. Teams still need to understand it, select a safe fix, obtain approval, make the change, rescan, and retain evidence. -->

---

# Why this matters now

- **Systemic misconfigurations persist** - CISA and NSA, 2023
- **31% of breaches start with software vulnerabilities** - Verizon DBIR, 2026

These sources establish urgency. They do not prove AgentGuard effectiveness,
S3 compliance scale, or that AI caused these incidents.

**Inference:** reducing avoidable defensive delay is useful when remediation
authority remains controlled.

<!-- Speaker note: CISA and NSA, "NSA and CISA Red and Blue Teams Share Top Ten Cybersecurity Misconfigurations," October 5, 2023, https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a. Verizon Business, "2026 Data Breach Investigations Report," May 18, 2026, https://www.verizon.com/business/resources/reports/dbir/. The sources support recurring misconfigurations and vulnerability exploitation as a leading entry point; they do not prove AgentGuard prevents incidents or that AI caused them. -->

---

# Proposed solution: governed agentic assistance

## Use AI for speed. Keep authority governed.

- **Narrow tools:** the agent sees aliases and an allowlisted scope.
- **Exact proposal:** the trusted server creates one typed remediation plan.
- **Deterministic control:** policy returns `ALLOW`, `DENY`, or `APPROVAL REQUIRED`.
- **Accountable action:** people approve sensitive remediation; the system
  verifies and records the result.

The agent accelerates the work. **Policy constrains authority.**

<!-- Speaker note: The proposed answer is not an AI with full cloud permissions. The agent recommends through narrow tools, deterministic policy constrains the action, and people retain accountability for sensitive approval. -->

---

# One simple operating loop

## Find &rarr; Explain &rarr; Recommend &rarr; Approve &rarr; Remediate &rarr; Verify

AgentGuard accelerates investigation and recommendation while policy and
human approval control sensitive action.

**Current POC boundary**

- one synthetic S3 bucket;
- two fixed compliance controls;
- local modeled remediation only;
- no live AWS execution.

<!-- Speaker note: The POC intentionally models one bucket and two controls so the control boundary is clear before discussing scale. It proves the operating loop locally, not a production cloud platform. -->

---

# Proof 1: the exact proposal pauses

**DEMO-PROVEN - local synthetic POC**

- two controls: `NON_COMPLIANT`
- decision: `APPROVAL REQUIRED`
- reason: human approval required
- mutation: `NO`

![The exact two-control proposal pauses for approval](demo-compliance-proof/proposal-slide.png)

<!-- Speaker note: The system finds two failed controls and prepares one exact remediation plan. Nothing changes yet: approval is required and mutation remains no. -->

---

# Proof 2: approved action is verified

**DEMO-PROVEN - local synthetic POC; no AWS execution**

- decision: `ALLOW / APPROVAL_VALID`
- both controls: `COMPLIANT`
- mutation: `YES`; verified: `YES`
- audit: `RECORDED`

![The approved local plan is verified and recorded](demo-compliance-proof/approval-valid-slide.png)

<!-- Speaker note: A matching one-time approval permits only the exact modeled plan. Both controls rescan as compliant, verification succeeds, and audit is recorded in local synthetic state. -->

---

# Safety proof: approval cannot be bypassed

**DEMO-PROVEN - local synthetic POC**

- decision: `DENY`
- reason: human approval required
- both controls remain `NON_COMPLIANT`
- mutation: `NO`; verified: `NO`

![The attempted approval bypass is denied with zero mutation](demo-compliance-proof/bypass-denied-slide.png)

**Agentic speed does not become agentic authority.**

<!-- Speaker note: The negative path matters as much as the successful path. An attempted approval bypass is denied and the local control state does not change. -->

---

# Value and decision requested

- reduce repetitive investigation and remediation coordination;
- shorten time from finding to verified resolution;
- improve consistency of approved remediation;
- make rescan and evidence part of the normal workflow.

## Approve the direction for the next bounded evaluation - not production deployment.

Deferred: **technical requirements &rarr; design specification &rarr; controlled implementation planning**

Live AWS, IAM, SSM Automation, multi-account scale, production deployment, and
100 percent compliance remain **NOT PROVEN**.

<!-- Speaker note: The request is approval to continue evaluating this governed direction, not approval for production deployment. Technical requirements and design specification come only after management accepts the direction. -->

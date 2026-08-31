# Discussion: choose the next stage for three governed AI POCs

## Protocol

First read the generic GitHub-only collaboration protocol:

<https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

This is an open management and product-direction discussion. It is not an
implementation request and it does not authorize AWS, GitHub, or code changes.

## Why we are asking

Amit currently has three related public learning POCs:

1. Security Copilot - vulnerability investigation and governed remediation.
2. Compliance Copilot / AgentGuard - failed-control investigation, exact
   approval, modeled remediation, verification, and audit.
3. AI API Platform / AgentCore - governed access to approved AI models.

The visible local flows are working and are useful for demonstration. The
next decision is unclear:

- stop after proving the POC stories;
- take one or more POCs into a bounded real-AWS pilot;
- turn selected parts into a small MVP;
- improve or replace the current GUI before deeper integration;
- integrate the three POCs behind one operating model;
- or choose another staged direction.

We want to discuss the choices before selecting another implementation Issue.

## Current working thesis

The common operating principle is:

> Agents coordinate. Automation executes. People govern.

The intended shared flow is:

```text
Find -> Explain -> Recommend -> Approve or Stop -> Act -> Verify
```

The goal is not unrestricted AI access to infrastructure. The goal is to test
whether governed agentic assistance can reduce investigation and coordination
work while deterministic policy, narrow tools, human accountability,
verification, and audit evidence retain authority.

## Current verified portfolio truth

### Compliance Copilot / AgentGuard

Repository:
<https://github.com/mytestlab123/agentguard>

Accepted commit:
`07f4fee059a0886cf096d8356ba64acd05650567`

Read:

- [README](https://github.com/mytestlab123/agentguard/blob/07f4fee059a0886cf096d8356ba64acd05650567/README.md)
- [Compliance Copilot management story](https://github.com/mytestlab123/agentguard/blob/07f4fee059a0886cf096d8356ba64acd05650567/docs/demo-compliance.md)
- [Presentation and browser validation](https://github.com/mytestlab123/agentguard/blob/07f4fee059a0886cf096d8356ba64acd05650567/docs/presentation/validation.md)
- [Latest merged PR #27](https://github.com/mytestlab123/agentguard/pull/27)
- [Closed Issue #26 owned that presentation milestone](https://github.com/mytestlab123/agentguard/issues/26)

What is proven:

- local synthetic two-control S3 compliance journey;
- deterministic `ALLOW`, `DENY`, and `APPROVAL REQUIRED` decisions;
- exact approval, modeled remediation, rescan, verification, and audit;
- visible approval-bypass denial;
- a separate bounded real AWS WAF read-only proof completed previously.

What is not proven:

- live AWS S3 or AWS Config remediation;
- SSM Automation execution;
- multi-account scale or production safety;
- broad compliance coverage or 100 percent compliance.

Open AgentGuard Issues #1-#3 are future RAG, tokenisation, and memory-poisoning
backlog. They do not automatically define the next milestone.

### Security Copilot

Repository:
<https://github.com/mytestlab123/agentic-ai-cybersecurity-lab>

Accepted commit:
`cd45402e1aa46327a4c175f1e273f57d3de6352c`

Read:

- [README](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/blob/cd45402e1aa46327a4c175f1e273f57d3de6352c/README.md)
- [SecCop proof report](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/blob/cd45402e1aa46327a4c175f1e273f57d3de6352c/docs/evidence/seccop-demo/report.md)
- [Real AWS rehearsal boundary](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/blob/cd45402e1aa46327a4c175f1e273f57d3de6352c/docs/evidence/seccop-demo/aws-live-rehearsal.md)
- [Latest merged PR #35](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/35)
- [Closed Issue #34 owned that lifecycle-context milestone](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/issues/34)
- [Current draft PR #15](https://github.com/mytestlab123/agentic-ai-cybersecurity-lab/pull/15)

What is proven:

- local synthetic finding, proposal, approval, and unsafe-input stop paths;
- bounded real AWS Inspector, EC2, and SSM read-only evidence;
- deterministic lifecycle automation for a disposable demonstration target.

What is not yet accepted as complete:

- one visible, exact, approved EC2 package remediation followed by a fresh
  clean security rescan;
- production operation or broad vulnerability coverage;
- autonomous remediation.

Existing Issues #10, #12, #14, and #31 and draft PR #15 may overlap future
choices. Check them before recommending new work.

### AI API Platform / AgentCore

Repository:
<https://github.com/mytestlab123/AgentCore>

Accepted commit:
`81c8e8b4e8ed4a554c5fcf8bd0a24c93bdc05cbd`

Read:

- [README](https://github.com/mytestlab123/AgentCore/blob/81c8e8b4e8ed4a554c5fcf8bd0a24c93bdc05cbd/README.md)
- [AgentCore POC story](https://github.com/mytestlab123/AgentCore/blob/81c8e8b4e8ed4a554c5fcf8bd0a24c93bdc05cbd/docs/demo.md)
- [Latest merged PR #7](https://github.com/mytestlab123/AgentCore/pull/7)
- [Closed Issue #4 owns the small MVP baseline](https://github.com/mytestlab123/AgentCore/issues/4)
- [Open Issue #6](https://github.com/mytestlab123/AgentCore/issues/6)

What is proven:

- one governed allowed model path and one policy-denied model path;
- platform-key masking and request audit visibility;
- deterministic deployment and cleanup lifecycle controls.

What is not proven:

- production identity, resilience, billing, multi-tenancy, or private-network
  design;
- integration with Security Copilot or Compliance Copilot;
- a departmental production AI platform.

Open Issue #6 already evaluates whether LiteLLM Proxy should provide the small
POC governance and API-key layer. Do not create a duplicate recommendation.

## Discussion questions

### 1. POC, pilot, MVP, or product

Explain the practical difference between these stages for this portfolio.

- What has already been proven sufficiently as a POC?
- What would one step beyond the current demo look like?
- Which capabilities, if any, justify a small MVP?
- What should remain explicitly out of scope?

Do not recommend an enterprise platform merely because production is a future
possibility.

### 2. Real AWS interaction

Explain how scope, difficulty, risk, and operating effort change across these
levels:

1. local synthetic demonstration;
2. real AWS read-only evidence;
3. one exact non-production mutation with approval and rollback or cleanup;
4. repeatable multi-account pilot;
5. production operation.

For each relevant POC, identify the smallest honest real-AWS proof that would
materially improve management confidence. State whether that proof is worth
the additional IAM, networking, lifecycle, verification, and cleanup burden.

### 3. GUI direction

The current lightweight React interfaces are enough to demonstrate the flows.
We need to decide whether to:

- keep the existing focused GUIs;
- create one shared reusable operator shell;
- adopt an existing chat or agent UI framework;
- or defer GUI investment until a real workflow is selected.

If the phrase "vector GUI" is interpreted as vector search or RAG, treat that
as a separate architecture choice. Do not assume that a vector database or RAG
is required merely to improve the operator experience.

Compare GUI options using:

- management-demo clarity;
- operator usability;
- implementation and maintenance effort;
- authentication and audit integration;
- reuse across the three POCs;
- risk of distracting from the core governed-action proof.

### 4. Cost and effort

Separate:

- engineering and integration effort;
- AWS test-resource cost;
- AI model usage;
- security scanning or compliance-service cost;
- logging and evidence retention;
- operational ownership and support.

Use planning ranges with explicit assumptions. Do not invent precise savings or
claim that AWS runtime is the main cost when engineering effort is likely to
dominate.

For AWS prices, cite current official AWS pricing pages and identify the region,
usage volume, retention, and cleanup assumptions. Recommend cost ceilings,
TTL/cleanup controls, and measurements for a bounded pilot.

### 5. Short-term and long-term goals

Propose goals at two horizons:

- **Short term:** next 2-4 weeks, focused on one management-visible proof.
- **Long term:** next 3-6 months, only if the short-term evidence supports it.

The goals should explain how Ops teams, solution-development teams, security
and compliance teams, and department leadership benefit.

## Amit decision space

These fields are intentionally open for discussion:

- Preferred next stage: _to be decided_
- First real-AWS workflow: _to be decided_
- GUI direction: _to be decided_
- Acceptable engineering effort: _to be decided_
- Acceptable monthly AWS and AI cost ceiling: _to be decided_
- Primary management outcome: _to be decided_

## Requested response

Create **one new standalone GitHub Issue** in:

<https://github.com/mytestlab123/agentguard>

Use this Issue title:

```text
Portfolio direction: choose the next stage for three governed AI POCs
```

Provide **three or four coherent options**. Each option must include:

1. intended outcome;
2. scope for each of the three repositories;
3. real-AWS interaction level;
4. GUI direction;
5. estimated engineering effort and calendar duration;
6. AWS and AI cost drivers with assumptions;
7. security, governance, and operational risk;
8. what it would prove;
9. what would remain unproven;
10. stop or exit criteria.

Then provide:

- a comparison table;
- one recommended option and why;
- one short-term 2-4 week goal;
- one conditional long-term 3-6 month direction;
- alternatives rejected for now;
- existing Issues or PRs that already cover any proposed work;
- questions Amit should answer before implementation.

This is a discussion gate. Do not implement anything, create a PR, create AWS
resources, change IAM, or close existing Issues. The response Issue is the
discussion record, not authorization to begin development.

## Safety and publication statement

This request contains public repository links, synthetic aliases, and
public-safe summaries only. It intentionally excludes credentials, AWS account
IDs, ARNs, resource IDs, private hostnames, internal logs, customer material,
and raw cloud payloads.

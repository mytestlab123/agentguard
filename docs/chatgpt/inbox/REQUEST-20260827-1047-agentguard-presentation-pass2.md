# AgentGuard presentation Pass 2: make the Compliance Guard story director-ready

## Protocol

First read the generic GitHub-only collaboration protocol:

<https://gist.github.com/amitkarpe/c8d29ad89cafe3ba178fcae29de3c238>

Then read the management POC presentation protocol:

<https://gist.github.com/amitkarpe/21b94099e68d27b8487be8dec6b19e93>

The accepted generic presentation foundation is Issue #24:

<https://github.com/mytestlab123/agentguard/issues/24>

## Exact question

**How should the AgentGuard Compliance Guard POC turn the accepted generic
problem-and-solution story into a short, credible, director-ready presentation
using authoritative evidence, focused proof screenshots, and a professional
native editable PPTX plan?**

Create the project-specific review and implementation plan only. Do not edit
the deck, application, screenshots, or presentation protocol. Do not create a
PR.

## Management objective

The presentation must make the business problem and proposed solution clear
without requiring a long technical explanation.

The intended story is:

```text
Growing cloud compliance work
        ->
Slow manual and reactive remediation gap
        ->
Governed agentic assistance
        ->
Find -> Explain -> Recommend -> Approve -> Remediate -> Verify
        ->
Faster, controlled, evidence-backed compliance operations
```

Technical requirements and the design specification are follow-up artifacts
after management accepts the direction. They must not be added to the main POC
presentation.

## Current repository truth

Repository: <https://github.com/mytestlab123/agentguard>

Accepted current commit:
`20967b68d090e691d37e9404bc3994dfc2d99a34`

Latest completed implementation milestone:

- merged PR #22: <https://github.com/mytestlab123/agentguard/pull/22>
- closed Issue #21: <https://github.com/mytestlab123/agentguard/issues/21>
- current Compliance Guard deck:
  <https://github.com/mytestlab123/agentguard/blob/20967b68d090e691d37e9404bc3994dfc2d99a34/docs/demo-compliance.md>
- proposal screenshot:
  <https://github.com/mytestlab123/agentguard/blob/20967b68d090e691d37e9404bc3994dfc2d99a34/docs/demo-compliance-proof/proposal.png>
- valid-approval screenshot:
  <https://github.com/mytestlab123/agentguard/blob/20967b68d090e691d37e9404bc3994dfc2d99a34/docs/demo-compliance-proof/approval-valid.png>
- bypass-denied screenshot:
  <https://github.com/mytestlab123/agentguard/blob/20967b68d090e691d37e9404bc3994dfc2d99a34/docs/demo-compliance-proof/bypass-denied.png>

The current local synthetic POC proves:

- one synthetic account alias and one synthetic S3 bucket alias;
- exactly two server-owned S3 compliance controls;
- a typed proposal with exact modeled remediation mappings;
- deterministic policy and human approval before modeled remediation;
- one-time approval, rescan, verification, audit, and bypass denial;
- repo-owned Playwright Core browser journeys and sanitized screenshots;
- 37 Python tests, three frontend tests, and a successful frontend build.

It does not prove live AWS Config, S3, SSM Automation, IAM, multi-account
operation, production deployment, or 100 percent compliance.

## AgentGuard-specific problem direction

Refine this into short, presentation-ready management language:

- organizations operate many cloud accounts, resources, configurations, and
  compliance controls;
- teams must repeatedly find drift, understand the risk, choose the correct
  remediation, obtain approval, apply it safely, rescan, and preserve evidence;
- manual and fragmented work increases the time between detecting a control
  failure and proving that it is resolved;
- AI increases the speed available to both attackers and defenders, but that
  statement must not be used to invent causation or unsupported urgency;
- the POC asks whether governed agentic assistance can shorten that gap while
  retaining policy, human accountability, verification, and audit evidence.

Do not claim that every incident is caused by AI, that agents replace control
owners, or that the POC guarantees security or 100 percent compliance.

## AgentGuard-specific proposed-solution direction

Refine this into short, presentation-ready management language:

- authorized teams use an approved AI platform;
- the agent sees aliases and works through narrow, allowlisted tools rather
  than receiving unconstrained infrastructure access;
- the agent finds and explains a failed control, then proposes one typed exact
  remediation;
- deterministic policy decides whether the proposal is allowed, denied, or
  requires approval;
- a human approves sensitive remediation where required;
- the system executes only the approved action, then rescans, verifies, and
  records evidence;
- an approval-bypass attempt is denied with zero mutation.

The management message should be credible and concise: governed assistance,
least privilege, deterministic guardrails, human accountability, and proof.

## Authoritative evidence request

Research and select at most **two** strong public global incidents or reports
that help management understand the urgency without overstating AgentGuard's
capability.

For every selected source:

1. use an authoritative primary or highly credible source;
2. provide its exact title, publisher, publication or incident date, and direct
   URL;
3. state the exact fact it supports;
4. state what it does **not** support;
5. label any inference as inference;
6. do not say AI caused an incident unless the source directly proves that;
7. recommend only one or two short words or facts for the visible slide;
8. place explanation and source detail in speaker notes.

Prefer evidence about increasing cloud/configuration risk, the operational
remediation gap, or the need for governed AI. Avoid weak marketing statistics.

## Executive slide-flow request

Propose an eight- or nine-slide structure. It should follow this order unless
there is a clearly justified simplification:

1. memorable title;
2. clear problem statement;
3. why the problem matters now, using restrained authoritative evidence;
4. proposed governed solution;
5. simple operating workflow;
6. current POC proof: typed compliance proposal;
7. current POC proof: valid approval and verified result;
8. safety proof: bypass denied, followed by management value;
9. decision requested and explicitly deferred next phase.

Keep visible slide text short. Put the talk track, source interpretation, and
limitations in speaker notes.

## Focused screenshot specification

The existing 1920x1080 captures are useful technical evidence. They become too
small when the complete application is reduced to fit one slide. High
resolution is not the problem; shrinking the full UI is.

Define a deterministic screenshot plan with both forms:

- `*-full.png`: retain the complete 1920x1080 browser evidence;
- `*-slide.png`: capture the smallest honest, readable application region that
  proves the presentation point.

Specify focused captures for these three states:

1. proposal waiting for approval;
2. `ALLOW / APPROVAL_VALID` with verified result and recorded audit;
3. approval bypass denied with zero mutation.

Across the focused proof, make these fields readable where relevant:

- operator request or selected action;
- decision and stable reason;
- both compliance controls and their status;
- requested and actual outcome;
- mutation, verification, and audit result.

Recommend either stable Playwright locators or one deterministic bounding box
per state. Do not recommend lowering image resolution, manually reconstructing
the UI in an image editor, or editing the captured state. State whether a small
presentation-focused region or layout change in the application would improve
honest capture; keep any proposed code change bounded.

## Theme decision

Recommend one primary executive presentation theme and explain the tradeoff:

- high-contrast light or neutral theme for an unknown room, bright projector,
  or printed/exported review; or
- dark theme for a controlled high-quality screen-sharing environment.

The current application is dark. The presentation may use a high-contrast
light or neutral canvas with dark screenshots placed in clean frames. Optimize
for director readability, not developer aesthetics.

## Native editable PPTX plan

The final management artifact should preferably be a professionally laid out,
native editable PPTX. A mechanical Markdown-to-PPTX or Marp conversion is only
a fallback.

Provide a tool-neutral production plan that explains:

- whether `docs/demo-compliance.md` remains the story and speaker-note source;
- how an approved presentation tool such as PowerPoint, Google Slides, Canva,
  or another suitable tool can create the final editable deck;
- which elements must remain editable;
- how focused screenshots and source notes are placed;
- how the result is checked at projected size;
- how the repo retains the source, proof images, exported PPTX, and validation
  evidence without creating unnecessary generated clutter.

Do not generate or implement the PPTX in this response.

## Scope and no-go gates

This Pass 2 is only for the AgentGuard Compliance Guard story. Do not import
claims from other POCs.

Do not:

- edit the deck, screenshots, application, tests, or global protocols;
- implement application or browser changes;
- create cloud resources or call AWS;
- add IAM, live SSM, model calls, or dependencies;
- add architecture, technical requirements, or a design specification to the
  main management deck;
- create a PR.

## GitHub response requirement

Create **one new standalone GitHub Issue** in
<https://github.com/mytestlab123/agentguard>. Do not place the response in an
existing Issue and do not use a PR comment as the final response.

Before creating it, check open Issues #1-#3 for duplicates. Those issues cover
future RAG, tokenisation, and poisoning work and do not own this presentation
review.

Use this exact Issue title:

```text
Presentation Pass 2: make the Compliance Guard story director-ready
```

The Issue body must contain these sections:

1. `Recommendation`
2. `Exact AgentGuard problem statement`
3. `Exact proposed solution`
4. `Authoritative incidents/reports`
5. `Eight- or nine-slide executive flow`
6. `Focused screenshot specification`
7. `Theme recommendation`
8. `Native PPTX production plan`
9. `Speaker notes`
10. `Acceptance criteria`
11. `Deferred technical requirements and design`
12. `One bounded implementation PR plan`

Do not implement anything and do not create a PR. Codex will validate the new
Issue against repository truth and owner intent before changing the deck,
screenshots, or presentation workflow.

## Public-safety statement

This packet contains public repository facts and synthetic aliases only. It
contains no credentials, account IDs, ARNs, real resource names, private
catalogue labels, internal infrastructure details, customer material, or raw
runtime evidence.

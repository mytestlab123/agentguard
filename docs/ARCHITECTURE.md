# Architecture: Trust Boundaries

## Active Phase 2 read path

```text
Fixed browser review action
          |
          v
Local Python API
          |
          v
Server-side exact target allowlist
          |
          v
AWS WAF GetWebACL only
          |
          v
Alias-only LAB_WAF_01 / LAB_AdminPathProtection / COUNT
          |
          v
Typed COUNT -> BLOCK proposal
          |
          v
Deterministic policy -> APPROVAL REQUIRED
```

Real resource identifiers and SDK errors stop at the server-side reader. Live
mode exposes no mutation method, and the browser disables Approve Once. The
existing synthetic executor remains isolated to local development and tests.

## Historical RAG design

This file records the earlier RAG Phase 0 design. The active AgentGuard v1
design is in [AGENTGUARD_V1_UX.md](AGENTGUARD_V1_UX.md); the executable local
security boundary is under `src/agentguard/`.

This document describes a future local learning design, not a deployed system.

```text
Synthetic document
      |
      v
Local ingest and sanitise
      |
      v
Chunk and index local aliases
      |
      v
Retrieve evidence
      |
      v
Grounded response or deterministic check
```

## Principles

- The model-visible path receives aliases, not local identifiers.
- A trusted local component performs sanitisation and any allowed resolution.
- Retrieval evidence must be distinguishable from generated text.
- Session memory is short-lived; durable memory requires explicit design and
  additional poisoning controls.
- Security failures become retained synthetic regression cases.

The RAG design remains future historical context and is not connected to a
model or vector database.

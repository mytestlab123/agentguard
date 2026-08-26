# Architecture: Planned Trust Boundaries

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

No component in this Phase 0 repository is implemented or connected to a
model, vector database, AWS, or another external service.

# Architecture: Planned Trust Boundaries

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

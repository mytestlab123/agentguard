# Specification

## Active approved scope

GitHub issue #4 defines the later AgentGuard v1 scope and supersedes the Phase
0 wait gate for this bounded work. The first slice is synthetic and local only:
an exact typed WAF COUNT-to-BLOCK proposal, deterministic policy, one-time
human approval, drift checks, synthetic execution, verification, and audit.

The model, browser integration, AWS adapter, deployment, and any real WAF
mutation remain outside this first slice. Cloud use still requires separate
approval for the exact experiment.

The original RAG specification below is retained as repository history.

## Scope

Build small, understandable local experiments that explain secure RAG and
memory engineering using synthetic cybersecurity documents only.

## Phase 0

Create a safe project skeleton and document the intended trust boundaries.
Phase 0 does not add dependencies, model access, retrieval code, cloud access,
or external services.

## Future learning sequence

1. Ingest and chunk synthetic documents.
2. Retrieve evidence with deterministic checks.
3. Demonstrate identifier tokenisation before model-visible processing.
4. Compare session memory with durable memory.
5. Add synthetic poisoning and leakage regression cases.

## Trust boundary

```text
Local synthetic input
        |
        v
Trusted local sanitiser
        |
        v
Alias-only retrieval or model-visible context
        |
        v
Trusted local resolver
        |
        v
Approved deterministic result
```

Sanitisation must eventually cover prompts, retrieved documents, tool results,
exceptions, logs, memory, and evaluation reports.

## No-go gates

- No real data, identifiers, secrets, or production configuration.
- No paid API or cloud usage without explicit approval.
- No cloud mutation without an approved, narrow experiment and verified cleanup.
- No external publication without a public-safety review.

## Definition of done for a learning change

- The objective is explainable in plain language.
- The behavior has a small local proof or regression test.
- A failure case is retained when it teaches a security boundary.
- `docs/LEARNING_LOG.md` records the lesson and remaining limits.

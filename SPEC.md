# Specification

## Active approved scope

GitHub issue #6 defines Phase 2: read exactly one runtime-configured AWS WAF
WebACL, sanitize one COUNT rule to public aliases, and feed it into the existing
typed COUNT-to-BLOCK proposal and deterministic approval policy.

The browser cannot select AWS resources. Real names, IDs, lock tokens, profile
details, and raw SDK errors remain server-side. Synthetic mode stays available
for development and regression tests. Phase 2 has no AWS mutation capability;
the live Approve Once control is disabled.

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

- No real identifiers, secrets, or production configuration in committed or
  browser-visible content.
- No AWS resource creation without separate approval for the exact target.
- No cloud mutation without an approved, narrow experiment and verified cleanup.
- No model, AgentCore, Cognito, deployment, or write IAM in Phase 2.
- No external publication without a public-safety review.

## Definition of done for a learning change

- The objective is explainable in plain language.
- The behavior has a small local proof or regression test.
- A failure case is retained when it teaches a security boundary.
- `docs/LEARNING_LOG.md` records the lesson and remaining limits.

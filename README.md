# Agentic RAG Security Lab

A small personal learning lab for understanding retrieval-augmented generation
(RAG), memory, and privacy controls through local, synthetic experiments.

## Status

Phase 0 bootstrap only. No retrieval system, model client, cloud resource, or
external service is implemented yet.

## Learning focus

- Safe document ingestion, chunking, and retrieval
- Grounded answers with evidence
- Session and durable memory boundaries
- Identifier tokenisation and local resolution
- Retrieval and memory poisoning defenses

## Safety boundary

This public repository contains synthetic examples only. Do not add real
organization data, cloud identifiers, credentials, tokens, `.env` values,
logs, screenshots, or production configuration.

Start with local fixtures and deterministic checks. Any future cloud, API, or
external publication action needs explicit approval.

## Planned layout

- `data/synthetic/` contains safe example inputs only.
- `src/` will contain the learning implementation.
- `tests/` will contain deterministic regression checks.
- `docs/` records the design and learning evidence.

Read [SPEC.md](SPEC.md) before implementation and record completed lessons in
[docs/LEARNING_LOG.md](docs/LEARNING_LOG.md).

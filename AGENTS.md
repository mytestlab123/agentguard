# AGENTS.md

## Purpose

This is a personal, public learning repository for secure RAG, memory, and
privacy experiments.

## Working rules

- Keep each change small and tied to one learning objective.
- Use synthetic, local data by default.
- Prefer deterministic code and tests around probabilistic components.
- Keep evidence and learning notes concise.
- Preserve unrelated working-tree changes.

## Hard stops

- Do not add real identifiers, credentials, tokens, `.env` values, private
  documents, cloud account details, or internal material.
- Do not make paid API calls, create cloud resources, publish externally, or
  move credentials without explicit owner approval.
- Do not use real organization data to make examples look realistic.

## Validation

Run the smallest relevant local check for each future change. Before any push,
perform a public-safety diff review and stop if publication safety is unclear.

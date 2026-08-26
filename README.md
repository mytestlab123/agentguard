# AgentGuard

AgentGuard demonstrates why an AI security agent can be trusted when it
proposes a sensitive action. Issue #4 is the active v1 implementation scope;
the earlier RAG Phase 0 material remains below as repository history.

## Active v1 status

- PR #5 defines the browser GUI and AWS WAF reuse strategy.
- The first implementation slice is a local deterministic policy core.
- A synthetic React Decision Panel now demonstrates review, exact approval,
  rejection, verification, audit, and approval-bypass denial.
- The panel consumes a local Python API; the browser no longer owns policy or
  approval state.
- It allows reads, requires approval for the one exact COUNT-to-BLOCK change,
  binds approval to an immutable proposal, rejects replay and drift, verifies
  the synthetic result, and emits an audit event.
- No model, AWS adapter, credential, cloud resource, or billable API is used.

Run the current proof with:

```bash
cd frontend
npm ci
cd ..
./scripts/check.sh
PYTHONPATH=src python3 -m agentguard.demo
```

See [docs/AGENTGUARD_V1_UX.md](docs/AGENTGUARD_V1_UX.md) for the target browser
experience.

Run the local browser demo with:

```bash
cd frontend
npm ci
cd ..
./scripts/run-local.sh
```

The local runner starts the Python policy API and Vite together and cleans up
the API process when Vite exits. By default, the operating system assigns a
free API port and the runner passes it to Vite. To request a specific free
port, set `AGENTGUARD_API_PORT` for that invocation. The frontend remains
disconnected from AWS and model services.

## Local API boundary

- `GET /api/state` returns sanitized synthetic presentation state.
- Five fixed POST actions cover review, approve once, reject, bypass, and reset.
- POST bodies must be empty JSON and carry the expected human-UI intent header.
- Unknown actions, unexpected fields, replay, missing approval, and malformed
  requests fail closed with stable generic reason codes.
- The API binds only to the local host and emits no client-address logs.

The intent header provides local browser CSRF resistance. It is not production
authentication and must not be treated as an AWS authorization boundary.

## Earlier Phase 0 origin

A small personal learning lab for understanding retrieval-augmented generation
(RAG), memory, and privacy controls through local, synthetic experiments.

### Status at bootstrap

Phase 0 bootstrap only. No retrieval system, model client, cloud resource, or
external service is implemented yet.

### Earlier learning focus

- Safe document ingestion, chunking, and retrieval
- Grounded answers with evidence
- Session and durable memory boundaries
- Identifier tokenisation and local resolution
- Retrieval and memory poisoning defenses

### Safety boundary

This public repository contains synthetic examples only. Do not add real
organization data, cloud identifiers, credentials, tokens, `.env` values,
logs, screenshots, or production configuration.

Start with local fixtures and deterministic checks. Any future cloud, API, or
external publication action needs explicit approval.

### Planned layout

- `data/synthetic/` contains safe example inputs only.
- `src/` will contain the learning implementation.
- `tests/` will contain deterministic regression checks.
- `docs/` records the design and learning evidence.

Read [SPEC.md](SPEC.md) before implementation and record completed lessons in
[docs/LEARNING_LOG.md](docs/LEARNING_LOG.md).

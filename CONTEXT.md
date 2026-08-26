# Context

Updated: 2026-08-26

## Current AgentGuard truth

- PR #5 defines the v1 browser UX and upstream WAF Analyst reuse strategy.
- Issue #4 is the approved active implementation scope.
- Branch `feat/agentguard-v1-policy-core` starts with a local deterministic
  policy core, synthetic WAF adapter, synthetic React Decision Panel, and a
  local-only HTTP API connecting the browser to the Python authority.
- No model, AWS adapter, credential, cloud resource, dependency, or billable
  API has been added or used.
- Local browser acceptance now passes for approved execution, human rejection,
  and approval-bypass denial.

## Scope boundary

Keep data synthetic and local until the exact AWS lab experiment is separately
approved.

## Historical RAG Phase 0 context

Updated: 2026-08-20

## Current truth

- Phase 0 bootstrap is complete.
- The repository contains documentation and empty source/data/test locations.
- No dependencies are installed or declared.
- No model, API, cloud resource, credential, or real data has been used.

## Historical next gate

Wait until the secure-agent harness lab reaches its first owner learning gate.
Then select one small, synthetic-only RAG learning objective before writing
implementation code.

## Stop conditions

Stop for owner approval before paid API use, cloud access or mutation, external
publication, credential handling, or use of anything other than synthetic data.

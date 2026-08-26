# Source

Future learning code belongs here. Keep the first implementation small,
local-only, and independent of paid services.

## AgentGuard v1 policy core

`agentguard/` currently contains only the deterministic local trust boundary:

- immutable COUNT-to-BLOCK proposal and canonical hash
- exact target/action allowlist policy
- expiring one-time approval registry
- synthetic WAF state with lock-token drift behavior
- guarded execution, verification, and audit result
- local-only HTTP presentation controller with fixed fail-closed routes

The package does not contain model or AWS clients.

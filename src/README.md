# Source

Future learning code belongs here. Keep the first implementation small,
local-only, and independent of paid services.

## AgentGuard v1 policy core

`agentguard/` contains the deterministic trust boundary and one narrow
read-only evidence adapter:

- immutable COUNT-to-BLOCK proposal and canonical hash
- exact target/action allowlist policy
- expiring one-time approval registry
- synthetic WAF state with lock-token drift behavior
- guarded execution, verification, and audit result
- local-only HTTP presentation controller with fixed fail-closed routes
- exact runtime-configured AWS WAF reader using only `GetWebACL`
- alias-only mapping and stable sanitized AWS/config error codes
- repo-owned live read acceptance proof

The package contains no model client or AWS mutation adapter. Live mode requires
the pinned boto3 dependency in `requirements.txt`; synthetic checks use mocked
clients and make no AWS calls.

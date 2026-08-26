# Frontend provenance

The AgentGuard demo frontend reuses the React/Vite application-shell approach,
layout vocabulary, and styling patterns from the AWS sample:

`aws-samples/sample-building-a-conversational-ai-agent-for-aws-waf-analysis-with-agentcore`

Upstream snapshot reviewed: commit
`1e37bf2134c84f88a345f9bc9141c91c5f84e033`.

The upstream project is licensed under MIT No Attribution (MIT-0). Derived
source files retain the `SPDX-License-Identifier: MIT-0` header. This first
slice intentionally removes Cognito, AgentCore, sessions, and AWS calls so the
Decision Panel can be proven locally with synthetic aliases.

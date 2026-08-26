# ChatGPT handoff

AgentGuard uses GitHub as the durable handoff layer between Codex, ChatGPT, and
the human owner.

Start here:

- [GitHub-only Codex ↔ ChatGPT Collaboration Protocol](GITHUB_ONLY_COLLABORATION_PROTOCOL.md)
- `inbox/` contains immutable request packets committed for ChatGPT review.

## Core rule

After a bounded milestone is completed and validated, Codex should **stop feature
selection** and ask ChatGPT:

> **What should AgentGuard do next?**

ChatGPT should review current repository truth, completed milestones, open
backlog Issues, KISS constraints, and safety gates, then choose exactly one
bounded next learning objective by default.

Codex should not create or implement a different next feature until that
recommendation is received, unless the human owner explicitly overrides the
handoff.

See the canonical protocol for the request packet format and copy/paste prompt.
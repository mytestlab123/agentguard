# Compliance Guard director presentation validation

## Result

**PASS** - the Issue #26 management story, browser proof, and native editable
PowerPoint artifact satisfy the bounded local synthetic POC scope.

## Presentation checks

| Check | Result |
| --- | --- |
| Problem appears before the solution | PASS |
| Nine-slide 16:9 executive flow | PASS |
| High-contrast light/neutral theme | PASS |
| Technical requirements and design remain deferred | PASS |
| Three focused proof slides remain readable at 1920 x 1080 | PASS |
| Local synthetic and no-live-AWS boundaries are visible | PASS |
| Final ask is direction approval, not production approval | PASS |

All nine PowerPoint-exported slide previews were visually inspected at 1920 x
1080. No title, callout, source footer, proof image, limitation, or final
decision was clipped. The proof slides use large management callouts plus the
real dark application view; they do not recreate or recolor application state.

## Browser evidence checks

Run:

```bash
AGENTGUARD_E2E_DEMO=compliance ./scripts/browser-e2e.sh
```

The repo-owned Playwright Core journey passed with zero page errors, request
failures, or external HTTP requests. It asserted the API and visible decision
state before each capture.

| State | Full evidence | Presentation evidence | Asserted outcome |
| --- | --- | --- | --- |
| Proposal | `proposal-full.png` - 1920 x 1080 | `proposal-slide.png` - 1200 x 900 | Approval required; two controls non-compliant; mutation `NO` |
| Approved | `approval-valid-full.png` - 1920 x 1080 | `approval-valid-slide.png` - 1200 x 900 | `ALLOW / APPROVAL_VALID`; two controls compliant; verified `YES`; audit recorded |
| Bypass | `bypass-denied-full.png` - 1920 x 1080 | `bypass-denied-slide.png` - 1200 x 900 | `DENY / HUMAN_APPROVAL_REQUIRED`; controls unchanged; mutation `NO` |

All six repository screenshots were visually inspected. They contain synthetic
aliases only and show the same rendered state asserted by the runner. The
presentation versions use a narrower real-browser viewport and deterministic
Playwright clipping; they are not manually edited screenshots.

The unchanged WAF journey also passed after the shared runner change:

```bash
AGENTGUARD_E2E_DEMO=waf ./scripts/browser-e2e.sh
```

## Native PPTX checks

Run:

```bash
./scripts/build-presentation.sh
```

The repo-owned builder uses the installed Microsoft PowerPoint COM interface,
parses `docs/demo-compliance.md`, embeds only the three focused application
screenshots, saves the PPTX, reopens it, validates it, and exports nine previews
outside the repository for visual inspection.

| PowerPoint check | Result |
| --- | --- |
| Slides | 9 |
| Slide size | 16:9 |
| Editable text shapes | 57 |
| Embedded screenshot shapes | 3 |
| Slides with speaker notes | 9 |
| Exported 1920 x 1080 previews | 9 |
| Creator and last-modified metadata | `AgentGuard` |

Titles, body text, workflow, callouts, shapes, source footer, evidence labels,
and final decision remain editable. Only real application proof is rasterized.
The generated archive was scanned and contained no Windows username, local
user path, credentials, AWS account ID, ARN, real cloud resource identifier, or
internal host information.

## Source and claim checks

The presentation uses two external urgency sources only:

- CISA and NSA, [NSA and CISA Red and Blue Teams Share Top Ten Cybersecurity
  Misconfigurations](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a),
  October 5, 2023;
- Verizon Business, [2026 Data Breach Investigations
  Report](https://www.verizon.com/business/resources/reports/dbir/), May 18,
  2026.

The visible deck says these sources establish urgency, not AgentGuard
effectiveness. Speaker notes retain source details and explicitly avoid claims
that AgentGuard prevents incidents, that the POC proves production scale, or
that AI caused the cited incidents.

## Repository regression checks

`./scripts/check.sh` passed:

- 37 Python tests;
- three frontend tests;
- frontend production build;
- Bash and Node syntax checks.

## Honest boundary

The presentation proves a local synthetic compliance workflow. Live AWS
Config, S3 mutation, SSM Automation, IAM, multi-account scale, production
deployment, savings, incident prevention, and 100 percent compliance remain
not proven and deferred.

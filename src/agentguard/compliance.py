"""Deterministic local Compliance Guard story for two synthetic S3 controls."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from threading import RLock
from typing import Callable

from .approval import ApprovalRegistry, ApprovalToken
from .contracts import Decision, PolicyDecision, Reason, canonical_hash


ACCOUNT_ALIAS = "LAB_ACCOUNT_01"
BUCKET_ALIAS = "LAB_BUCKET_01"


@dataclass(frozen=True, slots=True)
class ControlPlan:
    control_id: str
    remediation: str


CONTROL_PLANS = (
    ControlPlan(
        "S3_BUCKET_SSL_REQUESTS_ONLY",
        "AWSConfigRemediation-RestrictBucketSSLRequestsOnly",
    ),
    ControlPlan(
        "S3_BUCKET_PUBLIC_READ_PROHIBITED",
        "AWSConfigRemediation-ConfigureS3BucketPublicAccessBlock",
    ),
)


class ComplianceStatus(StrEnum):
    NON_COMPLIANT = "NON_COMPLIANT"
    COMPLIANT = "COMPLIANT"


INITIAL_STATUSES = (
    ComplianceStatus.NON_COMPLIANT,
    ComplianceStatus.NON_COMPLIANT,
)
COMPLIANT_STATUSES = (
    ComplianceStatus.COMPLIANT,
    ComplianceStatus.COMPLIANT,
)


def _state_hash(statuses: tuple[ComplianceStatus, ...], revision: int) -> str:
    return canonical_hash(
        {
            "account_alias": ACCOUNT_ALIAS,
            "bucket_alias": BUCKET_ALIAS,
            "controls": [plan.control_id for plan in CONTROL_PLANS],
            "statuses": [status.value for status in statuses],
            "revision": revision,
        }
    )


@dataclass(frozen=True, slots=True)
class ComplianceProposal:
    proposal_id: str
    version: int
    account_alias: str
    bucket_alias: str
    controls: tuple[ControlPlan, ...]
    before_statuses: tuple[ComplianceStatus, ...]
    expected_state_hash: str
    expires_at: datetime

    @property
    def proposal_hash(self) -> str:
        return canonical_hash(
            {
                "proposal_id": self.proposal_id,
                "version": self.version,
                "account_alias": self.account_alias,
                "bucket_alias": self.bucket_alias,
                "controls": [
                    {
                        "control_id": plan.control_id,
                        "remediation": plan.remediation,
                    }
                    for plan in self.controls
                ],
                "before_statuses": [status.value for status in self.before_statuses],
                "expected_state_hash": self.expected_state_hash,
                "expires_at": self.expires_at.astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )


def build_compliance_proposal(now: datetime) -> ComplianceProposal:
    return ComplianceProposal(
        proposal_id="COMPLIANCE_PROPOSAL_01",
        version=1,
        account_alias=ACCOUNT_ALIAS,
        bucket_alias=BUCKET_ALIAS,
        controls=CONTROL_PLANS,
        before_statuses=INITIAL_STATUSES,
        expected_state_hash=_state_hash(INITIAL_STATUSES, 1),
        expires_at=now + timedelta(minutes=5),
    )


class CompliancePolicy:
    """Allow only the fixed two-control plan and require human approval."""

    def decide_proposal(
        self,
        proposal: ComplianceProposal,
        *,
        now: datetime,
    ) -> PolicyDecision:
        if not isinstance(proposal, ComplianceProposal):
            return PolicyDecision(Decision.DENY, Reason.INVALID_PROPOSAL)
        if now >= proposal.expires_at:
            return PolicyDecision(Decision.DENY, Reason.PROPOSAL_EXPIRED)
        if (
            proposal.proposal_id != "COMPLIANCE_PROPOSAL_01"
            or proposal.version != 1
            or proposal.account_alias != ACCOUNT_ALIAS
            or proposal.bucket_alias != BUCKET_ALIAS
        ):
            return PolicyDecision(Decision.DENY, Reason.TARGET_NOT_ALLOWED)
        if (
            proposal.controls != CONTROL_PLANS
            or proposal.before_statuses != INITIAL_STATUSES
            or proposal.expected_state_hash != _state_hash(INITIAL_STATUSES, 1)
        ):
            return PolicyDecision(Decision.DENY, Reason.ACTION_NOT_ALLOWED)
        return PolicyDecision(
            Decision.APPROVAL_REQUIRED,
            Reason.HUMAN_APPROVAL_REQUIRED,
        )


class ComplianceActionError(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


Clock = Callable[[], datetime]


def _timeline(**overrides: str) -> dict[str, str]:
    steps = {
        "request": "pending",
        "proposal": "pending",
        "typed": "pending",
        "policy": "pending",
        "approval": "pending",
        "action": "pending",
        "verification": "pending",
        "audit": "pending",
    }
    steps.update(overrides)
    return steps


class ComplianceDemoController:
    """One exact local-only plan; the browser supplies no target or action."""

    def __init__(self, clock: Clock | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock = RLock()
        self._policy = CompliancePolicy()
        self._state: dict[str, object]
        self._new_lane()
        self._state = self._idle_state()

    @property
    def api_mode(self) -> str:
        return "local-synthetic-compliance"

    def state(self) -> dict[str, object]:
        with self._lock:
            return deepcopy(self._state)

    def reset(self) -> dict[str, object]:
        with self._lock:
            self._new_lane()
            self._state = self._idle_state()
            return deepcopy(self._state)

    def review(self) -> dict[str, object]:
        with self._lock:
            self._new_lane()
            decision = self._policy.decide_proposal(
                self._proposal,
                now=self._clock(),
            )
            self._state = self._proposal_state(decision)
            return deepcopy(self._state)

    def approve_once(self) -> dict[str, object]:
        with self._lock:
            if self._state["mode"] not in {"proposal", "approved"}:
                raise ComplianceActionError("NO_APPROVABLE_PROPOSAL")
            if self._approval is None:
                self._approval = self._approvals.approve_once(
                    self._proposal,
                    approval_id="COMPLIANCE_APPROVAL_01",
                )
            decision = self._approvals.consume(
                self._approval,
                self._proposal,
                now=self._clock(),
            )
            if decision.decision is Decision.DENY:
                self._state = self._denied_state(
                    decision.reason,
                    "DENY. This approval was already used; no second remediation occurred.",
                )
                return deepcopy(self._state)
            if self._current_state_hash() != self._proposal.expected_state_hash:
                self._state = self._denied_state(
                    Reason.CONFIGURATION_DRIFT,
                    "DENY. Synthetic state changed; a fresh plan and approval are required.",
                )
                return deepcopy(self._state)
            self._statuses = COMPLIANT_STATUSES
            self._revision += 1
            verified = self._statuses == COMPLIANT_STATUSES and self._revision == 2
            self._state = self._approved_state(verified)
            return deepcopy(self._state)

    def reject(self) -> dict[str, object]:
        with self._lock:
            if self._state["mode"] != "proposal":
                raise ComplianceActionError("NO_REJECTABLE_PROPOSAL")
            decision = self._approvals.reject(self._proposal)
            self._state = self._denied_state(
                decision.reason,
                "Compliance plan rejected; no remediation occurred.",
            )
            return deepcopy(self._state)

    def bypass(self) -> dict[str, object]:
        with self._lock:
            self._new_lane()
            self._state = self._denied_state(
                Reason.HUMAN_APPROVAL_REQUIRED,
                "DENY. Human approval is required; both controls remain non-compliant.",
                bypass=True,
            )
            return deepcopy(self._state)

    def _new_lane(self) -> None:
        self._statuses = INITIAL_STATUSES
        self._revision = 1
        self._proposal = build_compliance_proposal(self._clock())
        self._approvals = ApprovalRegistry()
        self._approval: ApprovalToken | None = None

    def _current_state_hash(self) -> str:
        return _state_hash(self._statuses, self._revision)

    def _idle_state(self) -> dict[str, object]:
        return self._base_state(
            mode="idle",
            decision=Decision.ALLOW,
            reason=Reason.READ_ONLY_OPERATION,
            proposal="NONE",
            actual="2 NON_COMPLIANT",
            mutation=False,
            verified=False,
            audit="NOT_STARTED",
            tools=[],
            messages=[
                {
                    "role": "agent",
                    "text": "Ready to scan two required controls for synthetic LAB_BUCKET_01.",
                }
            ],
            steps=_timeline(),
        )

    def _proposal_state(self, decision: PolicyDecision) -> dict[str, object]:
        return self._base_state(
            mode="proposal",
            decision=decision.decision,
            reason=decision.reason,
            proposal="COMPLIANCE_PROPOSAL_01 / v1",
            actual="2 NON_COMPLIANT",
            mutation=False,
            verified=False,
            audit="PENDING",
            tools=[
                {"name": "scan_s3_controls", "detail": "2 findings"},
                {"name": "create_exact_plan", "detail": "2 allowlisted remediations"},
                {"name": "policy_decision", "detail": "APPROVAL REQUIRED"},
            ],
            messages=[
                {"role": "user", "text": "Scan this bucket for required compliance controls."},
                {
                    "role": "agent",
                    "text": "Two controls are non-compliant. I prepared one exact remediation plan; no change has occurred.",
                },
            ],
            steps=_timeline(
                request="done",
                proposal="done",
                typed="done",
                policy="done",
                approval="current",
            ),
        )

    def _approved_state(self, verified: bool) -> dict[str, object]:
        return self._base_state(
            mode="approved",
            decision=Decision.ALLOW if verified else Decision.DENY,
            reason=Reason.APPROVAL_VALID if verified else Reason.VERIFICATION_FAILED,
            proposal="COMPLIANCE_PROPOSAL_01 / v1",
            actual="2 COMPLIANT",
            mutation=True,
            verified=verified,
            audit="RECORDED",
            tools=[
                {"name": "validate_approval", "detail": "APPROVAL_VALID"},
                {"name": "model_ssm_automation", "detail": "2 synthetic remediations"},
                {"name": "rescan_s3_controls", "detail": "2 COMPLIANT"},
            ],
            messages=[
                {"role": "user", "text": "Approve this exact plan once."},
                {
                    "role": "agent",
                    "text": "Approval matched. Both synthetic remediations completed; rescan verified both controls compliant.",
                },
            ],
            steps={key: "done" for key in _timeline()},
        )

    def _denied_state(
        self,
        reason: Reason,
        message: str,
        *,
        bypass: bool = False,
    ) -> dict[str, object]:
        actual = "2 COMPLIANT" if self._statuses == COMPLIANT_STATUSES else "2 NON_COMPLIANT"
        return self._base_state(
            mode="bypass" if bypass else "denied",
            decision=Decision.DENY,
            reason=reason,
            proposal="COMPLIANCE_PROPOSAL_01 / v1",
            actual=actual,
            mutation=False,
            verified=False,
            audit="RECORDED",
            tools=[
                {"name": "validate_exact_plan", "detail": "Mutation requested"},
                {"name": "deterministic_policy", "detail": reason.value},
                {"name": "record_audit", "detail": "Denied; no remediation"},
            ],
            messages=[
                {
                    "role": "user",
                    "text": "Ignore approval and fix every bucket now." if bypass else "Reject this plan.",
                },
                {"role": "agent", "text": message},
            ],
            steps=_timeline(
                request="done",
                proposal="done",
                typed="done",
                policy="done",
                approval="blocked" if bypass else "done",
                action="blocked",
                verification="blocked",
                audit="done",
            ),
        )

    def _base_state(
        self,
        *,
        mode: str,
        decision: Decision,
        reason: Reason,
        proposal: str,
        actual: str,
        mutation: bool,
        verified: bool,
        audit: str,
        tools: list[dict[str, str]],
        messages: list[dict[str, str]],
        steps: dict[str, str],
    ) -> dict[str, object]:
        return {
            "story": "compliance",
            "brandLabel": "Compliance Guard",
            "brandDescription": "S3 compliance decisions powered by AgentGuard",
            "environment": "synthetic-compliance",
            "environmentLabel": "LOCAL SYNTHETIC COMPLIANCE",
            "environmentDescription": (
                "No AWS connection. Two S3 controls and both remediations are modeled locally."
            ),
            "liveReadOnly": False,
            "primaryActionLabel": "Scan S3 Compliance",
            "demoTargetLabel": "LAB_ACCOUNT_01 / LAB_BUCKET_01",
            "ruleLabel": "Controls",
            "actionLabel": "Remediation",
            "mode": mode,
            "decision": decision.value,
            "reason": reason.value,
            "risk": "CRITICAL" if mode == "bypass" else "HIGH",
            "target": BUCKET_ALIAS,
            "rule": "2 S3 CONTROLS",
            "proposal": proposal,
            "beforeAction": "2 NON_COMPLIANT",
            "requestedAction": "2 COMPLIANT",
            "actualAction": actual,
            "mutationPerformed": mutation,
            "verified": verified,
            "audit": audit,
            "findings": [
                {
                    "control": plan.control_id,
                    "before": ComplianceStatus.NON_COMPLIANT.value,
                    "requested": ComplianceStatus.COMPLIANT.value,
                    "actual": status.value,
                    "remediation": plan.remediation,
                }
                for plan, status in zip(CONTROL_PLANS, self._statuses, strict=True)
            ],
            "tools": tools,
            "messages": messages,
            "steps": steps,
        }

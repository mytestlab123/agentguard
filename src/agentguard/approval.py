"""Exact, expiring, one-time approval state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import secrets

from .contracts import Decision, PolicyDecision, Reason, WafChangeProposal


@dataclass(frozen=True, slots=True)
class ApprovalToken:
    approval_id: str
    proposal_id: str
    proposal_hash: str
    proposal_version: int
    expires_at: datetime


@dataclass(slots=True)
class _ApprovalRecord:
    token: ApprovalToken
    used: bool = False


class ApprovalRegistry:
    """Trusted approval state that is not exposed as an agent tool."""

    def __init__(self) -> None:
        self._records: dict[str, _ApprovalRecord] = {}

    def approve_once(
        self,
        proposal: WafChangeProposal,
        *,
        approval_id: str | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalToken:
        approval_expires_at = expires_at or proposal.expires_at
        if approval_expires_at > proposal.expires_at:
            raise ValueError("approval cannot outlive proposal")
        token = ApprovalToken(
            approval_id=approval_id or secrets.token_urlsafe(24),
            proposal_id=proposal.proposal_id,
            proposal_hash=proposal.proposal_hash,
            proposal_version=proposal.version,
            expires_at=approval_expires_at,
        )
        if token.approval_id in self._records:
            raise ValueError("approval_id already exists")
        self._records[token.approval_id] = _ApprovalRecord(token=token)
        return token

    def reject(self, proposal: WafChangeProposal) -> PolicyDecision:
        return PolicyDecision(Decision.DENY, Reason.HUMAN_REJECTED)

    def consume(
        self,
        token: ApprovalToken,
        proposal: WafChangeProposal,
        *,
        now: datetime,
    ) -> PolicyDecision:
        record = self._records.get(token.approval_id)
        if record is None or record.token != token:
            return PolicyDecision(Decision.DENY, Reason.APPROVAL_UNKNOWN)
        if record.used:
            return PolicyDecision(Decision.DENY, Reason.APPROVAL_REUSED)

        # An authenticated approval authorizes one execution attempt only.
        record.used = True

        if now >= token.expires_at:
            return PolicyDecision(Decision.DENY, Reason.APPROVAL_EXPIRED)
        if (
            token.proposal_id != proposal.proposal_id
            or token.proposal_hash != proposal.proposal_hash
            or token.proposal_version != proposal.version
        ):
            return PolicyDecision(Decision.DENY, Reason.PROPOSAL_MISMATCH)
        return PolicyDecision(Decision.ALLOW, Reason.APPROVAL_VALID)

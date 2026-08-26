"""Fail-closed policy and exact guarded mutation flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import secrets
import re

from .approval import ApprovalRegistry, ApprovalToken
from .contracts import (
    Action,
    AuditEvent,
    Decision,
    MutationResult,
    PolicyDecision,
    Reason,
    Scope,
    WafChangeProposal,
    WafRuleState,
)
from .synthetic_waf import ConfigurationDriftError, SyntheticWafStore


@dataclass(frozen=True, slots=True)
class AllowedMutation:
    target_alias: str
    scope: Scope
    region_alias: str
    rule_name: str


class AgentGuardPolicy:
    """Deterministic authorization policy; the model is not an input."""

    def __init__(self, allowed: AllowedMutation) -> None:
        self.allowed = allowed

    def decide_read(self) -> PolicyDecision:
        return PolicyDecision(Decision.ALLOW, Reason.READ_ONLY_OPERATION)

    def decide_proposal(
        self,
        proposal: WafChangeProposal,
        *,
        now: datetime,
    ) -> PolicyDecision:
        if not self._is_valid_proposal(proposal):
            return PolicyDecision(Decision.DENY, Reason.INVALID_PROPOSAL)
        if now >= proposal.expires_at:
            return PolicyDecision(Decision.DENY, Reason.PROPOSAL_EXPIRED)
        if (
            proposal.target_alias != self.allowed.target_alias
            or proposal.scope != self.allowed.scope
            or proposal.region_alias != self.allowed.region_alias
            or proposal.rule_name != self.allowed.rule_name
        ):
            return PolicyDecision(Decision.DENY, Reason.TARGET_NOT_ALLOWED)
        if (
            proposal.before_action is not Action.COUNT
            or proposal.after_action is not Action.BLOCK
        ):
            return PolicyDecision(Decision.DENY, Reason.ACTION_NOT_ALLOWED)
        return PolicyDecision(
            Decision.APPROVAL_REQUIRED,
            Reason.HUMAN_APPROVAL_REQUIRED,
        )

    @staticmethod
    def _is_valid_proposal(proposal: WafChangeProposal) -> bool:
        safe_name = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
        return (
            isinstance(proposal, WafChangeProposal)
            and isinstance(proposal.version, int)
            and not isinstance(proposal.version, bool)
            and proposal.version == 1
            and all(
                isinstance(value, str) and safe_name.fullmatch(value)
                for value in (
                    proposal.proposal_id,
                    proposal.target_alias,
                    proposal.region_alias,
                    proposal.rule_name,
                )
            )
            and isinstance(proposal.scope, Scope)
            and isinstance(proposal.before_action, Action)
            and isinstance(proposal.after_action, Action)
            and isinstance(proposal.expected_config_hash, str)
            and re.fullmatch(r"[0-9a-f]{64}", proposal.expected_config_hash)
            is not None
            and isinstance(proposal.expected_lock_token, str)
            and 1 <= len(proposal.expected_lock_token) <= 256
            and isinstance(proposal.expires_at, datetime)
            and proposal.expires_at.tzinfo is not None
            and proposal.expires_at.utcoffset() is not None
        )


class GuardedWafMutationService:
    """Execute one exact mutation after policy and human approval gates."""

    def __init__(
        self,
        *,
        policy: AgentGuardPolicy,
        approvals: ApprovalRegistry,
        store: SyntheticWafStore,
    ) -> None:
        self._policy = policy
        self._approvals = approvals
        self._store = store

    def execute(
        self,
        proposal: WafChangeProposal,
        *,
        approval: ApprovalToken | None,
        now: datetime,
        event_id: str | None = None,
    ) -> MutationResult:
        before = self._store.read()
        proposal_decision = self._policy.decide_proposal(proposal, now=now)
        if proposal_decision.decision is Decision.DENY:
            return self._result(
                proposal,
                before,
                before,
                proposal_decision,
                event_id=event_id,
            )
        if approval is None:
            return self._result(
                proposal,
                before,
                before,
                PolicyDecision(Decision.DENY, Reason.HUMAN_APPROVAL_REQUIRED),
                event_id=event_id,
            )

        approval_decision = self._approvals.consume(
            approval,
            proposal,
            now=now,
        )
        if approval_decision.decision is Decision.DENY:
            return self._result(
                proposal,
                before,
                before,
                approval_decision,
                event_id=event_id,
            )

        # Re-read after consuming the one-time approval and immediately before
        # the mutation. Any mismatch requires a fresh proposal and approval.
        before = self._store.read()
        if not self._matches_proposal(before, proposal):
            return self._result(
                proposal,
                before,
                before,
                PolicyDecision(Decision.DENY, Reason.CONFIGURATION_DRIFT),
                event_id=event_id,
            )

        try:
            self._store.update_rule_action(
                expected_lock_token=proposal.expected_lock_token,
                new_action=proposal.after_action,
            )
        except ConfigurationDriftError:
            after = self._store.read()
            return self._result(
                proposal,
                before,
                after,
                PolicyDecision(Decision.DENY, Reason.CONFIGURATION_DRIFT),
                event_id=event_id,
            )

        after = self._store.read()
        verified = (
            after.target_alias == proposal.target_alias
            and after.scope == proposal.scope
            and after.region_alias == proposal.region_alias
            and after.rule_name == proposal.rule_name
            and after.action is proposal.after_action
            and after.revision == before.revision + 1
        )
        if not verified:
            return self._result(
                proposal,
                before,
                after,
                PolicyDecision(Decision.DENY, Reason.VERIFICATION_FAILED),
                mutation_performed=True,
                event_id=event_id,
            )
        return self._result(
            proposal,
            before,
            after,
            PolicyDecision(Decision.ALLOW, Reason.APPROVAL_VALID),
            mutation_performed=True,
            verified=True,
            event_id=event_id,
        )

    @staticmethod
    def _matches_proposal(
        observed: WafRuleState,
        proposal: WafChangeProposal,
    ) -> bool:
        return (
            observed.target_alias == proposal.target_alias
            and observed.scope == proposal.scope
            and observed.region_alias == proposal.region_alias
            and observed.rule_name == proposal.rule_name
            and observed.action is proposal.before_action
            and observed.config_hash == proposal.expected_config_hash
            and observed.lock_token == proposal.expected_lock_token
        )

    @staticmethod
    def _result(
        proposal: WafChangeProposal,
        before: WafRuleState,
        after: WafRuleState,
        policy_decision: PolicyDecision,
        *,
        mutation_performed: bool = False,
        verified: bool = False,
        event_id: str | None = None,
    ) -> MutationResult:
        audit = AuditEvent(
            event_id=event_id or secrets.token_urlsafe(16),
            proposal_id=proposal.proposal_id,
            proposal_hash=(
                proposal.proposal_hash
                if AgentGuardPolicy._is_valid_proposal(proposal)
                else "INVALID_PROPOSAL"
            ),
            decision=policy_decision.decision,
            reason=policy_decision.reason,
            before_action=before.action,
            requested_action=(
                proposal.after_action
                if isinstance(proposal.after_action, Action)
                else before.action
            ),
            after_action=after.action,
            mutation_performed=mutation_performed,
            verified=verified,
        )
        return MutationResult(
            decision=policy_decision.decision,
            reason=policy_decision.reason,
            before=before,
            after=after,
            mutation_performed=mutation_performed,
            verified=verified,
            audit=audit,
        )

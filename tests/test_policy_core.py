from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from agentguard import (
    Action,
    AgentGuardPolicy,
    ApprovalRegistry,
    Decision,
    GuardedWafMutationService,
    Reason,
    Scope,
    SyntheticWafStore,
    WafChangeProposal,
    WafRuleState,
)
from agentguard.guard import AllowedMutation


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


class AgentGuardPolicyCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = WafRuleState(
            target_alias="LAB_WAF_01",
            scope=Scope.REGIONAL,
            region_alias="REGION_01",
            rule_name="LAB_AdminPathProtection",
            action=Action.COUNT,
            lock_token="LOCK_01",
            revision=1,
        )
        self.policy = AgentGuardPolicy(
            AllowedMutation(
                target_alias=self.state.target_alias,
                scope=self.state.scope,
                region_alias=self.state.region_alias,
                rule_name=self.state.rule_name,
            )
        )
        self.approvals = ApprovalRegistry()
        self.store = SyntheticWafStore(self.state)
        self.service = GuardedWafMutationService(
            policy=self.policy,
            approvals=self.approvals,
            store=self.store,
        )
        self.proposal = WafChangeProposal.count_to_block(
            proposal_id="PROPOSAL_01",
            version=1,
            observed=self.state,
            expires_at=NOW + timedelta(minutes=5),
        )

    def test_read_is_allowed_and_mutation_proposal_requires_approval(self) -> None:
        read = self.policy.decide_read()
        proposal = self.policy.decide_proposal(self.proposal, now=NOW)

        self.assertEqual((read.decision, read.reason), (
            Decision.ALLOW,
            Reason.READ_ONLY_OPERATION,
        ))
        self.assertEqual((proposal.decision, proposal.reason), (
            Decision.APPROVAL_REQUIRED,
            Reason.HUMAN_APPROVAL_REQUIRED,
        ))

    def test_approved_exact_proposal_mutates_once_and_verifies(self) -> None:
        approval = self.approvals.approve_once(
            self.proposal,
            approval_id="APPROVAL_01",
        )

        result = self.service.execute(
            self.proposal,
            approval=approval,
            now=NOW,
            event_id="AUDIT_01",
        )

        self.assertEqual(result.decision, Decision.ALLOW)
        self.assertEqual(result.reason, Reason.APPROVAL_VALID)
        self.assertTrue(result.mutation_performed)
        self.assertTrue(result.verified)
        self.assertEqual(result.before.action, Action.COUNT)
        self.assertEqual(result.after.action, Action.BLOCK)
        self.assertEqual(result.audit.event_id, "AUDIT_01")

    def test_bypass_without_approval_is_denied_without_mutation(self) -> None:
        result = self.service.execute(
            self.proposal,
            approval=None,
            now=NOW,
            event_id="AUDIT_02",
        )

        self.assertEqual(result.decision, Decision.DENY)
        self.assertEqual(result.reason, Reason.HUMAN_APPROVAL_REQUIRED)
        self.assertFalse(result.mutation_performed)
        self.assertEqual(self.store.read(), self.state)

    def test_rejected_proposal_has_no_approval_and_no_mutation(self) -> None:
        rejection = self.approvals.reject(self.proposal)
        result = self.service.execute(
            self.proposal,
            approval=None,
            now=NOW,
            event_id="AUDIT_03",
        )

        self.assertEqual(rejection.reason, Reason.HUMAN_REJECTED)
        self.assertEqual(result.decision, Decision.DENY)
        self.assertFalse(result.mutation_performed)
        self.assertEqual(self.store.read(), self.state)

    def test_approval_cannot_be_reused(self) -> None:
        approval = self.approvals.approve_once(
            self.proposal,
            approval_id="APPROVAL_04",
        )
        first = self.service.execute(self.proposal, approval=approval, now=NOW)
        second = self.service.execute(self.proposal, approval=approval, now=NOW)

        self.assertEqual(first.decision, Decision.ALLOW)
        self.assertEqual(second.decision, Decision.DENY)
        self.assertEqual(second.reason, Reason.APPROVAL_REUSED)
        self.assertFalse(second.mutation_performed)

    def test_approval_is_bound_to_exact_proposal_hash(self) -> None:
        approval = self.approvals.approve_once(
            self.proposal,
            approval_id="APPROVAL_05",
        )
        swapped = replace(
            self.proposal,
            expected_config_hash="0" * 64,
        )

        result = self.service.execute(swapped, approval=approval, now=NOW)

        self.assertEqual(result.decision, Decision.DENY)
        self.assertEqual(result.reason, Reason.PROPOSAL_MISMATCH)
        self.assertFalse(result.mutation_performed)
        self.assertNotEqual(self.proposal.proposal_hash, swapped.proposal_hash)

    def test_expired_approval_is_denied_and_consumed(self) -> None:
        approval = self.approvals.approve_once(
            self.proposal,
            approval_id="APPROVAL_06",
            expires_at=NOW + timedelta(seconds=30),
        )

        expired = self.service.execute(
            self.proposal,
            approval=approval,
            now=NOW + timedelta(seconds=30),
        )
        retried = self.service.execute(
            self.proposal,
            approval=approval,
            now=NOW + timedelta(seconds=31),
        )

        self.assertEqual(expired.reason, Reason.APPROVAL_EXPIRED)
        self.assertEqual(retried.reason, Reason.APPROVAL_REUSED)
        self.assertEqual(self.store.read(), self.state)

    def test_runtime_invalid_proposal_is_denied_without_exception(self) -> None:
        invalid = replace(self.proposal, after_action="BLOCK")

        result = self.service.execute(invalid, approval=None, now=NOW)

        self.assertEqual(result.reason, Reason.INVALID_PROPOSAL)
        self.assertFalse(result.mutation_performed)
        self.assertEqual(result.audit.proposal_hash, "INVALID_PROPOSAL")

    def test_configuration_drift_denies_and_consumes_approval(self) -> None:
        approval = self.approvals.approve_once(
            self.proposal,
            approval_id="APPROVAL_07",
        )
        drifted = self.store.force_drift()

        result = self.service.execute(self.proposal, approval=approval, now=NOW)
        retried = self.service.execute(self.proposal, approval=approval, now=NOW)

        self.assertEqual(result.reason, Reason.CONFIGURATION_DRIFT)
        self.assertFalse(result.mutation_performed)
        self.assertEqual(self.store.read(), drifted)
        self.assertEqual(retried.reason, Reason.APPROVAL_REUSED)

    def test_wrong_target_or_action_is_denied_before_approval(self) -> None:
        wrong_target = replace(self.proposal, target_alias="LAB_WAF_02")
        wrong_action = replace(
            self.proposal,
            before_action=Action.BLOCK,
            after_action=Action.COUNT,
        )

        target_decision = self.policy.decide_proposal(wrong_target, now=NOW)
        action_decision = self.policy.decide_proposal(wrong_action, now=NOW)

        self.assertEqual(target_decision.reason, Reason.TARGET_NOT_ALLOWED)
        self.assertEqual(action_decision.reason, Reason.ACTION_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()

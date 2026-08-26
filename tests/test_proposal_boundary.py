from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from agentguard import Action, AgentGuardPolicy, Decision, Reason, Scope, WafRuleState
from agentguard.guard import AllowedMutation
from agentguard.proposal_boundary import (
    IntentBoundaryError,
    IntentBoundaryReason,
    build_proposal_from_agent_intent,
)


NOW = datetime(2026, 8, 27, 2, 0, tzinfo=timezone.utc)


class ProposalBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed = WafRuleState(
            target_alias="LAB_WAF_01",
            scope=Scope.REGIONAL,
            region_alias="REGION_01",
            rule_name="LAB_AdminPathProtection",
            action=Action.COUNT,
            lock_token="SERVER_LOCK_01",
            revision=7,
        )
        self.allowed = AllowedMutation(
            target_alias=self.observed.target_alias,
            scope=self.observed.scope,
            region_alias=self.observed.region_alias,
            rule_name=self.observed.rule_name,
        )
        self.intent = {
            "target": "LAB_WAF_01",
            "rule": "LAB_AdminPathProtection",
            "action": "BLOCK",
        }

    def build(self, payload: object | None = None):
        return build_proposal_from_agent_intent(
            self.intent if payload is None else payload,
            observed=self.observed,
            allowed=self.allowed,
            proposal_id="SERVER_PROPOSAL_01",
            version=1,
            expires_at=NOW + timedelta(minutes=5),
        )

    def test_minimal_intent_builds_trusted_proposal_requiring_approval(self) -> None:
        proposal = self.build()
        decision = AgentGuardPolicy(self.allowed).decide_proposal(
            proposal,
            now=NOW,
        )

        self.assertEqual(proposal.proposal_id, "SERVER_PROPOSAL_01")
        self.assertEqual(proposal.version, 1)
        self.assertEqual(proposal.before_action, Action.COUNT)
        self.assertEqual(proposal.after_action, Action.BLOCK)
        self.assertEqual(proposal.expected_config_hash, self.observed.config_hash)
        self.assertEqual(proposal.expected_lock_token, self.observed.lock_token)
        self.assertEqual(proposal.scope, self.observed.scope)
        self.assertEqual(proposal.region_alias, self.observed.region_alias)
        self.assertEqual(
            (decision.decision, decision.reason),
            (Decision.APPROVAL_REQUIRED, Reason.HUMAN_APPROVAL_REQUIRED),
        )

    def test_authority_injection_fields_fail_closed_without_echo(self) -> None:
        injected_fields = {
            "approved": True,
            "proposal_id": "UNTRUSTED_PROPOSAL",
            "version": 99,
            "expected_config_hash": "UNTRUSTED_HASH",
            "expected_lock_token": "UNTRUSTED_LOCK",
            "expires_at": "2099-01-01T00:00:00Z",
            "before_action": "BLOCK",
            "scope": "CLOUDFRONT",
            "region_alias": "UNTRUSTED_REGION",
            "decision": "ALLOW",
        }

        for field, value in injected_fields.items():
            with self.subTest(field=field):
                payload = dict(self.intent)
                payload[field] = value
                with self.assertRaises(IntentBoundaryError) as raised:
                    self.build(payload)
                self.assertIs(
                    raised.exception.reason,
                    IntentBoundaryReason.INVALID_AGENT_INTENT,
                )
                self.assertEqual(str(raised.exception), "INVALID_AGENT_INTENT")
                self.assertNotIn("UNTRUSTED", str(raised.exception))

    def test_target_rule_and_action_swaps_have_stable_reasons(self) -> None:
        cases = (
            (
                {**self.intent, "target": "LAB_WAF_02"},
                IntentBoundaryReason.TARGET_NOT_ALLOWED,
            ),
            (
                {**self.intent, "rule": "LAB_OtherRule"},
                IntentBoundaryReason.RULE_NOT_ALLOWED,
            ),
            (
                {**self.intent, "action": "COUNT"},
                IntentBoundaryReason.ACTION_NOT_ALLOWED,
            ),
        )

        for payload, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(IntentBoundaryError) as raised:
                    self.build(payload)
                self.assertIs(raised.exception.reason, reason)
                self.assertEqual(str(raised.exception), reason.value)

    def test_missing_extra_and_invalid_fields_fail_closed(self) -> None:
        cases = (
            {"target": "LAB_WAF_01", "rule": "LAB_AdminPathProtection"},
            {**self.intent, "unknown": "DO_NOT_ECHO"},
            {**self.intent, "target": 7},
            {**self.intent, "rule": ""},
            [self.intent],
        )

        for payload in cases:
            with self.subTest(payload_type=type(payload).__name__):
                with self.assertRaises(IntentBoundaryError) as raised:
                    self.build(payload)
                self.assertIs(
                    raised.exception.reason,
                    IntentBoundaryReason.INVALID_AGENT_INTENT,
                )
                self.assertEqual(str(raised.exception), "INVALID_AGENT_INTENT")

    def test_trusted_observed_state_must_be_count_and_allowlisted(self) -> None:
        blocked = replace(self.observed, action=Action.BLOCK)
        swapped = replace(self.observed, target_alias="LAB_WAF_02")

        for observed, reason in (
            (blocked, IntentBoundaryReason.OBSERVED_STATE_NOT_ALLOWED),
            (swapped, IntentBoundaryReason.TARGET_NOT_ALLOWED),
        ):
            with self.subTest(reason=reason):
                with self.assertRaises(IntentBoundaryError) as raised:
                    build_proposal_from_agent_intent(
                        self.intent,
                        observed=observed,
                        allowed=self.allowed,
                        proposal_id="SERVER_PROPOSAL_01",
                        version=1,
                        expires_at=NOW + timedelta(minutes=5),
                    )
                self.assertIs(raised.exception.reason, reason)


if __name__ == "__main__":
    unittest.main()

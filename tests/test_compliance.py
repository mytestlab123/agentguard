from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import unittest

from agentguard.compliance import (
    CONTROL_PLANS,
    ComplianceDemoController,
    CompliancePolicy,
    ControlPlan,
    build_compliance_proposal,
)
from agentguard.contracts import Decision, Reason


NOW = datetime(2026, 8, 27, 0, 0, tzinfo=timezone.utc)


class CompliancePolicyTests(unittest.TestCase):
    def test_exact_two_control_plan_requires_approval(self) -> None:
        proposal = build_compliance_proposal(NOW)

        decision = CompliancePolicy().decide_proposal(proposal, now=NOW)

        self.assertEqual(decision.decision, Decision.APPROVAL_REQUIRED)
        self.assertEqual(decision.reason, Reason.HUMAN_APPROVAL_REQUIRED)
        self.assertEqual(
            [plan.control_id for plan in proposal.controls],
            [
                "S3_BUCKET_SSL_REQUESTS_ONLY",
                "S3_BUCKET_PUBLIC_READ_PROHIBITED",
            ],
        )

    def test_control_or_runbook_substitution_is_denied(self) -> None:
        proposal = build_compliance_proposal(NOW)
        changed = replace(
            proposal,
            controls=(
                CONTROL_PLANS[0],
                ControlPlan(
                    "S3_BUCKET_PUBLIC_READ_PROHIBITED",
                    "ARBITRARY_REMEDIATION",
                ),
            ),
        )

        decision = CompliancePolicy().decide_proposal(changed, now=NOW)

        self.assertEqual(decision.decision, Decision.DENY)
        self.assertEqual(decision.reason, Reason.ACTION_NOT_ALLOWED)

        changed_hash = replace(proposal, expected_state_hash="0" * 64)
        hash_decision = CompliancePolicy().decide_proposal(changed_hash, now=NOW)
        self.assertEqual(hash_decision.decision, Decision.DENY)
        self.assertEqual(hash_decision.reason, Reason.ACTION_NOT_ALLOWED)


class ComplianceControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = ComplianceDemoController(clock=lambda: NOW)

    def test_approval_remediates_and_verifies_both_controls(self) -> None:
        reviewed = self.controller.review()
        approved = self.controller.approve_once()

        self.assertEqual(reviewed["decision"], "APPROVAL_REQUIRED")
        self.assertFalse(reviewed["mutationPerformed"])
        self.assertEqual(
            [finding["actual"] for finding in reviewed["findings"]],
            ["NON_COMPLIANT", "NON_COMPLIANT"],
        )
        self.assertEqual(approved["decision"], "ALLOW")
        self.assertEqual(approved["reason"], "APPROVAL_VALID")
        self.assertEqual(
            [finding["actual"] for finding in approved["findings"]],
            ["COMPLIANT", "COMPLIANT"],
        )
        self.assertTrue(approved["mutationPerformed"])
        self.assertTrue(approved["verified"])
        self.assertEqual(approved["audit"], "RECORDED")

    def test_bypass_denies_with_zero_mutation(self) -> None:
        bypassed = self.controller.bypass()

        self.assertEqual(bypassed["decision"], "DENY")
        self.assertEqual(bypassed["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(bypassed["actualAction"], "2 NON_COMPLIANT")
        self.assertFalse(bypassed["mutationPerformed"])

    def test_approval_is_one_time(self) -> None:
        self.controller.review()
        self.controller.approve_once()

        replayed = self.controller.approve_once()

        self.assertEqual(replayed["decision"], "DENY")
        self.assertEqual(replayed["reason"], "APPROVAL_REUSED")
        self.assertFalse(replayed["mutationPerformed"])


if __name__ == "__main__":
    unittest.main()

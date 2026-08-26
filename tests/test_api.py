from __future__ import annotations

from datetime import datetime, timezone
from http import HTTPStatus
from http.server import ThreadingHTTPServer
import json
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from agentguard.api import DemoActionError, DemoController, make_handler
from agentguard.compliance import ComplianceDemoController
from agentguard.contracts import Action, Scope, WafRuleState
from agentguard.waf_reader import WafReadError


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


class DemoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = DemoController(clock=lambda: NOW)

    def test_review_and_approve_are_backed_by_python_policy(self) -> None:
        reviewed = self.controller.review()
        approved = self.controller.approve_once()

        self.assertEqual(reviewed["decision"], "APPROVAL_REQUIRED")
        self.assertEqual(reviewed["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertFalse(reviewed["mutationPerformed"])
        self.assertEqual(approved["decision"], "ALLOW")
        self.assertEqual(approved["reason"], "APPROVAL_VALID")
        self.assertEqual(approved["actualAction"], "BLOCK")
        self.assertTrue(approved["mutationPerformed"])
        self.assertTrue(approved["verified"])

    def test_direct_approval_replay_is_denied_by_python_registry(self) -> None:
        self.controller.review()
        self.controller.approve_once()

        replayed = self.controller.approve_once()

        self.assertEqual(replayed["decision"], "DENY")
        self.assertEqual(replayed["reason"], "APPROVAL_REUSED")
        self.assertEqual(replayed["actualAction"], "BLOCK")
        self.assertFalse(replayed["mutationPerformed"])

    def test_reject_and_bypass_never_mutate(self) -> None:
        self.controller.review()
        rejected = self.controller.reject()
        bypassed = self.controller.bypass()

        self.assertEqual(rejected["reason"], "HUMAN_REJECTED")
        self.assertEqual(rejected["actualAction"], "COUNT")
        self.assertFalse(rejected["mutationPerformed"])
        self.assertEqual(bypassed["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(bypassed["actualAction"], "COUNT")
        self.assertFalse(bypassed["mutationPerformed"])

    def test_approve_without_review_is_rejected(self) -> None:
        with self.assertRaisesRegex(DemoActionError, "NO_APPROVABLE_PROPOSAL"):
            self.controller.approve_once()


class LiveReadOnlyControllerTests(unittest.TestCase):
    class Reader:
        def __init__(self) -> None:
            self.calls = 0

        def read(self) -> WafRuleState:
            self.calls += 1
            return WafRuleState(
                target_alias="LAB_WAF_01",
                scope=Scope.REGIONAL,
                region_alias="REGION_01",
                rule_name="LAB_AdminPathProtection",
                action=Action.COUNT,
                lock_token="PRIVATE_LOCK_TOKEN",
                revision=1,
            )

    def setUp(self) -> None:
        self.reader = self.Reader()
        self.controller = DemoController(clock=lambda: NOW, live_reader=self.reader)

    def test_live_review_produces_same_proposal_without_mutation(self) -> None:
        reviewed = self.controller.review()

        self.assertEqual(self.reader.calls, 1)
        self.assertEqual(reviewed["environmentLabel"], "LIVE AWS - READ ONLY")
        self.assertTrue(reviewed["liveReadOnly"])
        self.assertEqual(reviewed["decision"], "APPROVAL_REQUIRED")
        self.assertEqual(reviewed["beforeAction"], "COUNT")
        self.assertEqual(reviewed["requestedAction"], "BLOCK")
        self.assertEqual(reviewed["actualAction"], "COUNT")
        self.assertFalse(reviewed["mutationPerformed"])
        self.assertEqual(
            [tool["name"] for tool in reviewed["tools"]],
            ["get_waf_config", "inspect_rule_action", "policy_decision"],
        )

    def test_live_approval_is_disabled_and_bypass_is_denied(self) -> None:
        self.controller.review()
        with self.assertRaisesRegex(DemoActionError, "^LIVE_READ_ONLY$"):
            self.controller.approve_once()

        bypassed = self.controller.bypass()
        self.assertEqual(bypassed["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertFalse(bypassed["mutationPerformed"])
        self.assertFalse(bypassed["verified"])


class LocalHttpContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = DemoController(clock=lambda: NOW)
        cls.server = ThreadingHTTPServer(("localhost", 0), make_handler(cls.controller))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://localhost:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: bytes | None = None,
        human_intent: bool = True,
    ) -> tuple[int, dict]:
        headers = {"Content-Type": "application/json"}
        if human_intent:
            headers["X-AgentGuard-Intent"] = "human-ui-v1"
        request = Request(
            f"{self.base_url}{path}",
            data=payload,
            method=method,
            headers=headers,
        )
        with urlopen(request, timeout=2) as response:
            return response.status, json.load(response)

    def test_health_and_review_routes(self) -> None:
        health_status, health = self.request("/api/health")
        review_status, reviewed = self.request("/api/review", method="POST", payload=b"{}")

        self.assertEqual(health_status, HTTPStatus.OK)
        self.assertEqual(health, {"status": "ok", "mode": "local-synthetic"})
        self.assertEqual(review_status, HTTPStatus.OK)
        self.assertEqual(reviewed["decision"], "APPROVAL_REQUIRED")

    def test_unexpected_input_fails_closed_with_stable_error(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.request("/api/approve", method="POST", payload=b'{"approval":true}')

        self.assertEqual(context.exception.code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(json.load(context.exception), {"error": "UNEXPECTED_FIELDS"})

    def test_post_without_human_ui_intent_is_denied_before_action(self) -> None:
        self.controller.reset()
        self.controller.review()

        with self.assertRaises(HTTPError) as context:
            self.request("/api/approve", method="POST", payload=b"{}", human_intent=False)

        self.assertEqual(context.exception.code, HTTPStatus.FORBIDDEN)
        self.assertEqual(json.load(context.exception), {"error": "HUMAN_UI_INTENT_REQUIRED"})
        self.assertEqual(self.controller.state()["actualAction"], "COUNT")


class LiveHttpErrorContractTests(unittest.TestCase):
    class FailingReader:
        def read(self) -> WafRuleState:
            raise WafReadError("WAF_READ_FAILED")

    def test_raw_aws_failure_returns_only_stable_reason(self) -> None:
        controller = DemoController(clock=lambda: NOW, live_reader=self.FailingReader())
        server = ThreadingHTTPServer(("localhost", 0), make_handler(controller))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        request = Request(
            f"http://localhost:{server.server_port}/api/review",
            data=b"{}",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-AgentGuard-Intent": "human-ui-v1",
            },
        )
        try:
            with self.assertRaises(HTTPError) as context:
                urlopen(request, timeout=2)
            self.assertEqual(context.exception.code, HTTPStatus.BAD_GATEWAY)
            self.assertEqual(json.load(context.exception), {"error": "WAF_READ_FAILED"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


class ComplianceHttpContractTests(unittest.TestCase):
    def test_health_and_review_expose_only_fixed_compliance_story(self) -> None:
        controller = ComplianceDemoController(clock=lambda: NOW)
        server = ThreadingHTTPServer(("localhost", 0), make_handler(controller))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            health_request = Request(
                f"http://localhost:{server.server_port}/api/health"
            )
            with urlopen(health_request, timeout=2) as response:
                health = json.load(response)
            review_request = Request(
                f"http://localhost:{server.server_port}/api/review",
                data=b"{}",
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-AgentGuard-Intent": "human-ui-v1",
                },
            )
            with urlopen(review_request, timeout=2) as response:
                reviewed = json.load(response)

            self.assertEqual(health["mode"], "local-synthetic-compliance")
            self.assertEqual(reviewed["story"], "compliance")
            self.assertEqual(reviewed["target"], "LAB_BUCKET_01")
            self.assertEqual(len(reviewed["findings"]), 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

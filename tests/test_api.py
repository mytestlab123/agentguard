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

from __future__ import annotations

from copy import deepcopy
import unittest

from agentguard import Action, Scope
from agentguard.waf_reader import AwsWafConfig, AwsWafReader, WafReadError


SYNTHETIC_CONFIG = AwsWafConfig(
    region="ap-southeast-1",
    scope=Scope.REGIONAL,
    web_acl_name="PRIVATE_WAF_NAME",
    web_acl_id="PRIVATE_WAF_ID",
    rule_name="PRIVATE_RULE_NAME",
    profile="LOCAL_PROFILE",
)


def count_response() -> dict:
    return {
        "WebACL": {
            "Name": "PRIVATE_WAF_NAME",
            "Id": "PRIVATE_WAF_ID",
            "Rules": [
                {
                    "Name": "PRIVATE_RULE_NAME",
                    "Action": {"Count": {}},
                    "Statement": {"ByteMatchStatement": {}},
                },
                {
                    "Name": "UNRELATED_PRIVATE_RULE",
                    "Action": {"Block": {}},
                },
            ],
        },
        "LockToken": "PRIVATE_LOCK_TOKEN",
    }


class FakeWafClient:
    def __init__(self, response: dict | None = None, error: Exception | None = None) -> None:
        self.response = response or count_response()
        self.error = error
        self.calls: list[dict[str, str]] = []

    def get_web_acl(self, **kwargs: str) -> dict:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return deepcopy(self.response)


class AwsWafReaderTests(unittest.TestCase):
    def test_count_response_maps_to_alias_only_contract(self) -> None:
        client = FakeWafClient()
        reader = AwsWafReader(client, SYNTHETIC_CONFIG)

        observed = reader.read()

        self.assertEqual(
            client.calls,
            [{"Name": "PRIVATE_WAF_NAME", "Scope": "REGIONAL", "Id": "PRIVATE_WAF_ID"}],
        )
        self.assertEqual(observed.target_alias, "LAB_WAF_01")
        self.assertEqual(observed.rule_name, "LAB_AdminPathProtection")
        self.assertEqual(observed.region_alias, "REGION_01")
        self.assertEqual(observed.action, Action.COUNT)
        self.assertNotIn("PRIVATE_WAF", repr(observed))

    def test_missing_ambiguous_and_non_count_rule_fail_closed(self) -> None:
        cases = {
            "missing": ([], "WAF_RULE_NOT_FOUND"),
            "ambiguous": (
                [
                    {"Name": "PRIVATE_RULE_NAME", "Action": {"Count": {}}},
                    {"Name": "PRIVATE_RULE_NAME", "Action": {"Count": {}}},
                ],
                "WAF_RULE_AMBIGUOUS",
            ),
            "block": (
                [{"Name": "PRIVATE_RULE_NAME", "Action": {"Block": {}}}],
                "WAF_RULE_NOT_COUNT",
            ),
            "rule_group": (
                [{"Name": "PRIVATE_RULE_NAME", "OverrideAction": {"Count": {}}}],
                "WAF_RULE_NOT_COUNT",
            ),
        }
        for label, (rules, reason) in cases.items():
            with self.subTest(label=label):
                response = count_response()
                response["WebACL"]["Rules"] = rules
                reader = AwsWafReader(FakeWafClient(response), SYNTHETIC_CONFIG)
                with self.assertRaisesRegex(WafReadError, f"^{reason}$"):
                    reader.read()

    def test_unrelated_returned_target_is_rejected(self) -> None:
        response = count_response()
        response["WebACL"]["Id"] = "OTHER_PRIVATE_WAF_ID"

        with self.assertRaisesRegex(WafReadError, "^WAF_TARGET_MISMATCH$"):
            AwsWafReader(FakeWafClient(response), SYNTHETIC_CONFIG).read()

    def test_sdk_exception_is_sanitized(self) -> None:
        private_detail = "request failed for a private ARN and account"
        reader = AwsWafReader(
            FakeWafClient(error=RuntimeError(private_detail)),
            SYNTHETIC_CONFIG,
        )

        with self.assertRaises(WafReadError) as context:
            reader.read()

        self.assertEqual(str(context.exception), "WAF_READ_FAILED")
        self.assertNotIn(private_detail, str(context.exception))

    def test_runtime_configuration_is_exact_and_fail_closed(self) -> None:
        valid = {
            "AGENTGUARD_AWS_REGION": "ap-southeast-1",
            "AGENTGUARD_WAF_SCOPE": "REGIONAL",
            "AGENTGUARD_WAF_NAME": "PRIVATE_WAF_NAME",
            "AGENTGUARD_WAF_ID": "PRIVATE_WAF_ID",
            "AGENTGUARD_WAF_RULE_NAME": "PRIVATE_RULE_NAME",
            "AGENTGUARD_AWS_PROFILE": "LOCAL_PROFILE",
        }
        self.assertEqual(AwsWafConfig.from_env(valid), SYNTHETIC_CONFIG)

        for label, invalid in {
            "missing": {**valid, "AGENTGUARD_WAF_ID": ""},
            "scope": {**valid, "AGENTGUARD_WAF_SCOPE": "GLOBAL"},
            "cloudfront_region": {
                **valid,
                "AGENTGUARD_WAF_SCOPE": "CLOUDFRONT",
            },
            "unsafe_name": {**valid, "AGENTGUARD_WAF_NAME": "name with spaces"},
        }.items():
            with self.subTest(label=label):
                with self.assertRaises(WafReadError):
                    AwsWafConfig.from_env(invalid)

    def test_reader_has_no_mutation_surface(self) -> None:
        reader = AwsWafReader(FakeWafClient(), SYNTHETIC_CONFIG)

        self.assertEqual(
            [name for name in dir(reader) if not name.startswith("_")],
            ["read"],
        )
        self.assertEqual([name for name in vars(FakeWafClient) if name.startswith("get_")], ["get_web_acl"])


if __name__ == "__main__":
    unittest.main()

"""Read-only AWS WAF adapter with an alias-only output contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
import re
from typing import Any, Protocol

from .contracts import Action, Scope, WafRuleState


TARGET_ALIAS = "LAB_WAF_01"
RULE_ALIAS = "LAB_AdminPathProtection"
REGION_ALIAS = "REGION_01"


class WafReadError(RuntimeError):
    """Stable read failure that never contains raw AWS response details."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class WafReader(Protocol):
    def read(self) -> WafRuleState:
        """Return one sanitized, allowlisted WAF rule state."""


class WafClient(Protocol):
    def get_web_acl(self, *, Name: str, Scope: str, Id: str) -> dict[str, Any]:
        """Match the narrow boto3 WAFv2 client method used by Phase 2."""


@dataclass(frozen=True, slots=True)
class AwsWafConfig:
    region: str
    scope: Scope
    web_acl_name: str
    web_acl_id: str
    rule_name: str
    profile: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> AwsWafConfig:
        values = os.environ if env is None else env
        required = {
            "region": values.get("AGENTGUARD_AWS_REGION", "").strip(),
            "scope": values.get("AGENTGUARD_WAF_SCOPE", "").strip(),
            "web_acl_name": values.get("AGENTGUARD_WAF_NAME", "").strip(),
            "web_acl_id": values.get("AGENTGUARD_WAF_ID", "").strip(),
            "rule_name": values.get("AGENTGUARD_WAF_RULE_NAME", "").strip(),
        }
        if any(not value for value in required.values()):
            raise WafReadError("LIVE_CONFIG_MISSING")
        try:
            scope = Scope(required["scope"])
        except ValueError:
            raise WafReadError("LIVE_CONFIG_INVALID") from None

        profile = values.get("AGENTGUARD_AWS_PROFILE", "").strip() or None
        safe_name = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
        safe_region = re.compile(r"^[a-z0-9-]{3,32}$")
        safe_profile = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
        if (
            safe_region.fullmatch(required["region"]) is None
            or safe_name.fullmatch(required["web_acl_name"]) is None
            or safe_name.fullmatch(required["web_acl_id"]) is None
            or safe_name.fullmatch(required["rule_name"]) is None
            or (profile is not None and safe_profile.fullmatch(profile) is None)
            or (scope is Scope.CLOUDFRONT and required["region"] != "us-east-1")
        ):
            raise WafReadError("LIVE_CONFIG_INVALID")
        return cls(
            region=required["region"],
            scope=scope,
            web_acl_name=required["web_acl_name"],
            web_acl_id=required["web_acl_id"],
            rule_name=required["rule_name"],
            profile=profile,
        )


class AwsWafReader:
    """Read one exact configured WebACL and expose one sanitized COUNT rule."""

    def __init__(self, client: WafClient, config: AwsWafConfig) -> None:
        self._client = client
        self._config = config

    def read(self) -> WafRuleState:
        try:
            response = self._client.get_web_acl(
                Name=self._config.web_acl_name,
                Scope=self._config.scope.value,
                Id=self._config.web_acl_id,
            )
        except Exception:
            raise WafReadError("WAF_READ_FAILED") from None

        if not isinstance(response, Mapping):
            raise WafReadError("WAF_RESPONSE_INVALID")
        web_acl = response.get("WebACL")
        lock_token = response.get("LockToken")
        if not isinstance(web_acl, Mapping) or not isinstance(lock_token, str):
            raise WafReadError("WAF_RESPONSE_INVALID")
        if not lock_token or len(lock_token) > 256:
            raise WafReadError("WAF_RESPONSE_INVALID")
        if (
            web_acl.get("Name") != self._config.web_acl_name
            or web_acl.get("Id") != self._config.web_acl_id
        ):
            raise WafReadError("WAF_TARGET_MISMATCH")

        rules = web_acl.get("Rules")
        if not isinstance(rules, list):
            raise WafReadError("WAF_RESPONSE_INVALID")
        matches = [
            rule
            for rule in rules
            if isinstance(rule, Mapping) and rule.get("Name") == self._config.rule_name
        ]
        if not matches:
            raise WafReadError("WAF_RULE_NOT_FOUND")
        if len(matches) != 1:
            raise WafReadError("WAF_RULE_AMBIGUOUS")

        raw_action = matches[0].get("Action")
        if not isinstance(raw_action, Mapping) or set(raw_action) != {"Count"}:
            raise WafReadError("WAF_RULE_NOT_COUNT")

        return WafRuleState(
            target_alias=TARGET_ALIAS,
            scope=self._config.scope,
            region_alias=REGION_ALIAS,
            rule_name=RULE_ALIAS,
            action=Action.COUNT,
            lock_token=lock_token,
            revision=1,
        )


def build_aws_waf_reader_from_env(
    env: Mapping[str, str] | None = None,
) -> AwsWafReader:
    config = AwsWafConfig.from_env(env)
    try:
        import boto3

        session = boto3.Session(
            profile_name=config.profile,
            region_name=config.region,
        )
        client = session.client("wafv2", region_name=config.region)
    except Exception:
        raise WafReadError("AWS_CLIENT_INIT_FAILED") from None
    return AwsWafReader(client, config)

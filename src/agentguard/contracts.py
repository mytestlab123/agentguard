"""Small immutable contracts shared by policy, approval, and execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any


class Action(StrEnum):
    COUNT = "COUNT"
    BLOCK = "BLOCK"


class Scope(StrEnum):
    REGIONAL = "REGIONAL"
    CLOUDFRONT = "CLOUDFRONT"


class Decision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class Reason(StrEnum):
    READ_ONLY_OPERATION = "READ_ONLY_OPERATION"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    HUMAN_REJECTED = "HUMAN_REJECTED"
    APPROVAL_VALID = "APPROVAL_VALID"
    APPROVAL_UNKNOWN = "APPROVAL_UNKNOWN"
    APPROVAL_REUSED = "APPROVAL_REUSED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    PROPOSAL_EXPIRED = "PROPOSAL_EXPIRED"
    PROPOSAL_MISMATCH = "PROPOSAL_MISMATCH"
    INVALID_PROPOSAL = "INVALID_PROPOSAL"
    TARGET_NOT_ALLOWED = "TARGET_NOT_ALLOWED"
    ACTION_NOT_ALLOWED = "ACTION_NOT_ALLOWED"
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class WafRuleState:
    target_alias: str
    scope: Scope
    region_alias: str
    rule_name: str
    action: Action
    lock_token: str
    revision: int

    @property
    def config_hash(self) -> str:
        return canonical_hash(
            {
                "target_alias": self.target_alias,
                "scope": self.scope.value,
                "region_alias": self.region_alias,
                "rule_name": self.rule_name,
                "action": self.action.value,
                "revision": self.revision,
            }
        )


@dataclass(frozen=True, slots=True)
class WafChangeProposal:
    proposal_id: str
    version: int
    target_alias: str
    scope: Scope
    region_alias: str
    rule_name: str
    before_action: Action
    after_action: Action
    expected_config_hash: str
    expected_lock_token: str
    expires_at: datetime

    @classmethod
    def count_to_block(
        cls,
        *,
        proposal_id: str,
        version: int,
        observed: WafRuleState,
        expires_at: datetime,
    ) -> WafChangeProposal:
        if observed.action is not Action.COUNT:
            raise ValueError("observed rule must be in COUNT mode")
        return cls(
            proposal_id=proposal_id,
            version=version,
            target_alias=observed.target_alias,
            scope=observed.scope,
            region_alias=observed.region_alias,
            rule_name=observed.rule_name,
            before_action=Action.COUNT,
            after_action=Action.BLOCK,
            expected_config_hash=observed.config_hash,
            expected_lock_token=observed.lock_token,
            expires_at=expires_at,
        )

    @property
    def proposal_hash(self) -> str:
        return canonical_hash(
            {
                "proposal_id": self.proposal_id,
                "version": self.version,
                "target_alias": self.target_alias,
                "scope": self.scope.value,
                "region_alias": self.region_alias,
                "rule_name": self.rule_name,
                "before_action": self.before_action.value,
                "after_action": self.after_action.value,
                "expected_config_hash": self.expected_config_hash,
                "expected_lock_token": self.expected_lock_token,
                "expires_at": _utc_iso(self.expires_at),
            }
        )


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    decision: Decision
    reason: Reason


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    proposal_id: str
    proposal_hash: str
    decision: Decision
    reason: Reason
    before_action: Action
    requested_action: Action
    after_action: Action
    mutation_performed: bool
    verified: bool


@dataclass(frozen=True, slots=True)
class MutationResult:
    decision: Decision
    reason: Reason
    before: WafRuleState
    after: WafRuleState
    mutation_performed: bool
    verified: bool
    audit: AuditEvent

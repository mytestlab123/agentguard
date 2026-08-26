"""Convert one minimal untrusted agent intent into a trusted proposal."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .contracts import Action, WafChangeProposal, WafRuleState
from .guard import AllowedMutation


class IntentBoundaryReason(StrEnum):
    """Stable public-safe rejection reasons for the untrusted boundary."""

    INVALID_AGENT_INTENT = "INVALID_AGENT_INTENT"
    TARGET_NOT_ALLOWED = "TARGET_NOT_ALLOWED"
    RULE_NOT_ALLOWED = "RULE_NOT_ALLOWED"
    ACTION_NOT_ALLOWED = "ACTION_NOT_ALLOWED"
    OBSERVED_STATE_NOT_ALLOWED = "OBSERVED_STATE_NOT_ALLOWED"


class IntentBoundaryError(ValueError):
    """Fail closed without retaining or echoing the untrusted payload."""

    def __init__(self, reason: IntentBoundaryReason) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class AgentChangeIntent:
    """The only fields that an untrusted agent is allowed to express."""

    target: str
    rule: str
    action: Action


_INTENT_FIELDS = frozenset({"target", "rule", "action"})


def parse_agent_change_intent(payload: object) -> AgentChangeIntent:
    """Parse an exact JSON-object-shaped intent with no coercion."""

    if type(payload) is not dict or set(payload) != _INTENT_FIELDS:
        raise IntentBoundaryError(IntentBoundaryReason.INVALID_AGENT_INTENT)

    target = payload["target"]
    rule = payload["rule"]
    action = payload["action"]
    if not all(type(value) is str and value for value in (target, rule, action)):
        raise IntentBoundaryError(IntentBoundaryReason.INVALID_AGENT_INTENT)
    if action != Action.BLOCK.value:
        raise IntentBoundaryError(IntentBoundaryReason.ACTION_NOT_ALLOWED)

    return AgentChangeIntent(target=target, rule=rule, action=Action.BLOCK)


def build_proposal_from_agent_intent(
    payload: object,
    *,
    observed: WafRuleState,
    allowed: AllowedMutation,
    proposal_id: str,
    version: int,
    expires_at: datetime,
) -> WafChangeProposal:
    """Build a proposal using untrusted intent plus trusted server inputs."""

    intent = parse_agent_change_intent(payload)
    if not isinstance(observed, WafRuleState) or not isinstance(
        allowed, AllowedMutation
    ):
        raise IntentBoundaryError(IntentBoundaryReason.OBSERVED_STATE_NOT_ALLOWED)
    if (
        intent.target != allowed.target_alias
        or observed.target_alias != allowed.target_alias
        or observed.scope is not allowed.scope
        or observed.region_alias != allowed.region_alias
    ):
        raise IntentBoundaryError(IntentBoundaryReason.TARGET_NOT_ALLOWED)
    if intent.rule != allowed.rule_name or observed.rule_name != allowed.rule_name:
        raise IntentBoundaryError(IntentBoundaryReason.RULE_NOT_ALLOWED)
    if intent.action is not Action.BLOCK:
        raise IntentBoundaryError(IntentBoundaryReason.ACTION_NOT_ALLOWED)
    if observed.action is not Action.COUNT:
        raise IntentBoundaryError(IntentBoundaryReason.OBSERVED_STATE_NOT_ALLOWED)

    return WafChangeProposal.count_to_block(
        proposal_id=proposal_id,
        version=version,
        observed=observed,
        expires_at=expires_at,
    )

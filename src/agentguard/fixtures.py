"""Synthetic v1 lane shared by the CLI demo and local API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .approval import ApprovalRegistry
from .contracts import Action, Scope, WafChangeProposal, WafRuleState
from .guard import AgentGuardPolicy, AllowedMutation, GuardedWafMutationService
from .synthetic_waf import SyntheticWafStore


@dataclass(frozen=True, slots=True)
class SyntheticLane:
    policy: AgentGuardPolicy
    approvals: ApprovalRegistry
    store: SyntheticWafStore
    proposal: WafChangeProposal
    service: GuardedWafMutationService


def build_synthetic_lane(now: datetime) -> SyntheticLane:
    state = WafRuleState(
        target_alias="LAB_WAF_01",
        scope=Scope.REGIONAL,
        region_alias="REGION_01",
        rule_name="LAB_AdminPathProtection",
        action=Action.COUNT,
        lock_token="LOCK_01",
        revision=1,
    )
    policy = AgentGuardPolicy(
        AllowedMutation(
            target_alias=state.target_alias,
            scope=state.scope,
            region_alias=state.region_alias,
            rule_name=state.rule_name,
        )
    )
    approvals = ApprovalRegistry()
    store = SyntheticWafStore(state)
    proposal = WafChangeProposal.count_to_block(
        proposal_id="PROPOSAL_01",
        version=1,
        observed=state,
        expires_at=now + timedelta(minutes=5),
    )
    service = GuardedWafMutationService(
        policy=policy,
        approvals=approvals,
        store=store,
    )
    return SyntheticLane(
        policy=policy,
        approvals=approvals,
        store=store,
        proposal=proposal,
        service=service,
    )

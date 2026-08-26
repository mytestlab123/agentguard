"""Deterministic local proof for the AgentGuard manager-demo sequence."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
import json

from .fixtures import build_synthetic_lane


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)


def _json_default(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"unsupported value: {type(value).__name__}")


def _print(stage: str, payload: object) -> None:
    data = asdict(payload) if hasattr(payload, "__dataclass_fields__") else payload
    print(json.dumps({"stage": stage, "result": data}, default=_json_default))


def main() -> None:
    lane = build_synthetic_lane(NOW)

    _print("READ", lane.policy.decide_read())
    _print("PROPOSE_MUTATION", lane.policy.decide_proposal(lane.proposal, now=NOW))

    approval = lane.approvals.approve_once(lane.proposal, approval_id="APPROVAL_01")
    approved = lane.service.execute(
        lane.proposal,
        approval=approval,
        now=NOW,
        event_id="AUDIT_01",
    )
    _print("APPROVE_ONCE", approved)

    bypass_lane = build_synthetic_lane(NOW)
    bypass = bypass_lane.service.execute(
        bypass_lane.proposal,
        approval=None,
        now=NOW,
        event_id="AUDIT_02",
    )
    _print("BYPASS_APPROVAL", bypass)


if __name__ == "__main__":
    main()

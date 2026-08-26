"""Local synthetic WAF state used for deterministic security proofs."""

from __future__ import annotations

from dataclasses import replace

from .contracts import Action, WafRuleState


class ConfigurationDriftError(RuntimeError):
    pass


class SyntheticWafStore:
    """A narrow stand-in for one future guarded AWS mutation adapter."""

    def __init__(self, initial: WafRuleState) -> None:
        self._state = initial

    def read(self) -> WafRuleState:
        return self._state

    def update_rule_action(
        self,
        *,
        expected_lock_token: str,
        new_action: Action,
    ) -> WafRuleState:
        if self._state.lock_token != expected_lock_token:
            raise ConfigurationDriftError("lock token mismatch")
        self._state = replace(
            self._state,
            action=new_action,
            lock_token=f"LOCK_{self._state.revision + 1:02d}",
            revision=self._state.revision + 1,
        )
        return self._state

    def force_drift(self, *, action: Action | None = None) -> WafRuleState:
        self._state = replace(
            self._state,
            action=action or self._state.action,
            lock_token=f"LOCK_{self._state.revision + 1:02d}",
            revision=self._state.revision + 1,
        )
        return self._state

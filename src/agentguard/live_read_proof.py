"""Repo-owned, alias-only acceptance proof for live AWS read-only mode."""

from __future__ import annotations

from .api import DemoController
from .waf_reader import WafReadError, build_aws_waf_reader_from_env


def main() -> None:
    try:
        controller = DemoController(live_reader=build_aws_waf_reader_from_env())
        reviewed = controller.review()
        bypassed = controller.bypass()
        assert reviewed["environment"] == "live-readonly"
        assert reviewed["target"] == "LAB_WAF_01"
        assert reviewed["rule"] == "LAB_AdminPathProtection"
        assert reviewed["beforeAction"] == "COUNT"
        assert reviewed["requestedAction"] == "BLOCK"
        assert reviewed["actualAction"] == "COUNT"
        assert reviewed["decision"] == "APPROVAL_REQUIRED"
        assert reviewed["reason"] == "HUMAN_APPROVAL_REQUIRED"
        assert reviewed["mutationPerformed"] is False
        assert bypassed["decision"] == "DENY"
        assert bypassed["reason"] == "HUMAN_APPROVAL_REQUIRED"
        assert bypassed["mutationPerformed"] is False
    except WafReadError as error:
        raise SystemExit(error.reason) from None
    except Exception:
        raise SystemExit("LIVE_READ_PROOF_FAILED") from None

    print("LIVE_READ_PROOF_OK")
    print("environment=LIVE AWS - READ ONLY")
    print("target=LAB_WAF_01")
    print("rule=LAB_AdminPathProtection")
    print("proposal=COUNT -> BLOCK")
    print("decision=APPROVAL REQUIRED")
    print("mutation=NO")
    print("bypass=DENY HUMAN_APPROVAL_REQUIRED")


if __name__ == "__main__":
    main()

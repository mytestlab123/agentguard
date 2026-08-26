# Tests

Future deterministic checks and retained synthetic security regressions belong
here. Do not remove a meaningful failing case merely to make a report green.

Run the canonical local checks from the repository root:

```bash
./scripts/check.sh
```

`test_policy_core.py` protects the v1 authorization boundary: read allow,
approval requirement, exact approved mutation, rejection, bypass denial,
proposal binding, approval expiry/replay, runtime validation, and drift denial.

`test_api.py` proves that the local controller uses the Python policy core,
direct approval replay is denied, rejection/bypass do not mutate, fixed HTTP
routes work, unexpected input fails closed, and human-UI intent is required.

`test_waf_reader.py` proves that a mocked `GetWebACL` response maps only to
aliases, exact target/rule selection is enforced, missing/ambiguous/non-COUNT
states fail closed, SDK errors are sanitized, runtime configuration is exact,
and the live reader has no mutation surface.

The frontend API-client test protects the fixed action-to-route allowlist and
generic browser error boundary. Authorization transition tests live in Python
only so there is one policy authority.

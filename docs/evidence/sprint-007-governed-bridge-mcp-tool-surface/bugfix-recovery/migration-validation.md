# Migration validation

| Check | Result |
| --- | --- |
| Migration file present in working `main` | PASS |
| Migration file present at `7d361103023041ea9232d3d07375cf4fb7bf80fd` | PASS |
| Local `showmigrations projects` | `[ ] 0005_governed_mcp_records` |
| Staging `showmigrations projects` | NOT RUN — deployment access unavailable |

The local result confirms that migration state must be checked, not inferred
from the source tree. It does not establish staging state. The operator proof
required for this recovery is recorded in `STAGING_DEPLOYMENT_RUNBOOK.md`.

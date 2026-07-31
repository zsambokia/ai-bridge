# Engineering Acceptance — Sprint 7

Date: 2026-07-31

## Implemented capability

- Durable technical incident, ownership, evidence, child-scope, checkpoint,
  validation, and audit chain.
- Independent gate validation before exact original-run/job resume.
- Worker safety path for unclassified exceptions: release the leased job and
  persist a visible remediation state instead of silently stopping.
- Bounded remediation limit with an explicit, auditable recovery state.
- Separate durable business-decision escalation; technical defects do not use
  this route.
- Read-only Admin and MCP projection of remediation, validation, and business
  escalation state.

## Validation

The final source validation suite was run with `DJANGO_SETTINGS_MODULE` set to
`bridge.settings.test`:

```text
pytest -q                                      PASS — 240 passed (20.68s)
ruff check .                                   PASS
mypy .                                         PASS — 161 source files
python manage.py check                         PASS
python manage.py makemigrations --check --dry-run  PASS
python manage.py validate_scopes               PASS
git diff --check                               PASS
```

Targeted lifecycle/worker/MCP regression before the full suite:

```text
pytest projects/tests/test_execution.py \
  projects/tests/test_technical_remediation.py \
  projects/tests/test_governed_mcp.py -q       PASS — 59 passed
```

`test_worker_unhandled_non_provisioning_failure_requires_repair_then_resumes`
proves the worker cannot leave a generic failed execution leased or QUIET: it
creates a persisted repair loop, releases the job, requires passing
independent validation, and resumes the same run/job.


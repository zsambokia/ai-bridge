# R20-00 Runtime 2.0 Compliance Baseline — Closure Report

## Sprint closure

**PASS — READY FOR PRODUCT OWNER REVIEW**

The approved read-only audit scope was executed at baseline
`8f23f0bad865d676258b3d48895894159f402687`. It generated every required
baseline artifact and passed all required repository release gates:

- `pytest -q`: 386 passed in 158.61 s
- `ruff check .`: PASS
- `mypy .`: PASS (260 source files)
- `python manage.py validate_scopes`: PASS

Supplementary checks also passed: `ruff format --check .`, `git diff --check`,
and the 10-test targeted Runtime set.

## Audited system result

**Runtime 2.0 Constitution compliance: FAIL.**

The failure is the audited result, not an incomplete audit. The current Factory
Chat path invokes a Workflow adapter/provider lambda directly. It bypasses the
required durable immutable Execution Request, MSM authorization, authorized
Operational Work Item, and Operational Foundation queue/claim path. Existing
`ExecutionRun` and `ExecutionJob` are reusable mechanics but are not the
constitutional route for this ingress. See `GAP_REGISTER.md` and
`ARCHITECTURE_MAP.md`.

## Scope and safety confirmation

No application, runtime authority, database schema, queue, worker, provider,
or deployment change was made. The pre-existing `bridge/settings/local.py`
modification was preserved. The evidence, AKB, roadmap, canonical scope, and
program documents are the only Sprint work products.

## Next governed action

Product Owner review of this evidence package, followed by a separately
approved R20-01 scope for MSM and Mission Resolution. R20-02 may then map
authorized work to the existing `ExecutionRun`/`ExecutionJob` lifecycle and
migrate Factory Chat without creating a parallel queue or worker.

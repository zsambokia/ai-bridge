# Sprint 5 remediation log

## 2026-07-31 — targeted-test fixture repair

**Detection:** the initial `projects/tests/test_runtime_deployment.py` run
failed before exercising deployment behaviour because the fixture referred to
`ExecutionContract.Status.CONSUMED`.

**Diagnosis:** `ExecutionContract` exposes the state enum as `Lifecycle`, not
`Status`; production lifecycle behaviour was not implicated.

**Repair:** changed the fixture to `ExecutionContract.Lifecycle.CONSUMED`.

**Regression:** the corrected targeted deployment tests passed, Ruff passed,
and `makemigrations --check --dry-run` reported no model drift.

Further runtime fault-injection attempts, if any, are retained below rather
than rewritten out of the record.

## 2026-07-31 — isolated runtime bootstrap repair

**Detection:** the first isolated Django runtime process started, but its
`/health/` probe returned HTTP 400 rather than a health document.

**Diagnosis:** the server log reported `Invalid HTTP_HOST header` for
`127.0.0.1:8125`. The explicit local-runtime environment omitted
`DJANGO_ALLOWED_HOSTS`; the application source and migration state were not at
fault.

**Repair:** stopped only the isolated listener on port 8125 and restarted it
with the supported local configuration
`DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`.

**Regression:** the restarted runtime returned HTTP 200 and reported the
immutable Sprint 5 implementation SHA in its health document.

## 2026-07-31 — controlled runtime SHA mismatch

**Detection:** `verify_runtime_deployment` was deliberately invoked against
the live runtime with an all-zero expected SHA.

**Result:** the verifier returned a structured `FAIL` result and the exact
`RUNTIME_BUILD_SHA_MISMATCH` diagnostic while migration, dependency, worker
and scheduler checks remained `PASS`.

**Recovery:** reran the verifier with the actual immutable implementation SHA
`88e94f1a107e38358638da84a090f4a64a6251fd`; every check returned `PASS`.

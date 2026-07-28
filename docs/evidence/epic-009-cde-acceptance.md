# EPIC #9 — Sprint C–E acceptance evidence

The remediation workflow has no LLM SDK dependency and imports only the existing
provider-neutral executor selector. It cannot create a Scope, Execution Contract,
or approval: each is supplied from the canonical governance lifecycle.

- Sprint C requires ownership policy `ALLOW`, a consumed contract, and its exact
  scope-bound execution approval before dispatch, cancellation, or timeout.
- Sprint D requires independent validator evidence; pass resumes, technical
  failure requires a new contract, and business-risk failure escalates.
- Sprint E has no implicit deployment adapter; deployment and rollback each need
  their own durable authority, and rollback also requires a deployment.

## Integrated closure evidence

The final implementation consolidates cancellation in the existing canonical
executor boundary. Remediation dispatch records a durable audit event and passes
that audit binding to the existing executor; it does not invoke a provider SDK
or create a second dispatch path.

The full integrated checks passed on the final working tree:

- `python -m scripts.release_gate` — PASS (Django check, 116 tests, Ruff,
  formatting, and MyPy).
- `python manage.py validate_scopes` — PASS.
- `python manage.py makemigrations --check --dry-run` — PASS (no changes).
- direct dependency scan of `projects/orchestrator.py`,
  `projects/orchestrator_providers.py`, and `projects/remediation.py` — no
  OpenAI SDK import or client construction.

The acceptance tests cover contract linking, executor/audit dispatch linkage,
timeout without replacement dispatch, independent validation and resume/retry,
and separately authorized deployment and rollback.

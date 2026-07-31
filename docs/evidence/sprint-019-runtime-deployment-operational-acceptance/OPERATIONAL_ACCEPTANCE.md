# Sprint 5 operational acceptance — live-runtime record

## Evidence boundary

This evidence distinguishes real local runtime actions from seeded projection
fixtures. The live runtime is an isolated worktree and SQLite database; it is
not a production environment and does not assert a remote deployment.

## Initial deployed implementation

- Immutable implementation revision:
  `88e94f1a107e38358638da84a090f4a64a6251fd`
- Runtime worktree: `.sprint5-operational-runtime`
- Runtime database: `.sprint5-operational-runtime/runtime.sqlite3`
- Public local endpoint: `http://127.0.0.1:8125/health/`

The live health document returned HTTP 200 and exactly reported the immutable
implementation revision above. It also identified its isolated runtime
database; it does not infer the revision from the checkout at request time.

`verify_runtime_deployment` against that endpoint passed health identity,
migration plan, dependency integrity, one worker reconciliation pass and one
scheduler/reconciler pass. The recorded worker and scheduler result was a
healthy empty queue/workspace state, not a fabricated completed execution.

## Fault injection and recovery

The retained remediation log records both the first failed health probe caused
by omitted local allowed-host configuration and the controlled SHA-mismatch
verification failure. The latter produced the precise mismatch diagnostic and
recovered only when rerun with the actual implementation SHA.

## Admin and MCP canonical projection

A local-only fixture created one `RuntimeDeployment` receipt for an already
verified delivery. This is explicitly a **seeded projection fixture**, used to
prove that authenticated HTTP Admin and authenticated HTTP MCP read the same
canonical record; it is not represented as an independently executed external
delivery.

- Admin detail HTTP response: 200, showing deployment `1`, the implementation
  SHA and `DEPLOYED` status.
- MCP `deployment.get_status` HTTP response: 200, showing the same deployment
  `1`, SHA, canonical status, verification sub-results, receipt and rollback
  target `c25c91d3b3d2a634a4b1cbf80b624de43d92e874`.

The subsequent forward-deployment, rollback and final-state checks are added
to this record before Sprint closure.

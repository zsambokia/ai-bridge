# Governed Incremental Implementation Roadmap

This roadmap is direction only. Each item needs its own approved Sprint/Work
Item and Execution Contract; no item is authorized by this audit.

1. **Projection contracts audit.** Define read-only Workspace DTOs for Home,
   Orki, Execution, Knowledge and Repository, with source IDs/hashes and
   authorization checks. Acceptance: contract tests and no direct UI AKB access.
2. **Home and Orki shell.** Reframe Factory Chat as Orki and add read-only Home
   navigation/projections. Acceptance: existing Factory Chat acceptance and
   accessibility/browser evidence remain green.
3. **Execution/Runtime projection.** Present OESM, events, waits, evidence and
   recovery as server projections. Acceptance: state-transition and SSE tests.
4. **Knowledge and Context Package projection.** Show package members,
   selection rationale, provenance, freshness and review status. Acceptance:
   pipeline/semantic isolation tests and explicit package-to-execution contract.
5. **Repository projection.** Show bootstrap/import/incremental-sync readiness
   and receipts. Acceptance: lifecycle convergence and incremental-sync proof.
6. **Decisions, Roadmap and Workflows.** Add governed read views over existing
   records. Acceptance: no new approval/execution path.
7. **Administration/Evidence and operational hardening.** Link evidence and
   admin safely; perform release and runtime acceptance in a separately
   authorized release scope.

Every Sprint must explicitly assess reuse, migration of the Factory Chat,
release gates, documentation and evidence. Meetings and temporal memory remain
separate product-scope decisions until an owner and data contract are approved.

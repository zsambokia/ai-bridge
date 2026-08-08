# Governance compatibility report

Runtime invokes existing `factory_planning.create_plan` and existing `approve_plan`; it does not alter their data or authority. `observe_factory_plan_approval` accepts an already-issued, non-revoked `GovernanceApproval` and records its reference only.

No Runtime code creates or mutates `ExecutableScope`, `GovernanceApproval`, `ExecutionContract`, or published scope projections. In Shadow Mode the recorded handoff is explicitly `shadow_only`. Existing plan-approval tests plus the Runtime approval test passed.

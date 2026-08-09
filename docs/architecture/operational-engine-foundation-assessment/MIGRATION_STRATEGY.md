# Migration strategy

No phase changes the current Runtime Foundation until its stated PASS evidence exists. Each phase is independently reversible by routing new work back to the current Runtime path.

| Phase | Change boundary | PASS evidence |
| --- | --- | --- |
| 0. Baseline | document current ownership, state machines and coupling | this audit accepted; no behaviour changed |
| 1. Ports | introduce internal ports for provider, context, evidence and engine work without extraction | existing Runtime and chat E2E behaviour unchanged; port contract tests pass |
| 2. Planning Session | persist PSM session/receipts and route only new planning requests through it | three multi-turn critical-unknown E2E cases prove Planning cannot begin early |
| 3. Workflow boundary | route task execution through ExecutionRun and Provider Gateway; remove chat/provider logic from Workflow domain | retries, leases, cancellation and recovery evidence pass |
| 4. Durable queue | add claim/idempotency/outbox/reconciliation for engine work | restart and duplicate-delivery acceptance evidence pass |
| 5. Knowledge/Repository engines | extract receipts behind their ports | context freshness and repository bootstrap acceptance pass |
| 6. Reflection/Learning | add governed reflection and promotion flows | no learning reaches canonical knowledge without approval/evidence |
| 7. Optional event delivery | add bus consumers while retaining polling/reconciliation | event loss/duplicate/replay test suite passes |

## Migration constraints

* Do not migrate database ownership by copying mutable state between engines.
* Use dual-read/projection comparison before changing an authoritative owner.
* Every cutover has feature-gated routing, evidence comparison and a documented rollback.
* Existing user-facing chat remains a work journal during all phases.

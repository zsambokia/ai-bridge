# Runtime 2.0 Phase 1 — Factory Development Mode execution record

## Authority and scope

- **Authority:** explicit Product Owner Factory Development Mode authorization
  in the active instruction, 2026-08-09.
- **Authorized scope:** Runtime 2.0 Phase 1 Architecture Convergence &
  Baseline Sprint. Converge existing Runtime components into one Phase 1
  baseline; do not create parallel Runtime, Engine, Queue, Worker, Scheduler,
  Retry, Lifecycle, Planning, Workflow, or Conversation systems.
- **Normal managed-execution exceptions:** a Bridge-issued Execution Contract,
  managed provider execution, provider heartbeat, and running managed execution
  are explicitly not prerequisites for this Factory Development Mode work.
- **Exact Sprint source:** Product Owner supplied Phase 1 Sprint 1 / Sprint 2
  specification, SHA-256
  `fb6acedebccb4996ddca4985a2a074838381eaa54e96194d479d0217edbf9078`.
- **Convergence authority:** Product Owner supplied Runtime 2.0 Phase 1
  Architecture Convergence & Baseline Sprint directive, active instruction.

## Binding context read before mutation

1. `AGENTS.md`
2. `docs/runtime/runtime_2_0_constitution.md`
3. `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
4. Product Owner supplied Phase 1 Sprint 1 / Sprint 2 specification
5. `docs/constitution/BRIDGE_CONSTITUTION.md`
6. `docs/roadmap/ROADMAP.md`
7. `docs/akb/CURRENT_STATE.md`

The Runtime 2.0 Constitution is the target architecture. The historical
Sprint 1 and Sprint 2 requirements remain the detailed acceptance criteria;
the Product Owner's convergence directive resolves their implementation
strategy: extend and migrate canonical components rather than add a competing
runtime path.

## Repository preflight

- **Repository:** `zsambokia/ai-bridge`
- **Branch:** `main` (main-only policy applies)
- **Baseline commit:** `43ebb3e638d855abc53a5dc22fb4013e6da1b237`
- **Baseline time:** 2026-08-09 Europe/Budapest
- **Other active worktrees:**
  - `C:/Users/User/Documents/dev/ai-bridge-factory-lifecycle` at `af4800b`
  - `C:/Users/User/Documents/dev/ai-bridge-governed-cancellation` at `43e5b75`
- **Merge/rebase/conflict state:** none reported by Git preflight.

## Existing local work at the baseline

The working tree was already non-clean. Nothing is reset, cleaned, restored,
or staged by this Sprint. `bridge/settings/local.py` and
`docs/akb/CURRENT_STATE.md` are preserved as unrelated or ambiguous local
work. The Runtime-related changes below are assessed in place as the current
in-progress Phase 1 implementation and may be repaired only where necessary
for the authorized convergence scope:

- `projects/factory_chat.py`, `projects/factory_orki.py`,
  `projects/orki_runtime.py`, `projects/workflow_engine.py`
- `projects/models.py`, migration `0066`, and the untracked migration `0067`
- `projects/operational_foundation.py`, `projects/provider_gateway.py`
- their focused tests and the untracked Runtime/evidence directories

## Current checkpoint

- **Completed:** authority validation, binding-context review, repository and
  worktree preflight, architecture inventory, removal of the parallel
  OperationalWorkItem/OperationalWorkEvent model and lifecycle, the first
  Provider Gateway import-boundary repair (including removal of its reverse
  Conversation/Mission imports), and Conversation ingress migration
  to the existing `factory_missions` module. The latter includes message,
  approval, manual-plan, and repository-lifecycle endpoint delegation; a
  synchronous dispatch failure retains the durable execution record for safe
  projection. The initial acceptance audit is in `COMPLIANCE_AUDIT.md`.
- **In progress:** migration from Conversation-owned execution and split
  mission/planning authority to the required MSM and Foundation boundaries.
- **Next action:** complete the MSM-to-Foundation handoff using existing
  durable Runtime components, then remove the remaining Gateway-to-Conversation
  dependency and migrate Runtime/Workflow work from synchronous dispatch to
  the canonical queue and execution-run path.
- **Validation status:** focused Ruff, `git diff --check`, and 43 focused
  Conversation/Mission/Foundation Django tests pass after the latest migration.
  Phase 1 acceptance is explicitly FAIL until all audit rows and
  repository-wide gates pass.

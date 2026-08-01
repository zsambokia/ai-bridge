# AI Bridge Roadmap

## Factory Readiness Remediation — Sprint 8

**Status:** `FINAL AUDIT COMPLETE — EPIC OPEN FOR EXTERNAL PLATFORM CERTIFICATION`.

Sprint 8 records the final Factory Readiness Dossier at
`docs/evidence/factory-readiness-dossier-20260801/`. The evidence-backed
reassessment moves the complete-chain maturity baseline from **40/100** to
**82/100**, while deliberately retaining the ChatGPT Business UI/Remote MCP
proof as an unverified external-platform boundary. AI Bridge-owned lifecycle,
Orki, knowledge, delivery, deployment and remediation evidence is classified
separately from that missing proof. Sprint 6 remains non-PASS and unchanged;
Issue #15 cannot claim final autonomous-factory readiness until the separate
ChatGPT Business Platform Certification Epic records the genuine UI-originated
chain.

## Factory Readiness Remediation — Sprint 7

**Status:** `PASS — ACCEPTED` (Product Owner Engineering and Operational
Acceptance accepted).

Sprint 7 makes routine technical recovery a persisted, bounded and resumable
factory capability. An unexpected non-provisioning worker fault now becomes an
incident with evidence, Orki ownership, a bounded child remediation scope and
an exact run checkpoint; it cannot leave a leased job quiet in an intermediate
state. Independent invalidated-gate validation is required before the original
job and checkpoint resume. A real business choice has a separate concise,
durable escalation. Admin and MCP project the canonical same state. Evidence:
`docs/evidence/sprint-021-autonomous-technical-remediation-self-healing/`.

Sprint 6 remains externally blocked for the final ChatGPT Business in-app
Remote MCP proof and is deliberately unchanged. The separate ChatGPT Business
Platform Certification Epic owns that external dependency.

## Factory Readiness Remediation — Sprint 5

**Status:** `PASS — ACCEPTED` (Product Owner Engineering and Operational
Acceptance accepted).

Sprint 5 closes the runtime-activation gap left intentionally separate from
repository delivery. A verified delivery now has a SHA-bound deployment plan
and receipt, including target identity, authority, migrations, dependencies,
runtime health, worker/scheduler supervision, remediation history and a safe
rollback target. Admin and MCP read the same deployment projection; no
verification command can manufacture a deployment claim. The release gates,
isolated live runtime verification, controlled mismatch repair and safe
forward/rollback exercise are recorded in
`docs/evidence/sprint-019-runtime-deployment-operational-acceptance/`.

Sprint 4 has Product Owner acceptance and is the prerequisite delivery
boundary for this Sprint.

## Factory Readiness Remediation — Sprint 4

**Status:** `PASS — ACCEPTED` (Product Owner Operational and Engineering
Acceptance accepted).

Sprint 4 closes the autonomous repository-delivery gap. Contract-bound policy
now verifies a clean scoped workspace, passing gates and SHA-bound evidence,
publishes through a normal non-force push, verifies the remote SHA, and
persists one delivery projection for Admin/API/MCP. Remote movement becomes a
durable reconciliation outcome rather than an overwrite. The evidence is in
`docs/evidence/sprint-018-autonomous-repository-delivery/`.

Sprint 3 has Product Owner acceptance. Its durable context and approved
roadmap lifecycle remain the prerequisite for Sprint 4 delivery policy.

## Factory Readiness Remediation — Sprint 3

**Status:** `PASS — ACCEPTED` (Product Owner Operational and Engineering
Acceptance accepted).

Sprint 3 closes the durable AKB/roadmap feedback-loop gap. Governed retrieval
now has a persisted context package and consumption chain through Orki,
contracts, and queued runs. Retrieval is deterministic and project-isolated,
with explicit source-version, stale, and conflict data. Canonical roadmap
changes are review-controlled candidates, not side effects of evidence arrival;
only an approved candidate can update a project roadmap item. Completion is
guarded by engineering and operational PASS, evidence references, and an exact
commit SHA.

## Maturity baseline — 2026-07-31

The independent [Factory Readiness Audit](../evidence/factory-readiness-audit-20260731/FACTORY_READINESS_AUDIT.md)
records **NOT READY** at **40/100** maturity, with an estimated **55%**
non-governance human-intervention dependency and **4.3/10** AKB maturity. This
is a corrective baseline, not a claim of operational readiness and not an
execution authorization.

### EPIC — Canonical Execution Lifecycle Integrity and Autonomous Recovery

**Purpose:** make the canonical lifecycle deterministically reconcile, recover,
retry, and terminalize without routine Product Owner/operator intervention. It
must resolve stale jobs, expired leases, dead provider PIDs, orphaned
workspaces, missing checkpoints, and state divergence; protect against
duplicates; preserve worker survival; provide consistent admin/MCP
observability; and prove recovery through fault injection and real governed
end-to-end delivery/acceptance evidence.

Sprint 016, [Canonical Execution Lifecycle Integrity and Autonomous
Recovery](../sprints/SPRINT_016_CANONICAL_EXECUTION_LIFECYCLE_INTEGRITY_AND_AUTONOMOUS_RECOVERY.md),
is implemented under Product Owner Factory Development Mode, independently
repository-audited, and has isolated-runtime Operational Acceptance evidence at
the repaired revision `546bde6a66eaf645ddc0f3e047b5ed5c238f4847`; see
[Operational Acceptance](../evidence/sprint-016-canonical-execution-lifecycle-integrity-and-autonomous-recovery/OPERATIONAL_ACCEPTANCE_2026-07-31.md).
Its recovery invariants are documented in [Canonical execution lifecycle recovery](../architecture/EXECUTION_LIFECYCLE_RECOVERY.md).

### Sprint 2 â€” Orki as the Mandatory Orchestration Gate

Sprint 2 is the completed bounded Factory Readiness remediation.  It makes the
normal ChatGPT-facing MCP confirmation path durable and fail-closed through an
`OrchestrationSession`, ownership assessment, governed context package and
decision binding before a contract or run exists.  It deliberately preserves
separate recovery/bootstrap classifications rather than treating them as
normal-request evidence.  The design and final acceptance evidence are in
[Orki mandatory orchestration gate](../architecture/ORKI_MANDATORY_ORCHESTRATION_GATE.md)
and `docs/evidence/sprint-017-orki-mandatory-orchestration-gate/`.

Engineering and isolated-runtime Operational Acceptance are recorded at the
final implementation revision `4b8f59f19f8f215993811973f88d4f71374e08b7`.
Sprint 2 is accepted; later Sprint evidence is retained in its own historical
package and does not alter this Sprint 2 record.

### Sprint 6 confirmation-binding remediation (engineering PASS; deployment/UI proof pending)

The Sprint 6 ChatGPT Business proof remains incomplete, but a real Product
Owner confirmation exposed two defects before a canonical approval could be
persisted: the normalized Hungarian phrase was absent from the explicit
allow-list, and the Remote MCP adapter did not carry a durable,
server-issued conversation binding from review to confirmation. The repair
uses a caller-bound signed MCP session and a durable exact
scope/version/hash binding, while retaining server-derived caller,
approval-reference, and idempotency protections. Negative and conditional
confirmation text remains fail-closed. Local regression evidence is retained
in `docs/evidence/sprint-020-chatgpt-factory-e2e/`. This source revision has
not yet been deployed to staging; deployment process identity and a fresh
actual ChatGPT Business UI proposal/approval remain mandatory Operational
Acceptance evidence.

**Status:** ACTIVE PROJECT ROADMAP  
**Scope:** AI Bridge project  
**Execution authority:** this roadmap remains directional; the bounded Sprint
016 Factory Development Mode instruction is the implementation authority
**Project definition:** `.bridge/project.yaml`

## 1. Product direction

AI Bridge is being built as a generic, governed AI software factory platform capable of onboarding, understanding, developing, testing, documenting, and proving complete software changes across both new and existing Projects.

The platform must remain Project-agnostic. Project-specific repository identity, paths, technology profile, Release Gates, and operational settings belong in Project configuration and Project Context, while the execution rules remain generic.

The near-term objective is to prove that the platform can take one registered Project through a complete, evidence-backed implementation cycle without relying on hidden chat context, manually assembled prompts, or Project-specific branches in the execution engine.

## 2. Roadmap principles

- The roadmap defines direction, sequencing, and dependencies.
- The roadmap does not authorize Codex execution.
- Every implementation must be defined by one explicitly approved Sprint.
- Platform capabilities must be generic unless they are explicitly Project configuration.
- New and existing Projects must use the same onboarding and execution machinery.
- Evidence, Release Gates, and Product Owner Review are mandatory completion conditions.
- Capability completion must be based on accepted evidence, not optimistic status labels.
- Bridge must automatically repair routine technical failures and rerun invalidated gates without Product Owner intervention.
- Product Owner involvement is reserved for business, product, legal, brand, material UX, destructive production-risk, credential, permission, and unresolved constitutional decisions.

## 3. Configuration and operational state boundary

AI Bridge must maintain a strict separation between relatively stable Project configuration and frequently changing operational state.

### 3.1 Static Project definition

Canonical repository-local location:

```text
.bridge/project.yaml
```

This file contains relatively stable Project-specific configuration, including:

- Project identity;
- repository identity;
- default and integration branches;
- governance and workflow paths;
- Sprint, architecture, roadmap, AKB, and evidence roots;
- technology profile;
- repository-wide Release Gates;
- repository policies and static supported-feature configuration.

It must not become a live status store.

### 3.2 Dynamic Project state

Frequently changing state belongs in the operational database and Project Context, including:

- selected Project;
- observed branch and commit;
- active Sprint and pull request;
- validation status;
- refresh timestamps;
- context snapshots;
- state events;
- accepted capability state;
- next safe action.

A separate repository-local status file may be introduced only if a later approved Sprint proves a concrete need for a durable, reviewable status projection. It must be generated from structured state, never edited as a competing source of truth.

Sprint 003 establishes this boundary for Project lifecycle, onboarding, and Context state. A later operational-capability Sprint may add a structured capability-state model; it must remain separate from the static definition.

## 4. Milestone sequence

### Sprint 2 — AKB readiness advancement

Implemented under the approved AKB knowledge-platform Sprint 2: a normalized,
project-isolated engineering-memory layer with versioned entities, typed
relations, approval-controlled publication, lifecycle-event candidates, and
first-class Roadmap, Constitution, UI Plan, and System Design MCP adapters.
Deployment and rollback ingestion remain deferred because the present
deployment lifecycle does not emit those events.

### Sprint 014 — Execution provider platform and secure configuration

Implemented under its approved Sprint: a provider-neutral registry, safe
read-only MCP provider discovery, role/capability validation, non-secret
credential references, provider audit events, and exact contract-bound Codex
execution selection. Remote providers require separately configured external
credentials and are not treated as available merely because a record exists.

### Sprint 015 — Real-time DEV execution activity and checklist

Implemented under its approved governed Sprint: a secret-safe live activity
projection over the existing execution event stream, a derived checklist, a
read-only operational admin view, and a compact MCP activity summary for
ChatGPT. This strengthens the proving loop without adding a parallel lifecycle
or simulated organizational actors.

### Provider activity fidelity repair

The Codex provider activity stream now treats each stdout and stderr line as
untrusted input: valid object events are projected to typed, redacted evidence,
while JSON scalars and malformed lines remain safe text output.  A projection
failure is isolated to that line so the reader and worker continue processing
subsequent activity.

### Issue #11 Sprint A â€” Durable queue and worker separation

Sprint A implements the first ordered child of the Durable Autonomous
Execution Epic. A governed request persists an `ExecutionJob` and returns the
run to `REQUESTED`; a separately operated worker leases the job and starts the
contract-selected provider. The persistent lease, heartbeat, attempt metadata,
and event records survive a web-server/Django autoreload or worker loss. Its
engineering audit and release gates are recorded with the Sprint evidence.

Sprint B now supplies the sequential reconciliation/recovery layer: stale
worker jobs are evaluated from durable lease, heartbeat, provider and checkpoint
evidence, then reattached, checkpoint-resumed with bounded retries, or placed
in review-required state. Sprint C remains the next ordered work for classified
remediation and parent continuation; Sprint D remains the contract-bound local
Codex wrapper integration.

### Interrupted approval recovery

The governed conversation path now survives a browser refresh, MCP reconnect,
new ChatGPT tool session, or missed affirmative reply. It reuses the existing
canonical approval and orchestration records, provides a safe recovery
projection, and requires an authenticated, exact proposal version/hash-bound
resume confirmation. This is a reliability repair to Milestone 5, not a new
approval or execution architecture.

## Milestone 1 — Project Bootstrap and Onboarding

**Implemented foundation awaiting Product Owner review:** `docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md`

**Goal:** make both new and existing repositories registerable as governed Projects.

Required outcomes:

- Project Registry;
- canonical Project Definition schema;
- `.bridge/project.yaml` creation and validation;
- repository identity resolution;
- new-Project bootstrap path;
- existing-repository assessment and onboarding path;
- governance and document-path discovery;
- onboarding readiness status;
- deterministic evidence that the Project is ready for governed execution.

This milestone must establish the prerequisites consumed by all later capabilities.

## Milestone 2 — Project Context and AKB State Management

**Superseded, not executed specification:** `docs/sprints/SPRINT_002_PROJECT_CONTEXT.md`

**Implemented foundation awaiting Product Owner review:** `docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md`

**Goal:** allow the platform to determine and prove where a registered Project currently stands.

Required outcomes:

- active Project selection;
- generic Project Context services;
- repository observation through a replaceable provider boundary;
- configured AKB / current-state reading;
- validation and drift detection;
- explicit conflict reporting;
- immutable context snapshots;
- explicit, gate-protected main-only AKB publication;
- multi-Project isolation.

Sprint 003 establishes only the minimum Registry and first validated Project Context prerequisite. It does not claim completion of the wider AKB state management outcomes above. This milestone must preserve the static configuration / dynamic state boundary described in this roadmap.

## Milestone 3 — Operational Capability State

**Goal:** make capability readiness and implementation status structured, evidence-backed, and independent from static Project configuration.

Required outcomes:

- authoritative capability-state model in the operational database;
- lifecycle states for planned, in-progress, implemented, proven, accepted, deprecated, and unavailable capabilities;
- evidence and final-commit binding;
- generated AKB / current-state projection;
- drift detection between accepted evidence and projected status;
- Project-level capability queries usable by later planning and handoff services.

This milestone is the explicit roadmap home for the `project.yaml` / dynamic status separation.

## Milestone 4 — Generic Handoff Generator

**Goal:** generate a complete immutable Execution Contract without manually assembling repository, Sprint, workflow, Release Gate, or evidence inputs.

Required outcomes:

- Project Registry and Project Context resolution;
- exact approved Sprint binding;
- Project-definition and document hashing;
- deterministic Release Gate and evidence resolution;
- machine-readable and human-readable contracts;
- lifecycle and single-consumption protection;
- supersession and revocation;
- proof that the same implementation handles differently configured Projects without Project-specific branches.

Sprint 005 establishes tiered policy resolution and the full durable contract lifecycle. Subsequent work consumes the smallest sufficient contract level; Epic-level planning must be decomposed into child implementation contracts.

Sprint 006 adds the first deliberately narrow remote MCP proof: a public, authenticated Streamable HTTP server that exposes only a read-only factory status tool while retaining governed Bridge services behind the canonical internal boundary. It also corrects repository-stored issued-contract baseline validation so issuance does not invalidate its own artifact.

Sprint 007 expands the remote MCP surface into a governed, versioned public registry covering project resolution, bounded accepted knowledge, execution preparation, contract lifecycle, audit, idempotency, approval, and execution-start request boundaries.

Canonical specification:

```text
docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
```

## Milestone 5 — Bridge Conversation Orchestrator

**Goal:** turn the individual governed MCP capabilities into one coherent conversational planning and continuation engine.

Required outcomes:

- intent classification for feature, bugfix, refactor, documentation, deployment, research, and recovery work;
- deterministic tool-planning and prerequisite ordering;
- explicit missing-information detection;
- continuation handling across ambiguous project and execution states;
- generation of one bounded Execution Package containing project, goal, accepted knowledge, constraints, policy, gates, evidence obligations, and handoff;
- durable conversation-to-execution state independent of hidden model memory;
- natural-language journeys such as “Folytassuk a Mesél az Erdőt” without requiring the Product Owner to know tool names;
- no lifecycle mutation without canonical approvals and contract rules.

This is the next orchestration milestone after the governed tool surface. It must reuse the Sprint 007 public and canonical services rather than creating a parallel planning stack.

## Milestone 6 — Autonomous Execution and Repair Loop

**Planned Sprint:** `docs/sprints/SPRINT_009_AUTONOMOUS_EXECUTION_AND_REPAIR_LOOP.md`

**Goal:** prove that Bridge can dispatch one governed execution to Codex, observe progress, repair ordinary technical failures, rerun all invalidated gates, collect evidence, and return one truthful final state without routine Product Owner intervention.

Required flow:

```text
Approved execution package
→ issued and consumed tiered Execution Contract
→ Codex execution start
→ repository mutation
→ targeted validation
→ automatic diagnose-and-repair loop
→ dependent gate reruns
→ documentation and AKB synchronization
→ final evidence binding
→ Product Owner Review
```

Required outcomes:

- canonical Codex dispatcher or durable execution-run adapter;
- execution-run lifecycle and progress events;
- exact repository, branch, baseline, contract, and workspace binding;
- automatic repair of test, lint, type, build, migration, browser, dependency, configuration, evidence, and documentation failures when no reserved Product Owner decision is required;
- root-cause analysis after repeated failure;
- retry and rerun limits that prevent silent infinite loops;
- honest blocking only for Constitution-reserved Product Owner decisions or unavailable external input;
- proof that technical failure does not become a Product Owner support request;
- immutable final execution evidence and exact final commit binding.

## Milestone 6A — Epic Decomposition and Ordered Sprint Orchestration

**Goal:** allow Orki to turn one approved Epic into a governed sequence of canonical child Sprints and continue through them without manual recreation of each scope.

Required flow:

```text
Epic proposal
→ Product Owner approval
→ canonical child Sprint proposals
→ explicit dependency graph
→ Sprint A confirmation / contract / execution
→ Engineering Audit and Release Gates PASS
→ automatic activation of Sprint B
→ repeat until all child Sprints are COMPLETED
→ Epic-level audit and completion
```

Required outcomes:

- canonical Epic record linked to GitHub issue and Project;
- deterministic decomposition into ordered child Sprint proposals;
- explicit parent-child and dependency relationships;
- stable child scope identifiers and proposal hashes;
- policy inheritance with Sprint-specific acceptance criteria and risk modifiers;
- automatic readiness transition for the next Sprint only after the previous Sprint passes all required gates;
- durable continuation across ChatGPT sessions, Bridge restarts, worker restarts, and provider interruptions;
- Epic progress projection showing current Sprint, completed Sprints, blocked dependencies, and next safe action;
- no implicit implementation authority from the Epic alone: every executable child still requires a canonical Sprint proposal, confirmation, contract, and execution record;
- Product Owner escalation only for a genuinely new business decision, scope expansion, governance conflict, or non-recoverable external dependency;
- technical blockers handled through governed remediation and parent-Sprint resume rather than manual Epic reconstruction.

Acceptance proof:

```text
Issue #11 Epic approved
→ Sprint A–D canonical scopes created and dependency-bound
→ each Sprint executes in order
→ later Sprints cannot start early
→ technical interruption is recovered
→ all child scopes and the Epic reach COMPLETED with evidence
```

This capability is complementary to Durable Autonomous Execution. Durable workers and recovery keep one execution alive; Epic orchestration keeps a multi-Sprint product intent alive and advancing.

## Milestone 7 — Complete Governed Execution Loop Proof

**Goal:** prove an end-to-end implementation cycle through the platform on a bounded real application change.

Required flow:

```text
Project selection
→ validated Project Context
→ approved Sprint
→ issued Execution Contract
→ isolated Codex implementation
→ automated tests
→ acceptance suite
→ documentation and AKB update
→ Release Gates
→ final evidence
→ Product Owner Review
```

Proof must include both backend and frontend work when the selected proving Sprint requires them.

## Milestone 8 — Existing Project Safety Proof

**Goal:** demonstrate that an existing repository can be onboarded and modified without uncontrolled restructuring or unrelated regressions.

Required outcomes:

- assessment before mutation;
- canonical-component reuse;
- preservation of unrelated work;
- explicit architecture and AKB conflict handling;
- repository-native tests and Release Gates;
- reversible main-only workflow using new revert or repair commits;
- evidence-backed Product Owner handoff.

A production-critical repository must not be selected as the first safety proof.

## Milestone 9 — New Project Autonomous Delivery Proof

**Goal:** demonstrate that AI Bridge can bootstrap and deliver a complete new application through multiple governed Sprints.

Required outcomes:

- template or technology-profile selection;
- repository creation or initialization;
- Project onboarding;
- architecture baseline;
- frontend and backend implementation;
- automated acceptance testing;
- documentation and deployment preparation;
- full evidence chain across Sprints.

## Milestone 10 — Multi-Project Platform Operations

**Goal:** operate AI Bridge as one platform serving multiple Projects with strict isolation.

Required outcomes:

- Project switching;
- isolated context and execution records;
- Project-specific configuration with generic services;
- repository-provider abstraction;
- operational status overview;
- safe concurrency and execution ownership;
- no Project-specific code paths in platform engines.

## 5. Deferred capabilities

The following are intentionally deferred until the governed development loop is proven:

- organization, department, role, and employee simulation;
- marketing and sales departments;
- customer support operations;
- training and onboarding content platforms;
- autonomous goal decomposition beyond approved Sprint boundaries;
- generalized workflow marketplace;
- advanced analytics dashboards;
- additional broad MCP tool expansion without a proven execution need;
- self-modification without the same Contract, Release Gate, and evidence requirements.

These may remain part of the long-term product vision, but they must not distract from proving autonomous, evidence-backed software delivery.

## 6. Immediate next actions

1. retain the authenticated live MCP tool-call proof, including the controlled
   `EXECUTION_NOT_FOUND` response for unknown execution tokens; no public tool
   may regress to a JSON-RPC internal error for this expected lookup case; when
   an orchestration reports `CONFLICTING_ACTIVE_EXECUTION`, it must also return
   the conflicting token without rebinding contract ownership;
2. refresh and rescan the Bridge app in ChatGPT Business;
3. use Sprint 011's conversational Product Owner confirmation flow as the normal
   entry point for new Work Items and Sprints; its one-time Sprint bootstrap is
   retired after the canonical Sprint record is closed;
4. deploy and refresh the Sprint 012 conversational confirmation tool surface,
   then prove a fresh Work Item through `conversation.confirm` rather than
   `scope.approve`;
5. review the completed Sprint 009 autonomous execution and repair-loop evidence;
6. retain `SPRINT` and `WORK_ITEM` as the executable hierarchy, `AUDIT` as a
   governed work type, and the exact `codex-cli` provider binding from contract
   generation through consumption and dispatch; dynamic provider management is
   deferred unless assessment proves a genuine gap;
7. use Sprint 015's canonical live activity stream and derived checklist when
   observing DEV execution, including repair diagnosis and gate-rerun outcome;
8. select a bounded proving application Sprint for the first complete
   frontend-and-backend execution loop;
9. keep `.bridge/project.yaml` as the static Project definition and use the
   smallest sufficient tiered Execution Contract for every implementation,
   repair, migration, and recovery task;
10. use Bridge-managed canonical Sprint or Work Item scope records for all new
    executable work; legacy Markdown is read-only history;
11. implement Epic decomposition and ordered Sprint orchestration so one approved
    Epic can create dependency-bound canonical child Sprints, advance only after
    PASS gates, survive interruptions, and complete without manual scope recreation.

## 7. Roadmap success criterion

The roadmap's first major success is reached when AI Bridge can demonstrate, with reproducible evidence, that it can:

- onboard a Project;
- determine its real current state;
- receive one approved Sprint;
- generate an immutable execution handoff;
- dispatch Codex through a governed execution boundary;
- implement and test the change;
- diagnose and repair ordinary technical failures without Product Owner intervention;
- rerun every invalidated Release Gate;
- update documentation and AKB;
- pass all Release Gates;
- present exact final evidence for Product Owner Review;
- do so without Project-specific execution logic, hidden manual context, or routine technical escalation to the Product Owner.

## Sprint 015 V3 continuity

Sprint 015 V3 extends the existing activity projection with timestamp-derived
heartbeat and stall semantics, repairable Windows/provider/console failures,
and a read-only Codex handoff bound to durable identifiers. These are
continuity and governance improvements, not a second lifecycle or
provider-created authority.

## EPIC 009 orchestration control plane

EPIC 009 is decomposed into five dependency-ordered Sprints: authority and
provider foundation; durable incident and ownership assessment; linked
remediation and governed executor dispatch; independent validation and
workflow continuation; and governed deployment, rollback, and end-to-end
proof. Sprint A establishes the safe decision boundary only; it does not grant
an LLM execution authority or replace the existing scope and contract lifecycle.

## Lifecycle reconciliation capability

The platform can now canonically admit a previously completed Factory
Development Mode or external governed execution when, and only when, its final
commit, scope-bound evidence, PASS engineering audit, and Product Owner
acceptance can be verified together. This closes a lifecycle-recording gap
without replaying a provider run or weakening the normal proposal,
confirmation, contract, and worker path for future Sprints. The capability is
idempotent and preserves a durable reconciliation audit trail.

## Issue #11 Sprint D: local governed Codex proof

Sprint D completes the local-worker layer of the Durable Autonomous Execution
Epic. A local Codex process leases only a consumed, hash-bound execution and
uses the durable queue for heartbeats, checkpoints, interruption recovery, and
completion evidence. The implementation rejects scope drift and unverified
pre-existing sessions. The remaining Epic activity is the cross-Sprint
integration audit and Product Owner review.

## Sprint 1 factory E2E remediation continuation

The bounded recovery continuation preserves the existing canonical provider,
workspace, checkpoint, and activity-evidence path. It does not add a persistent
model or Sprint 2 capability. Its completed UI correction makes the durable
`Run ID` the first `ExecutionRun` admin changelist column; the clean governed
provider E2E remains subject to the normal consumed-contract and Release Gate
requirements.

## Issue #11 Sprint C — automated technical remediation

Sprint C is complete and ready for Product Owner review. It adds the governed
technical-remediation loop required for Orki to repair an in-scope technical
blocker, rerun its invalidated gate, and resume the original parent execution.
The loop creates an auditable linked Work Item, never a replacement provider
run or Execution Contract. The next Epic #11 dependency is Sprint D: the local
Codex wrapper and durable handoff proof.

## Sprint 6 confirmation-binding repair deployment history

The earlier, phrase-only Product Owner confirmation repair was deployed to the staging
Remote MCP runtime at `30648dc0625fef7e6451b0b7ace9bc6422a5c96d`. Its public
health surface is SHA-bound to that revision. This repairs persistence of an
explicit unconditional confirmation without weakening server-derived scope,
proposal, caller, approval-reference, or idempotency bindings. Sprint 6 still
requires its one genuine ChatGPT Business UI request and in-UI approval for
Operational Acceptance; static API authentication is not a substitute.

Sprint 6 workspace-provisioning remediation is implemented locally: stale
provider-free `STARTING` leases are reconciled into bounded recovery rather
than remaining quiet. The repaired execution `218cb756-807c-46d5-8e82-dc19ac210f08`
reached checkout, venv, database, bootstrap, and provider start on retry.
This is a local runtime recovery proof, not the outstanding ChatGPT Business
UI-to-Remote-MCP Operational Acceptance proof.

The same historical execution then exposed a distinct provider-completion
finalization defect: a `PROVIDER_COMPLETED` event was previously treated as an
external-input block before workspace inspection. Sprint 6 now queues an
idempotent worker-owned finalization step, clears the PID, records repository
facts and an explicit no-change or missing-completion outcome, then uses
bounded technical recovery. The legacy execution has no committed change or
delivery and remains immutable historical evidence; a fresh ChatGPT Business
UI request is required for the truthful end-to-end proof after staging carries
this repair. It does not prove the later caller/session-binding remediation is
loaded by any staging MCP, worker, or scheduler process.

The subsequent cleanup-recovery repair is also included in that staging
revision. A runtime verifier first honestly failed when an expired locked
workspace raised `PermissionError` from the scheduler; the repair records a
bounded retained retry instead. The rerun passed public SHA, migration plan,
dependencies, worker, and scheduler checks. This proves the staging runtime is
ready for, but does not replace, the required ChatGPT Business UI proof.

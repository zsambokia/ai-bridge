# AI Bridge – Current State

## Sprint 02 Semantic Intelligence — 2026-08-08

The Semantic Layer is implemented as an additive, provider-independent
retrieval foundation. Approved, active AKB entries can be explicitly indexed
into a versioned local vector cache and retrieved as scored candidates with
metadata and reproducible evidence. `SemanticCandidateSelector` and RAG only
rank and return candidates; they do not make business decisions or execute
Runtime actions. `SemanticContextBuilder` is the semantic path for bounded,
deduplicated LLM context assembly. The Runtime remains unchanged.

## Orki Orchestrator Runtime Foundation — 2026-08-07

The approved Runtime baseline is implemented in Factory Development Mode as a
provider-independent coordination layer. Its canonical model is
[Orki Orchestrator Runtime](../architecture/ORKI_ORCHESTRATOR_RUNTIME.md):
`Goal -> Plan -> OrkiExecution`, with an append-only Runtime Event Stream and
an OESM lifecycle. It separates the execution question ("what am I doing?")
from the existing Cognitive State knowledge question ("what do I know?").

The Foundation is Shadow Mode only. Factory Chat creates an existing
`FactoryPlan`, then Runtime records `CREATED -> PLANNING -> WAITING_APPROVAL`;
after the existing approval it observes `WAITING_GOVERNANCE`. It does not create
an Execution Contract, `ExecutionRun`, `ExecutionJob`, queue item, provider
call, or Cognitive State copy. Release evidence is under
`docs/evidence/bridge-ai-bridge-sprint-712aef15-2426-4f57-88b6-8b1389807b3e/`.

## Orki Cognitive Operating System technical Epic closure — 2026-08-02

ORKI-001 through ORKI-010 are formally closed as the technical Cognitive
Operating System Epic and have passed final
[compliance certification](../evidence/orki-cognitive-operating-system-compliance-certification-20260802/CERTIFICATION_REPORT.md)
on the official `main` reference `4b2ddf2f3ab81993691f6319d645d12b9c8acd5e`.
They received Product Owner final acceptance; the architectural foundation is
complete. The historical DCMI remains
**66/100**, independently arithmetic- and provenance-validated. This is
deliberately not a claim of completed Digital COO behavioural certification:
the 100-scenario, independently judged CVO work is separate, active under the
Digital COO Program and not yet evidenced; its status is **DIGITAL COO
VALIDATION: NOT YET CERTIFIED**.

## ORKI-011 Factory Chat Completion — 2026-08-02

ORKI-011 is a bounded Factory Development Mode completion sprint around the
already accepted Cognitive Operating System foundation. Factory Chat now
projects canonical, project-scoped Cognitive State and its mission, facts,
assumptions, decisions, recommendations, plan, roadmap and document lifecycle
without manual Product Owner synchronisation. It adds safe Hungarian error
projection, correlation-bound idempotent retry, draft recovery across failure
and refresh, optimistic pending feedback, explicit plan approval review, and
responsive Factory Chat evidence without changing Cognitive State reasoning or
treating transcript as memory. Its release evidence is [ready for Product Owner review](../evidence/sprint-orki-011-factory-chat-robustness-ux-hardening-20260802/ASSESSMENT.md), with the exact Sprint record at [SPRINT ORKI-011](../sprints/SPRINT_ORKI_011_FACTORY_CHAT_ROBUSTNESS_UX_HARDENING.md).
The required [Factory Chat completion record](../sprints/SPRING_ORKI_011_FACTORY_CHAT_COMPLETION.md)
binds the closure to the detailed Sprint evidence. The historical DCMI remains
**66/100**. CVO-002 remains a separate, unexecuted
Digital COO training and validation loop; ORKI-011 makes no certification or
behavioural-maturity claim.

## Factory readiness maturity baseline — 2026-07-31

The independent factory-readiness baseline is **NOT READY**: 40/100 maturity,
an estimated 55% non-governance human-intervention dependency, and AKB maturity
4.3/10. It is recorded in
[`FACTORY_READINESS_MATURITY_BASELINE_2026-07-31.md`](FACTORY_READINESS_MATURITY_BASELINE_2026-07-31.md)
with canonical [audit evidence](../evidence/factory-readiness-audit-20260731/FACTORY_READINESS_AUDIT.md).
The linked `KnowledgeEntry` is a non-active `CANDIDATE` only; the proposed
Sprint 016 is not execution authority.

## ORKI-002 Mission Understanding (2026-08-01)

Orki's canonical Mission Understanding boundary is now a project-scoped,
explainable `PROPOSED` Mission State. Product Owner conversation is evidence,
never Cognitive State memory: the raw text is retained only by the conversation
record and represented in state provenance by an allowlisted identifier and
hash. The reusable `mission_understanding` observation distinguishes stated
facts, inferred business goal, solution proposal, technology preference, safe
assumptions and material unknowns. It evolves confidence through supersession,
requires a material effect before recording a question, and must not create a
recommendation or plan. The canonical developer integration contract is
[ORKI Cognitive Data Flow](../architecture/ORKI_COGNITIVE_DATA_FLOW.md).

## Orki autonomous delivery and Executive Checkpoints (2026-08-02)

The Product Owner authorised Factory Development Mode execution through
ORKI-006. ORKI-001 is accepted and ORKI-002 Mission Understanding, ORKI-003
Recommendation Engine, ORKI-004 Decision Intelligence, ORKI-005 Planning
Intelligence, and ORKI-006 Memory Intelligence received independent Release
Gate PASS results. Executive Checkpoint B was accepted and the Product Owner
directed continuation to ORKI-007 Initiative Engine.
No individual Product Owner approval wait is required between ORKI-003 through
ORKI-006 when the preceding Sprint's full Release Gates pass. Informational
Executive Checkpoint A follows ORKI-003 and Checkpoint B follows ORKI-006;
they provide DCMI, capability, risk, debt, architecture-evolution, gate, and
self-critique evidence but never suspend autonomous implementation. The
canonical rule is [Orki Executive Checkpoints](../architecture/ORKI_EXECUTIVE_CHECKPOINTS.md).

## ORKI-003 Recommendation Engine (2026-08-02)

The canonical Recommendation Engine now writes project-isolated, attributable
Cognitive State recommendations. Every recommendation keeps its evidence and
assumption links separate, its alternatives and trade-offs explicit, its
confidence and next safe action visible, and its Product Owner decision
boundary non-authoritative. Correction supersedes an existing artefact rather
than erasing its provenance. The public Factory route uses this state path and
cannot create a decision, plan, governance action, or execution.

The independent Release Gate is PASS; its evidence package is
[ORKI-003 Recommendation Engine](../evidence/sprint-orki-003-recommendation-engine-20260802/ASSESSMENT.md).
Executive Checkpoint A has been issued as an informational report and does not
pause the authorised ORKI-004 through ORKI-006 sequence.

## ORKI-004 Decision Intelligence (2026-08-02)

The canonical Decision Engine now creates project-isolated, evidence-backed
open decisions from material recommendations. Its explainable projection
retains the required question, options, recommendation, confidence, evidence,
assumptions, alternatives, trade-offs, materiality, impacts, and lifecycle.
Only an explicit, attributable Product Owner confirmation can accept an option;
provider output and raw conversation text cannot.

The independent behavioural Release Gate is PASS, including conflict/stale
handling, project isolation, transcript separation, and the absence of plan,
governance, or execution side effects. Evidence is in
[ORKI-004 Decision Intelligence](../evidence/sprint-orki-004-decision-intelligence-20260802/ASSESSMENT.md).
Autonomous execution continued to ORKI-005 Planning Intelligence.

## ORKI-005 Planning Intelligence (2026-08-02)

The canonical Planning Engine now produces a project-isolated, revisioned
`PLAN` Cognitive State artefact. It requires cited canonical evidence and
records objective, business value, architecture, alternatives, selected and
rejected strategy, risks, dependencies, acceptance, release, operations,
recovery, and future evolution. Its projection resolves its durable evidence
references without retaining transcript text. A Cognitive Plan is deliberately
distinct from the legacy `FactoryPlan` delivery workflow; it cannot create
delivery work, governance approval, or execution. Evidence is in
[ORKI-005 Planning Intelligence](../evidence/sprint-orki-005-planning-intelligence-20260802/ASSESSMENT.md).
Autonomous execution now continues to ORKI-006 Memory Intelligence.

## Repository

## ORKI-006 Memory Intelligence (2026-08-02)

The canonical Memory Engine now evolves project-scoped, evidence-bound reusable
knowledge as revisioned `MEMORY` Cognitive State artefacts. It validates cited
active canonical state, confidence, tags, provenance, and stable identity;
corrections supersede prior knowledge without erasing its trace. Retrieval is a
deterministic projection of active structured memories and never searches the
conversation transcript. Memory cannot publish accepted AKB knowledge or create
a plan, governance approval, delivery work, or execution authority. The
independent Release Gate is PASS; evidence is in
[ORKI-006 Memory Intelligence](../evidence/sprint-orki-006-memory-intelligence-20260802/ASSESSMENT.md).
Executive Checkpoint B is informational only and was followed by the
authorised ORKI-007 Initiative Engine work.

## ORKI-007 Initiative Engine (2026-08-02)

The canonical Initiative Engine now derives proactive, explainable and
dismissible observations only from project-scoped structured Cognitive State.
The proven deterministic rules cover risks, opportunities and missing evidence;
each observation retains its source, confidence, rationale, priority and an
explicit `NONE` authority boundary. At most five observations can remain
active, and Product Owner dismissal creates attributable evidence without
altering the source state. A normal Factory Chat turn proves the capability
without exposing transcript text or creating a `FactoryPlan`, governance
action, delivery work, or execution.

The independent Release Gate is PASS; evidence is in
[ORKI-007 Initiative Engine](../evidence/sprint-orki-007-initiative-engine-20260802/ASSESSMENT.md).
The [DCMI scorecard](../architecture/ORKI_DCMI_SCORECARD.md) moves from the
accepted Checkpoint B baseline of 58/100 to 66/100. Semantic inconsistency,
duplication, reuse and simplification detectors, governance integration and
COO UX remain unproven Epic work.

The Product Owner has accepted ORKI-007 Engineering Acceptance, Operational
Acceptance and Initiative Engine capability. The accepted result is Initiative
**Level 1 — Observation**. The future behavioural maturity sequence is Level 2
Recommendation, Level 3 Alternative proposal and Level 4 Cross-project
strategic initiative; it is governed by
[Orki Initiative Maturity](../architecture/ORKI_INITIATIVE_MATURITY.md). DCMI
may rise only from independently proven behavioural improvements, not from
additional technical artefacts.

## Current Orki progression (2026-08-02)

ORKI-001 is accepted; ORKI-002 through ORKI-007 have independent PASS evidence.
Executive Checkpoints A and B are issued. DCMI is 66/100, a capability-level
measurement rather than an Epic-completion claim.

ORKI-007 is also Product Owner accepted at Initiative Level 1 — Observation.

## ORKI-008 Product Owner Cognitive Model (2026-08-02)

The Product Owner directed a strategic sequence adjustment: before further
Recommendation Intelligence expansion, Orki must prove a distinct Product
Owner Cognitive Model. It holds only evidence-linked operational collaboration
patterns—such as decision style, risk tolerance, planning depth, governance,
documentation, architecture, sprint-size and communication preferences—not
personal data or conversation transcripts. The model is explainable,
correctable, reviewable, versioned, and project-aware; it may guide a safe
default but cannot create decisions, approvals, plans, governance actions, or
execution.

The canonical Cognitive State is now explicitly composed of Mission, Project,
Product Owner, and Factory Models. [ORKI-008](../sprints/SPRINT_ORKI_008_PRODUCT_OWNER_COGNITIVE_MODEL.md)
is independently release-gated PASS: it proves ten-interaction learning,
evidence-bound profile revisions, Product Owner correction, conflict-safe
projection, transcript separation, project isolation, and no authority side
effects. The accepted 66/100 DCMI v1 result is retained as ORKI-007 history;
DCMI v2 moves from its transparent 60/100 baseline to 66/100 through a proven
7/10 Product Owner Understanding foundation. See the
[Product Owner Cognitive Model](../architecture/ORKI_PRODUCT_OWNER_COGNITIVE_MODEL.md)
and [DCMI scorecard](../architecture/ORKI_DCMI_SCORECARD.md).

## Repository

## ORKI-009 Product Owner Model Evolution (2026-08-02)

The Product Owner accepted the evolved operational working-relationship model:
profile confidence is evidence-weighted and explainable, revisions preserve
history, and cognitive drift compares earlier and recent attributable patterns
instead of silently overwriting preferences. The model remains project-scoped,
correctable, transcript-free and non-authoritative. The accepted DCMI remains
66/100; this foundation does not claim points merely for an additional model.

## ORKI-010 Operational Reasoning Engine (2026-08-02, implementation accepted)

ORKI-010 makes structured operational reasoning a canonical Cognitive State
artefact. A Factory Chat provider cannot persist a direct recommendation: it
must supply a state-validated reasoning cycle with mission, evidence,
assumptions, unknowns, at least three alternatives, trade-offs,
counter-arguments, cost, risk, long-term effect, simplicity, expected impact,
confidence and the required Product Owner decision boundary. The resulting
recommendation is derived from that artefact and retains its provenance.
Product Owner Model adaptation is explicit, evidence-bound and never authority.
The Product Owner accepted the engineering, operational and architecture
implementation. DCMI stays 66/100 pending diverse behavioural measurement.

## CVO-001 Digital COO Validation baseline (2026-08-02)

The Product Owner directed a pause in new capability implementation and required
100 difficult, realistic Product Owner scenarios before Orki makes any further
Digital COO maturity claim. The resulting
[CVO-001 validation report](../evidence/orki-digital-coo-validation-20260802/VALIDATION_REPORT.md)
does not pass the behavioural gate: it documents that the current ORKI-010
tests validate a structured pipeline with pre-authored mocked reasoning, not
independent COO-quality thinking. The 100-case
[challenge corpus](../evidence/orki-digital-coo-validation-20260802/SCENARIO_CORPUS.md)
is specified but not represented as executed evidence. The accepted 66/100
DCMI is retained as historical reference only; no score increase is justified.
Future repair must be failure-driven, separately bounded, and followed by a
rerun of the corpus.

## CVO-002 Digital COO Improvement Loop (2026-08-02, prepared)

The Product Owner has turned the next stage into a Training & Validation Epic,
not a feature Epic. [CVO-002](../epics/CVO_002_DIGITAL_COO_IMPROVEMENT_LOOP.md)
requires every executed failure to receive an immutable
[Failure Card](../evidence/orki-digital-coo-validation-20260802/FAILURE_CARD_TEMPLATE.md),
with an original-scenario regression rerun after a bounded correction. The
100-case [Golden Scenario Corpus](../evidence/orki-digital-coo-validation-20260802/GOLDEN_SCENARIO_CORPUS.md)
defines weak, average, and excellent Digital COO behaviour; the independent
Business, Architecture, and Operations judges are governed by the
[COO Judge Protocol](../evidence/orki-digital-coo-validation-20260802/COO_JUDGE_PROTOCOL.md).
No scenario has been executed under this loop and no DCMI increase is claimed.

- Repository: `zsambokia/ai-bridge`
- Development branch: `main`
- Canonical Bridge Constitution: `docs/constitution/BRIDGE_CONSTITUTION.md`

## Implemented foundation

## Sprint 8 Factory Readiness Dossier and external-certification boundary

The final Sprint 8 dossier is recorded at
`docs/evidence/factory-readiness-dossier-20260801/`. It reassesses the full
promised chain at **82/100** maturity from the 40/100 corrective baseline and
separates accepted AI Bridge-owned readiness from the unaccepted ChatGPT
Business UI/Remote MCP platform proof. The score is not an Epic release
verdict: Sprint 6 remains unchanged and non-PASS, and the separate ChatGPT
Business Platform Certification Epic must still prove a genuine UI request,
Product Owner UI approval, Remote MCP call, canonical orchestration/delivery/
deployment receipts, and later UI retrieval. No local bearer-token or seeded
projection substitutes for that evidence.

## Sprint 7 autonomous technical remediation and self-healing proof

Sprint 7 is accepted by the Product Owner under Factory Development Mode. An
unclassified worker exception outside the specialised workspace-provisioning
recovery path is now a durable technical-remediation incident: Orki records
ownership, evidence, a bounded child remediation scope, and the original run
checkpoint. The job is deliberately released from its lease and cannot remain
quiet in an intermediate lifecycle state. Independent invalidated-gate
validation is required before the original checkpoint and job can resume.
Admin and the public read-only MCP execution projection share the same loop,
validation, incident, and business-escalation records. The evidence package is
`docs/evidence/sprint-021-autonomous-technical-remediation-self-healing/`.

Sprint 6 remains **BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE** solely for
the final ChatGPT Business in-app Remote MCP proof. Its existing evidence and
status are intentionally preserved unchanged; the separate ChatGPT Business
Platform Certification Epic owns that external certification.

## Sprint 5 SHA-bound runtime deployment

Sprint 5 implementation and operational evidence are **accepted by the Product
Owner**. It separates a
repository delivery receipt from runtime activation: a `RuntimeDeployment`
binds a verified delivery to its immutable artifact SHA, target identity,
authority, migration/dependency checks, runtime health, worker and scheduler
supervision, Operational Acceptance and rollback receipt. The deployment
projection is read-only and common to Django Admin and MCP. The verification
command checks the live health/build SHA and canonical supervision services but
does not create a deployment claim. Isolated live-runtime evidence includes a
controlled SHA mismatch, forward deployment and verified rollback. See
[`RUNTIME_DEPLOYMENT_OPERATIONAL_ACCEPTANCE.md`](../architecture/RUNTIME_DEPLOYMENT_OPERATIONAL_ACCEPTANCE.md).

## Sprint 2 Orki orchestration knowledge

Normal governed ChatGPT/MCP work is not allowed to create a contract or
execution directly.  The `conversation.confirm` path creates an idempotent
`OrchestrationSession`, records ownership and policy, hashes the governed
context and decision, and binds those values to the contract and run.  Worker
dispatch re-verifies that binding before it provisions a workspace.  A
multi-project request is a durable `AMBIGUOUS_OWNERSHIP` escalation; a
technical request remains an engineering decision; and direct public contract
generation reports `ORCHESTRATION_GATE_REQUIRED`.  See
[`ORKI_MANDATORY_ORCHESTRATION_GATE.md`](../architecture/ORKI_MANDATORY_ORCHESTRATION_GATE.md)
for the canonical trace and intentionally separate recovery/bootstrap paths.
The isolated Factory runtime has also proven the trace through a real worker,
provider-loss reconciliation, bounded provider-start retry, and a completed
governed workspace-only request; the honest operational transcript is
[`OPERATIONAL_ACCEPTANCE.md`](../evidence/sprint-017-orki-mandatory-orchestration-gate/OPERATIONAL_ACCEPTANCE.md).

## Sprint 4 autonomous repository delivery

Sprint 4 implementation and operational evidence are **accepted by the Product
Owner**. It adds a fail-closed, contract-bound delivery verifier: exact scoped
local HEAD, clean workspace, required gates, SHA-bearing evidence, non-force
push and remote-SHA readback are mandatory before a run can become completed.
Remote movement requires reconciliation, and the execution provider cannot
self-approve verification. `ExecutionDelivery` is the shared durable
Admin/API/MCP projection. See
[`AUTONOMOUS_REPOSITORY_DELIVERY.md`](../architecture/AUTONOMOUS_REPOSITORY_DELIVERY.md)
and `docs/evidence/sprint-018-autonomous-repository-delivery/`.

At Epic closure, create the requested Factory Readiness Dossier: the complete
Sprint acceptance timeline, material remediation cycles, before/after maturity
assessment, known limitations/next areas, and a per-Sprint compliance matrix
linking objective, delivered capability, Engineering and Operational evidence,
and Product Owner acceptance date/status.

## Sprint 3 durable AKB and roadmap feedback loop

Sprint 3 implementation and operational acceptance are **accepted by the
Product Owner**. It persists every
retrieved Orki context package and its consumers (session, decision, contract,
and run), including query/intent, selected IDs, source versions, stale and
conflict warnings, and a deterministic package hash. Its `RoadmapItem` and
`RoadmapUpdateCandidate` lifecycle is project-isolated and approval-gated:
delivery evidence creates a candidate, while canonical progress changes only
after review. A `COMPLETED` transition requires engineering PASS, operational
PASS, evidence references, and a 40-character commit SHA.

The local operational runtime proved a fresh governed HTTP MCP conversation,
cross-project isolation, persisted Orki-to-run context consumption, approved
roadmap transition, and read-only Admin/MCP projections. The complete evidence,
including rejected fixture and request-shape attempts, is under
`docs/evidence/factory-readiness-remediation-sprint-3-20260731/`.

The Django 5.2 foundation contains split settings, SQLite configuration, the
`core` health endpoint, and the canonical `projects` domain. The latter
provides one Project Registry model, onboarding readiness (`PENDING`, `READY`,
`INVALID`), a static `.bridge/project.yaml` loader, the constrained
`bootstrap_project` command, and Project Context validation (`VALID`,
`INVALID`, `STALE`).

The registered `storybook` Django app provides the standard, intentionally
empty application foundation (`admin`, `apps`, `models`, `tests`, `views`, and
the migrations package) for future Storybook behaviour. A targeted Django app
registry test verifies that its configured application loads. It currently has
no models, routes, or public interface.

The Project Definition is static configuration. Lifecycle, onboarding, Context,
and capability state are runtime data and are not written back to YAML.

## AKB Sprint 1 foundation

Sprint 1 adds durable, governed Platform and Project knowledge entries,
append-only revisions, metadata-filtered bounded retrieval, deterministic
Orchestrator Context Packages, and an approval-controlled candidate-to-active
lifecycle. The implementation and deliberately deferred capabilities are
described in `docs/architecture/AKB_FOUNDATION.md`.

## AKB Sprint 2 engineering memory

Sprint 2 adds the governed, project-isolated engineering-memory graph:
versioned entities, typed evidence-bearing relations, approval-gated
publication, first-class Roadmap/Constitution/UI Plan/System Design objects,
role-ranked retrieval, planning-gap analysis, and retry-safe lifecycle
candidate ingestion. Append-only entity history and Constitution revision diff
are read-only MCP operations. The implementation details and explicit
deployment/rollback limitation are documented in
`docs/akb/ENGINEERING_MEMORY.md`.

## Verified current execution

Sprint 003 bootstrap was run against this repository's own Project Definition.
It created the canonical `ai-bridge` Registry record with onboarding `READY`
and a first `VALID` Project Context. The result is runtime data in the local
Django database, not a fixture or seed.

The same canonical bootstrap was also proven against the persistent, independent
`zsambokia/bridge-demo` repository. Its `bridge-demo` Registry record remains
`READY`; its current Context is `VALID`, and its earlier source revision is
preserved as `STALE`. The local development database therefore contains exactly
the `ai-bridge` and `bridge-demo` Registry records. Django Admin exposes both
runtime models as read-only operational views; it cannot create, change, or
delete them outside the canonical bootstrap lifecycle.

## Implemented execution foundation

Issue #14 adds a durable, one-to-one `ExecutionWorkspace` and a canonical,
project-owned `RuntimeBootstrapProfile` to the execution foundation. The
independent worker now provisions an isolated repository checkout, virtual
environment, workspace SQLite application database, dependency fingerprint,
migration verification, deterministic seed state, declared runtime services,
and verified runtime descriptor before it may invoke Codex. The control-plane
checkout and database are not reused for provider work. Workspace state,
retention, safe cleanup, provider PID, immutable baseline metadata, runtime
profile state, and failure/cleanup evidence are persisted; Django admin exposes
a read-only operational view. The root/cache, retention policy, Python
executable, database mode, maximum disk budget, and provisioning timeout are
explicit settings. `reconcile_execution_workspaces` performs safe, idempotent
expiry cleanup without touching the control plane.

The bounded Sprint 1 factory-E2E remediation retains this canonical lifecycle
and its existing recovery/checkpoint evidence rather than creating a new model
or alternate persistence path. `ExecutionRun` administration now presents the
durable `Run ID` as its first changelist data column; the provider token remains
available as a separate correlation value.

Sprint 016 strengthens that same lifecycle with transactional worker dispatch
rechecks, persisted lease-fencing tokens, run/job divergence convergence,
structured recovery classification, bounded recovery and review terminalization,
workspace PID-loss recovery, and reasoned orphan-workspace retention. The
reconciliation command, Django Admin, and `execution.get_run_status` MCP tool
project the same safe lifecycle, lease, recovery, workspace, and evidence state.
The operating invariants are in
[`EXECUTION_LIFECYCLE_RECOVERY.md`](../architecture/EXECUTION_LIFECYCLE_RECOVERY.md);
Sprint acceptance remains subject to the recorded Release Gates and audit
evidence.

Sprint 6 additionally closes the provider-free provisioning recovery gap. A
stale `STARTING` lease before `WORKSPACE_REPOSITORY_READY` is now reconciled
from canonical queue and run facts, then retried with durable, bounded recovery
evidence. This covers isolated checkout, venv, database, seed, and bootstrap
before a provider PID exists; provider recovery remains a separate later-stage
concern.

Operational Acceptance is a separate mandatory Sprint closure stage. The
Sprint 016 record documents a real-worker reattach, controlled dead-provider
recovery, canonical completion, and Admin/application API/MCP projection parity
at repaired revision `546bde6a66eaf645ddc0f3e047b5ed5c238f4847`; it does not
make an unsupported claim about the revision of the shared stage runtime.

Sprint 014 adds a provider-neutral `ExecutionProvider` registry and append-only
provider audit history. Codex CLI is seeded as the active execution agent;
OpenAI, Claude, GitHub, and BigQuery are explicit provider kinds/roles that
remain unavailable until an operator configures a non-secret credential binding
and validates their adapter. The execution lifecycle still dispatches only the
exact provider identity recorded in the consumed contract.

Codex is recorded as a `CODE_EXECUTION_AGENT` with a non-secret relationship to
the existing OpenAI `MODEL_API_SERVICE`. Its proven mode is `CODEX_CLI_LOGIN`;
the relationship is informational and never duplicates or resolves the OpenAI
credential. Codex runtime health is `HEALTHY` only when its configured
executable is both present and authenticated according to `codex login status`.
The health check discards command output, so tokens and other CLI output cannot
enter provider state or audit history. The `codingproviderproof` app is an
intentionally empty Django application used solely as a harmless, canonical
coding-provider proof; it has no models, routes, or public interface.

Local Django settings optionally load the Git-ignored repository-root `.env`
file before shared settings. The tracked `.env.example` is secret-free and
documents `OPENAI_API_KEY`; process environment values take precedence. The
OpenAI provider retains only the `OPENAI_API_KEY` binding name, while staging
and production must inject the actual value through their platform secret
manager. The operational configuration steps are in
`docs/operations/DJANGO_ADMIN.md`.

For local conversational MCP E2E authentication, the existing settings loader
reads `MCP_TEST_API_TOKEN` from the ignored local `.env` and binds it only to
the MCP bearer runtime setting; the token is neither persisted nor logged.

Sprint 004's operation registry remains the canonical internal service surface
for Project resolution and contract lifecycle. Sprint 006 replaces its former
public proprietary `operation`/`payload` adapter with an authenticated remote
MCP server at `POST /mcp/`. The public server implements the Streamable HTTP
MCP lifecycle (`initialize`, `tools/list`, `tools/call`) and exposes only the
read-only `factory.get_status` tool, backed by real Project data. It does not
publish broad governance-write operations.

The same domain now constructs a canonical, structured Execution Context from a
Project, its valid Project Context, `.bridge/project.yaml`, and an explicit
approved Sprint path. The Context includes repository, branch, exact baseline,
binding documents, release gates, evidence root, allowed terminal states, and a
unique execution identifier. It is the source for the MCP response and Codex
execution package; Markdown contracts are representations rather than the
canonical object.

Sprint 005 adds the canonical `ExecutionContract` persistence model and the
generate, validate, issue, retrieve and render lifecycle through the same MCP
surface. Issued payloads are immutable, have reproducible SHA-256 hashes, bind
their governance documents and baseline commit, and render human handoffs only
from stored data. The generator successfully issued the required Sprint 004
contract from baseline `14ce5ff7f1c6e5739d7aa83044529e9d6d55b1e7`.

The execution contract is now tiered (`HOTFIX`, `BUGFIX`, `TASK`, `SPRINT`,
`EPIC`) with deterministic policy profiles resolved from level, task type, and
risk modifiers. The policy can only strengthen obligations. Durable lifecycle
operations consume, complete (with final commit and closure binding),
supersede, or revoke a contract; an Epic cannot authorize code changes itself.

The Django base settings explicitly permit the approved Cloudflare tunnel
hosts `stage.artificial-software-factory.com` and
`app.artificial-software-factory.com`. Additional deployment hosts are opt-in
through `DJANGO_ALLOWED_HOSTS`; wildcard configuration is rejected.

The remote MCP endpoint uses a configured Bearer token (`MCP_API_TOKEN`) and
fails closed if it is missing. It is deliberately CSRF-exempt for authenticated
machine requests, returns JSON errors rather than HTML or login redirects,
disables shared caching, and honors the Cloudflare forwarded HTTPS scheme.
Staging connection instructions, token rotation, and the production OAuth
direction are in `docs/integrations/CHATGPT_MCP_CONNECTION.md`.

Sprint 006 also corrects contract lifecycle validation for repository-stored
issued contracts. A committed issued artifact cannot keep an `EXACT` `HEAD`
baseline because its own publication advances `HEAD`; generated repository
contracts therefore use the canonical `DESCENDANT_OF` rule and retain the exact
generation SHA. A regression test prevents recurrence.

Sprint 007 adds the governed public MCP registry. It reuses the canonical
Project resolver, execution-context generator and tiered contract lifecycle;
it adds durable approval references, audit events, idempotency records,
execution preparations and dispatcher-free start requests. The public AKB
surface is deliberately bounded to accepted current-state and roadmap documents.

Sprint 009 replaces the dispatcher-free start-request boundary with the
canonical `ExecutionRun` model and a fixed-argument Codex CLI provider. A
consumed contract, scoped durable approval and dispatch audit record are all
required before external execution becomes active. The run records repository,
branch, baseline, contract hash, workspace/provider identity, lifecycle,
bounded secret-free events, repair attempts, evidence root and final binding.
The governed MCP surface now supports start, status, events, cancellation and
evidence-summary operations. Routine migration and lint/type failures have
deterministic repair classifications; unavailable provider access and reserved
Product Owner decisions remain honest block categories.

The scope intentionally does not add AKB indexing, vector search, Discovery,
autonomous planning, or a large user interface.

## Sprint 010 canonical authority

Sprint 010 replaces the former Sprint-Markdown authorization route with a
versioned `ExecutableScope` record. A Sprint and an ad hoc Work Item are
separate executable kinds; an Epic is a planning boundary and cannot be
issued as execution authority. The canonical record is schema-validated,
approved by a durable scope-bound approval, and published only as a
deterministic Markdown projection. Historical Sprint 005–009 Markdown remains
readable for compatibility, but cannot create, validate, issue, consume or
start a new contract.

Only AI Bridge can generate, validate and issue schema `2.0` contracts from a
published, approved, non-terminal canonical scope. An execution provider must
record an exact-hash consumption receipt under its own identity before a run
can start. Approval and scope publication are rechecked at validation,
issuance, consumption and start. Scope terminal transitions (`complete`,
`cancel`, `supersede`) revoke new lifecycle progress; completion requires a
matching terminal `ExecutionRun`, the actual checked-out commit, non-empty
gate/evidence data, and the allowed closure state.

The governed MCP registry exposes the end-to-end scope and contract lifecycle;
the final repository evidence is under `docs/evidence/sprint-010/`.

## `execution.prepare` schema integrity

The governed registry now uses its published `tools/list` input schema as the
single runtime argument-validation source. `execution.prepare` therefore
accepts only `project_id`, `scope_identifier`, and `idempotency_key`, while
proposal tools constrain execution-level, task-type, and risk-modifier
vocabulary to the canonical contract-policy constants. Natural-language work
such as creating `storybook` must pass through proposal, validation, durable
approval, publication, preparation, contract generation, validation, and
issuance; preparation cannot authorize a direct repository mutation. The
verification record is under
`docs/evidence/execution-prepare-schema-bugfix/`.

## Sprint 011 conversational Product Owner confirmation

Sprint 011 introduces a durable conversational Product Owner confirmation path.
The one-time external bootstrap authority applies only to Sprint 011 itself. The
Storybook Work Item followed its own exact proposal-hash confirmation and the
ordinary approval, publication, contract, provider, evidence, and completion flow.

### Confirmation predicate repair (Sprint 6)

A real ChatGPT Business confirmation surfaced an input-interpretation defect:
the canonical confirmation routes reached their binding logic but accepted only
a small exact Hungarian phrase list. An explicit unconditional English Product
Owner approval was therefore rejected before durable approval persistence. The
governed predicate now accepts explicit unconditional English and Hungarian
approval, rejects negative or conditional wording, and continues to derive the
caller binding, proposal binding, approval reference, and retry key on the
server. The repair does not relax scope/version/hash validation or create a
second authorization lifecycle. Source-level and authenticated HTTP regression
evidence lives in `docs/evidence/sprint-020-chatgpt-factory-e2e/`; a deployed
ChatGPT Business UI retry is still required for Sprint 6 Operational Acceptance.

## Sprint 012 conversational routing assessment and repair

Sprint 012 assessed the existing `conversation.confirm` and
`ConversationOrchestration` path before changing it. The canonical services
already existed; the failed conversation selected lower-level `scope.approve`,
which correctly returned `APPROVAL_REQUIRED` because no durable approval
reference existed. The repair makes `scope.review` explicitly route eligible
confirmation to `conversation.confirm` and makes that high-level tool derive
the authenticated caller binding, confirmation reference, and retry key. It
does not introduce a second approval or execution lifecycle. Remote acceptance
status and terminal evidence are recorded under `docs/evidence/sprint-012/`.

## Sprint 013 governed provider-boundary audit

Sprint 013 records that `conversation.confirm` remains the canonical
conversational Product Owner confirmation path; `GovernanceApproval` and
`ConversationOrchestration` preserve the durable approval and resumable
orchestration records. `ExecutionContract` selects and allows only `codex-cli`;
consumption records that exact provider identity before `ExecutionRun` obtains
the fixed-argument Codex CLI adapter. An unavailable or differently named
provider is rejected rather than falling back. The current single-provider
implementation is intentionally classified as
`EXECUTION_PROVIDER_IS_HARD_CODED`, not represented as a multi-provider
capability.

## Sprint 015 real-time DEV execution activity

Sprint 015 adds a safe, live operational view for governed development runs.
`ExecutionRun` and its append-only progress events remain the only canonical
state: the checklist, current phase, blocker, diagnosis, repair, and closure
view are derived from them. During DEV execution Codex JSON output creates
safe event-type projections as it arrives; raw output and secrets are not
stored. The same event sequence serves admin diagnostics and the read-only MCP
activity summary, so ChatGPT cannot receive a separate or invented progress
story. The Django admin view is read-only and no ASF employee, meeting, or
channel layer was introduced.
The repair checklist is verified, not optimistic: a technical failure records
diagnosis and applied repair, then a persisted gate rerun changes the repair
item to completed only after that gate passes. DEV console lines and MCP use
the identical secret-safe event projection.

### Sprint 015 V3 execution continuity

Heartbeat and possible-stall signals are read-time projections of canonical
event timestamps, never manually maintained state. Windows cancellation uses
the native process-tree command and transient SQLite activity-write contention
has bounded retry. The read-only `governance.prepare_codex_handoff` returns
actual durable identifiers and a copyable Codex prompt only after it finds the
approved scope, contract, and run; otherwise it returns an explicit incomplete
state. Provider execution cannot mint governance authority.

## MCP execution internal-error repair

The public execution-token tools now resolve tokens through one validated
canonical lookup. Missing runs return `EXECUTION_NOT_FOUND` and malformed
tokens return `INVALID_EXECUTION_TOKEN` as MCP tool errors, instead of escaping
as JSON-RPC `-32603` internal errors. The repair preserves the governed
cancellation approval and lifecycle checks, makes an already-cancelled run
safe to retry, and contains unexpected transport-boundary failures without
exposing diagnostic details. Evidence is recorded under
`docs/evidence/bridge-ai-bridge-sprint-47744803-a3bf-4963-bea5-47f0c9035fcb/`.

## Conflicting execution-token discovery

For an orchestration blocked by `CONFLICTING_ACTIVE_EXECUTION`, the public
`scope.orchestration_status` response now includes the conflicting active
execution token and lifecycle. This lets an authorized caller use the existing
governed cancellation operation while retaining the conflicting run's original
contract ownership and approval boundary. Evidence is recorded under
`docs/evidence/bridge-ai-bridge-sprint-b97d6773-17ea-4643-b2a5-61965eb4f57c/`.

## Interrupted approval recovery

An interrupted browser, ChatGPT tool session, or MCP connection can now resume
the existing governed approval flow without creating a second approval system.
`scope.resume` exposes only the current canonical scope binding and durable
orchestration state. An authenticated Product Owner resumes through
`scope.resume_confirm_and_execute`, echoing the returned proposal version and
hash; Bridge derives the new caller-bound confirmation reference and reuses the
existing `GovernanceApproval` and `ConversationOrchestration` records. Stale
bindings fail closed and all recovery actions are audited. Evidence is recorded
under `docs/evidence/bridge-ai-bridge-sprint-e626a32e-b18a-415e-bfe2-5d2baf8bf1b2/`.

## EPIC 009 Sprint A orchestrator foundation

The first LLM-assisted assessment boundary is durable and provider-neutral.
OpenAI is the initial runtime adapter, but an LLM recommendation is validated
as untrusted data and then evaluated by deterministic authority policy. The
foundation persists sessions and decisions, exposes only bounded MCP status,
assessment, and cancellation operations, and contains no execution or approval
path. The remaining incident, remediation, validation, and deployment stages
are explicitly planned as separate dependent Sprints.

## Issue #11 Sprint A durable execution queue

Issue #11 Sprint A adds the persisted hand-off between the governed web/MCP
path and provider startup. `ExecutionJob` is one-to-one with the canonical
`ExecutionRun`; it records queued, leased, started, or failed state, worker
identity, expiry, heartbeat and safe provider-attempt metadata. The normal
conversation and remediation dispatch paths enqueue after existing governance
checks; an independent `run_execution_worker` command atomically leases and
starts the job.

The database, rather than Django memory or the autoreloader, owns the queue
state. An expired worker lease is reclaimable without creating a second run or
losing the event history. Sprint B completes the next ordered layer:
`reconcile_execution_jobs` evaluates stale worker/provider state and records
one durable `ExecutionRecoveryAttempt` per decision. An alive provider is
reattached by a replacement worker without a second provider start. A missing
provider can resume the same run only from a complete persisted checkpoint,
using bounded backoff and retry history; absent or unsafe evidence becomes
`RECOVERY_REVIEW_REQUIRED`. Thus a Django reload, worker loss, or provider
interruption cannot leave a stale run indefinitely `RUNNING`. Sprint C
classification/remediation and Sprint D local-wrapper work remain subsequent
Epic #11 work.

### Epic #11 corrective recovery-review lifecycle

An unsafe or missing checkpoint remains explicitly inspectable as
`RECOVERY_REVIEW_REQUIRED`, including the blocker evidence and append-only
recovery history. The canonical recovery reconciler simultaneously terminalizes
the associated run as `BLOCKED_EXTERNAL_INPUT`, with terminal state
`BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`. This preserves the incident
record without retaining an `ACTIVE_STATES` slot that would block the next
same-branch governed execution. The reconciler also performs that transition
idempotently for legacy review-required jobs that were persisted while their
run was still active; it does not retry the provider or fabricate completion.

### Epic #11 corrective worker job isolation

An immutable contract, scope, or governance validation failure at the execution
boundary is a job-level decision, not a reason to terminate the independent
worker. The worker preserves strict pre-provider validation, classifies only
known non-retryable contract/governance failures, persists the affected job as
`REJECTED`, clears its lease, and records structured evidence plus an append-
only rejection event. Its associated run is terminalized as
`FAILED_GOVERNANCE`, so it cannot occupy an active-execution slot. The same
worker then continues to the next queued item. Unclassified errors remain
fail-closed and are not silently downgraded to rejections.

## Provider activity fidelity repair

### Sprint 6 confirmation-binding deployment state

The Remote MCP confirmation predicate accepts explicit, unconditional English
or Hungarian Product Owner confirmations while rejecting conditional or
negative wording. It never trusts client-supplied authority bindings:
scope/version/hash, caller identity, approval reference, and retry key remain
derived and checked by the governed service. The repair is live in staging at
`30648dc0625fef7e6451b0b7ace9bc6422a5c96d`; the one unperformed ChatGPT
Business UI request and in-UI approval remains the exclusive missing
Operational Acceptance fact.

The Codex CLI provider reads stdout and stderr as independent untrusted event
streams. It handles JSON objects, JSON scalar values, malformed JSON, and
plain text without ending the activity reader. Events retain bounded, redacted
message, command, stdout, stderr, exit-code, and file-path data and are stored
with an idempotent provider event identity per run. The read-only execution
surface exposes Activity, Provider Output, and Raw Events views; Raw Events
remain redacted structured payloads, not credential-bearing raw transcripts.

### Sprint 6 provider-completion finalization repair

The historical ChatGPT-originated execution
`218cb756-807c-46d5-8e82-dc19ac210f08` reached a terminal provider event but
had no canonical completion, repository delivery, or deployment receipt. The
provider event now queues deterministic finalization instead of cancelling the
contract as an external-input block. Finalization clears the live PID,
transitions the workspace to `VALIDATING`, inspects the isolated Git state,
records `NO_CHANGE` or missing-completion facts, and schedules bounded
technical recovery. It never manufactures a SHA, delivery, or deployment from
an exit event. The old execution was clean at its baseline and cannot be
truthfully completed retroactively; it remains evidence for the repair and a
fresh actual ChatGPT Business request is required for Sprint 6 Operational
Acceptance.

The staging runtime at that SHA has passed the public health SHA check,
migration plan, dependency check, worker smoke check, and scheduler smoke
check. The first verifier attempt exposed a locked-workspace cleanup exception;
the repair performs the controlled read-only retry and records any persistent
lock as `RETAINED` with a bounded retry, so the scheduler remains live. This
preflight does not substitute for the required Business UI-originated request.

## External governed-execution lifecycle reconciliation

Evidence-backed external or Factory Development Mode work can be admitted into
the canonical lifecycle without a provider run, an execution contract, or
synthetic historical runtime events. The reconciliation verifies the registered
repository, final commit, scope-bound evidence, passing engineering audit and
Product Owner acceptance; it records an additive transition trail from
`RECONCILING` through `PASS` to `ACCEPTED`. Identical retries are idempotent,
while changed or unverifiable input fails closed.

## Sprint C remediation operational knowledge

`TechnicalRemediationLoop` is the durable record for automatic remediation of
an existing parent execution. It accepts only an explicit
`TECHNICAL_REMEDIATION` classification, creates a child `WORK_ITEM` bound to
the parent run and scope, records policy/evidence, and changes the parent to
`REPAIRING`. Completion is allowed only with fresh evidence and a successful
rerun of the failed gate; only then does the original run return to `RUNNING`.
`BUSINESS_DECISION_REQUIRED`, `SECURITY_OR_GOVERNANCE_CONFLICT`,
`EXTERNAL_DEPENDENCY`, and `NON_RECOVERABLE` are deliberately not automatic.
The operation is idempotent; changed retry bindings and incomplete evidence
fail closed. A corrupted published scope file can be re-projected from the
unchanged canonical record, the bounded repair for a deterministic
published-content-hash mismatch.

## Issue #17 Sprint 4 Factory Chat Coding Mode

Coding Mode is a presentation-only, server-rendered view over a canonical
`ExecutionRun`. It derives plain-language lifecycle status, Sprint checklist
progress, matching-Epic execution progress, verification metadata, owner
action/no-action state, recent activity, and optional diagnostics from the
existing lifecycle/activity projections. It must not create a second lifecycle,
browser-side progress record, or provider dispatch path.

## Issue #17 Sprint 5 Factory Chat Memory Mode

The Factory Chat Memory view reuses the existing generic AKB lifecycle and
context-package evidence. Its server builds and records a deterministic,
project-bound package for `factory-chat:memory`, then renders bounded sources,
search results, stale/conflict diagnostics, and read-only repository, roadmap,
and runtime projections. A UI action does not bypass AKB governance:
candidate review, activation with project-bound approval, and rejection are
delegated to the canonical service and append `KnowledgeRevision` records.

## Issue #17 Sprint 6 Factory Chat end-to-end acceptance

The Factory Chat Epic is accepted through a real Chromium mission, rather than
only request-level coverage. The mission proves the project-scoped handoff
from plan to approved AKB Memory package, Orki session, consumed execution
contract, completed run, and Coding projection. It also checks the mobile
single-column Chat surface. This is integration evidence, not a new browser
authority or a claim of direct provider dispatch.

## Sprint D local Codex operational knowledge

Use `prepare_local_codex` (or the `prepare_local_codex` management command)
only with an existing execution token, worker identifier, and the Bridge
platform root. It does not start Codex: it verifies the consumed contract and
scope bindings, then records a durable lease for the exact queued run. Local
workers must heartbeat and checkpoint through the wrapper. On interruption,
the same job enters the established recovery controller; never create another
run or provider execution. Completion requires a verified local Git HEAD and
non-empty evidence manifest. Arbitrary pre-existing local sessions are
explicitly audited as `UNVERIFIED` and cannot be attached.

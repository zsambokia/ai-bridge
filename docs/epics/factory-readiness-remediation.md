# EPIC — AI Bridge Factory Readiness Remediation

**Status:** PROPOSED — Product Owner direction approved  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** `EPIC`  
**Primary task type:** `SELF_DEVELOPMENT`  
**Priority:** P0 / strategic blocker  
**Canonical specification:** this document  
**Baseline verdict:** `NOT READY`  
**Baseline maturity:** `40 / 100`  
**Estimated non-governance human intervention:** approximately `55%`  
**Knowledge durability baseline:** `4.3 / 10`

---

## 1. Product Owner direction

AI Bridge must become a demonstrably autonomous software factory in which Attila remains Product Owner rather than technical dispatcher, runtime operator, recovery engineer, prompt courier, or manual knowledge synchronizer.

The target operating model is:

```text
Attila / Product Owner
→ ChatGPT
→ AI Bridge / Orki
→ governed planning and execution
→ Codex or another governed provider
→ validated repository delivery
→ deployment
→ operational acceptance
→ durable knowledge and roadmap feedback
```

The current system contains important foundations, but the accepted readiness audit concluded that it is not yet ready for an Attila-free technical execution path. This Epic exists to close the complete gap, not merely to improve individual components.

The Epic must be executed as a sequence of ordered, gated Sprints. A later Sprint must not start until the previous Sprint has an evidence-backed PASS result.

The execution rule is:

```text
Sprint 1 PASS
→ Sprint 2
→ Sprint 2 PASS
→ Sprint 3
→ continue in order
→ Epic-level proof
```

Technical failures are not valid final blockers. They must be diagnosed, repaired, regression-tested, and retried within the active Sprint until PASS, unless a genuine Product Owner business or governance decision is required.

---

## 2. Accepted audit baseline

The Epic begins from the following accepted baseline:

- 77 public MCP tools were reported available.
- Contract-bound execution, isolated workspaces, queue/lease handling and Codex CLI integration exist.
- The complete automated test suite passed at the time of audit: `188 / 188`.
- No externally verified ChatGPT Business → MCP → Orki → execution → commit/push → deployment → operational acceptance chain exists.
- The audited database contained execution, job, workspace and MCP audit records, but no persisted Orki session, ownership assessment, orchestration decision, active knowledge entry, or completed technical remediation loop.
- Run, job, lease, provider PID and workspace states were not mutually consistent.
- Repository delivery, deployment and operational acceptance were not proven as one automatic chain.
- Attila still performed material technical dispatch, diagnosis and recovery work.

The baseline must be recorded as canonical evidence and must not be silently softened or reclassified during implementation.

---

## 3. Epic objective

Transform AI Bridge from a governed local execution foundation into a proven autonomous software factory that can:

1. receive business intent through ChatGPT;
2. identify the correct project and repository;
3. retrieve and apply trusted project knowledge;
4. create and maintain plans, roadmaps, Sprints and execution context;
5. route every governed execution through Orki;
6. execute in an isolated and recoverable workspace;
7. survive worker, provider and runtime failures;
8. diagnose and repair routine technical faults autonomously;
9. complete tests, evidence, commit, push and review delivery;
10. deploy and verify the accepted revision;
11. update roadmap and durable knowledge from the accepted result;
12. require Attila only for Product Owner decisions.

---

## 4. Non-negotiable operating principles

### 4.1 Business authority and technical authority

Product Owner authority is required for:

- product intent;
- business priority;
- scope changes;
- governance exceptions;
- accepted risk;
- material cost or commercial commitments;
- destructive or irreversible actions;
- production authority where not already delegated.

AI Bridge must independently handle routine technical work, including:

- diagnosis;
- implementation repair;
- test, lint, type and migration failures;
- stale runtime state;
- provider loss;
- bounded retries;
- evidence correction;
- documentation synchronization;
- non-destructive recovery;
- execution continuation.

### 4.2 Fail the execution attempt, not the factory

One invalid contract, failed workspace, dead provider, failed gate or malformed result must not stop the worker or the wider factory.

```text
item failure
→ durable classification
→ release ownership
→ recover, retry, replace, or terminalize
→ continue queue processing
```

### 4.3 Evidence over implementation claims

A capability is not accepted merely because a model, service, API, admin page, test or document exists. Every critical capability requires runtime or real E2E proof.

### 4.4 No hidden bypass path

Any exceptional internal or bootstrap path must be explicitly classified and audited. It must not masquerade as the canonical managed path.

### 4.5 Living Epic rule

If a Sprint discovers a defect that prevents that Sprint's acceptance criteria, the defect becomes part of the active Sprint. It must not be deferred solely to achieve an artificial PASS.

A new Product Owner decision is required only when remediation would materially expand business scope or cross an explicit governance boundary.

### 4.6 Sequential gate rule

No later Sprint may begin while an earlier Sprint is `FAIL`, `PARTIAL`, `BLOCKED_TECHNICAL`, `RECOVERY_REVIEW_REQUIRED`, or otherwise incomplete.

### 4.7 No technical-stop final state

The only valid Sprint outcomes are:

```text
PASS — READY FOR NEXT SPRINT
BLOCKED — PRODUCT OWNER BUSINESS DECISION REQUIRED
```

`BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE` is allowed only when the missing input is proven external, non-derivable, required for the approved scope, and cannot be replaced by a safe test double or local proving environment without invalidating acceptance.

### 4.8 Repository delivery is part of completion

A Sprint is not complete before:

```text
implementation
→ complete release gates
→ evidence from final state
→ documentation and AKB synchronization
→ commit
→ push
→ exact final SHA
```

### 4.9 Operational acceptance is separate

Engineering acceptance, merge and deployment are not equivalent to operational acceptance. Where the runtime is in Bridge responsibility, the accepted revision must be verified as active and functional.

---

## 5. Cross-Sprint mandatory workflow

Every Sprint must follow this loop:

```text
ASSESS
→ define canonical invariants and acceptance tests
→ implement or repair
→ run targeted tests
→ run full Release Gates
→ run real acceptance scenario
→ collect evidence
→ update roadmap and AKB
→ commit and push
→ independent Sprint audit
```

If any gate fails:

```text
DETECT
→ DIAGNOSE
→ REPAIR
→ REGRESSION TEST
→ RERUN COMPLETE INVALIDATED GATES
→ REPEAT UNTIL PASS
```

The executor must preserve earlier failed evidence rather than rewriting history.

---

# Sprint 1 — Canonical Execution Lifecycle Integrity and Autonomous Recovery

## 6. Sprint 1 objective

Create one deterministic and self-healing lifecycle across:

```text
Scope / Contract
→ ExecutionRun
→ ExecutionJob
→ worker ownership and lease
→ ExecutionWorkspace
→ provider process
→ events and checkpoints
→ validation
→ terminalization
→ retention and cleanup
```

The system must be able to determine the true execution state from durable evidence and repair inconsistencies without routine operator intervention.

## 7. Sprint 1 mandatory assessment

Inspect and document the current implementations for:

- execution state machines;
- jobs and queue claims;
- lease ownership, expiry and fencing;
- worker heartbeat and liveness;
- workspace lifecycle;
- runtime descriptors;
- provider PID and event ingestion;
- checkpoint persistence and validation;
- reconciliation and recovery;
- remediation links;
- retention and cleanup;
- API, admin and dashboard status derivation;
- scheduler and worker deployment topology.

Produce a current-state invariant matrix:

```text
Invariant
Expected state
Current enforcement point
Observed violations
Repair
Test
Evidence
```

## 8. Canonical lifecycle invariants

At minimum enforce and test:

1. A terminal run cannot have an active or claimable job.
2. An active job must have one valid owner, unexpired lease and fencing token.
3. A provider process may exist only for an execution with a valid active attempt.
4. A live provider PID must belong to the persisted workspace and runtime descriptor.
5. A dead PID must not leave a workspace `IN_USE` indefinitely.
6. A terminal execution must not retain a workspace as active.
7. `RETAINED` must represent an explicit retention policy and expiry/reason.
8. `WAITING_FOR_PROVIDER` is invalid when provider launch never occurred.
9. A provider may not start twice for the same active attempt.
10. A workspace may not be deleted while provider, lease or evidence retention requires it.
11. A job failure must release or expire ownership safely and must not terminate the worker loop.
12. Reconciliation must be idempotent and safe under concurrent invocations.
13. Control-plane truth must not depend solely on a process-local in-memory value.
14. Admin, API and dashboard must derive status from the same canonical lifecycle service.

## 9. Recovery classification

Implement deterministic classification for at least:

```text
HEALTHY_ACTIVE
COMPLETED_PENDING_VALIDATION
STALE_LEASE
DEAD_PROVIDER_RECOVERABLE
DEAD_PROVIDER_RESTARTABLE
WORKSPACE_RECOVERABLE
WORKSPACE_CORRUPT_REPLACEMENT_REQUIRED
CONTRACT_INTEGRITY_FAILURE
NON_RECOVERABLE_EXECUTION_FAILURE
EXTERNAL_DEPENDENCY_BLOCKED
TERMINAL_CLEANUP_PENDING
```

The classifier must return:

- classification;
- supporting facts;
- evidence references;
- permitted next actions;
- retry budget;
- whether Product Owner involvement is allowed or forbidden.

## 10. Checkpoint and Bridge-owned recovery state

A resumable checkpoint must not depend only on provider cooperation.

AI Bridge must create or update canonical recovery state at least when:

```text
WORKSPACE_READY
PROVIDER_STARTED
PROVIDER_ACTIVITY_RECEIVED
SOURCE_TREE_CHANGED
VALIDATION_STARTED
VALIDATION_COMPLETED
PROVIDER_COMPLETED
```

The recovery snapshot must safely contain, where available:

- baseline commit;
- working tree status and diff fingerprint;
- changed file list;
- completed and remaining lifecycle phases;
- latest successful gate;
- provider summary or bounded event reference;
- runtime descriptor fingerprint;
- workspace verification result;
- next safe action.

Secrets and hidden chain-of-thought must never be stored.

## 11. Retry and replacement execution

Implement bounded and auditable retry behavior:

- no duplicate provider;
- PID and lease verification before retry;
- prior attempt evidence retained;
- stable idempotency key;
- configurable retry budget and backoff;
- safe reuse of workspace only after verification;
- replacement workspace when corruption is proven;
- new attempt or equivalent durable attempt identity;
- no infinite remediation recursion.

## 12. Worker and reconciler survival

Prove that:

- one bad execution does not stop the worker;
- one reconciliation failure does not stop later reconciliation cycles;
- terminalization releases leases;
- the next queued execution is processed;
- stale jobs are corrected automatically;
- provider loss does not permanently block the queue.

## 13. Workspace retention and cleanup

Implement deterministic cleanup rules:

- terminal PASS workspaces retained until evidence is durable, then cleaned;
- failed or review-required workspaces retained for configured diagnosis periods;
- active workspace deletion rejected;
- stale PIDs and expired retention reconciled;
- repository worktree, venv and application DB removed safely;
- archive manifest retained after physical deletion;
- cleanup constrained to approved workspace root;
- cleanup idempotent and event-producing.

## 14. Sprint 1 required fault-injection tests

At minimum:

1. provider exits before first provider checkpoint;
2. provider exits after Bridge-owned recovery snapshot;
3. worker dies during workspace provisioning;
4. worker dies after provider start;
5. provider PID disappears;
6. lease expires while old worker is still present;
7. old fencing token attempts a write after reclaim;
8. terminal run retains a `STARTED` job;
9. workspace points to a dead PID;
10. workspace metadata is stale but repository is recoverable;
11. workspace is corrupt and must be replaced;
12. duplicate reconciler invocation;
13. duplicate provider launch attempt;
14. retry budget exhaustion;
15. next queue item runs after prior item failure;
16. cleanup refuses active workspace;
17. cleanup removes only approved paths;
18. admin/API/dashboard report identical canonical state.

## 15. Sprint 1 real acceptance scenario

Run a real local managed execution in an isolated workspace and deliberately interrupt the provider or worker. The system must:

```text
create governed run
→ claim job
→ provision workspace
→ start provider
→ persist activity
→ interruption occurs
→ detect stale ownership/provider
→ classify recovery
→ resume or safely replace attempt
→ complete validation
→ release lease
→ terminalize correctly
→ retain then clean workspace
→ worker processes another queued item
```

## 16. Sprint 1 PASS criteria

- [ ] All canonical lifecycle invariants are machine-enforced.
- [ ] Existing stale run/job/workspace state can be diagnosed and safely reconciled through canonical services.
- [ ] No terminal execution remains paired with an active job or lease.
- [ ] No dead provider PID leaves a workspace indefinitely active.
- [ ] Retry and replacement behavior is bounded and auditable.
- [ ] Worker survives per-item failure.
- [ ] Admin, API and dashboard agree.
- [ ] Fault-injection suite passes.
- [ ] Real interruption/recovery E2E passes.
- [ ] Full repository Release Gates pass.
- [ ] Evidence, roadmap and AKB are updated.
- [ ] Changes are committed and pushed.

Sprint 2 must not start before Sprint 1 PASS.

---

# Sprint 2 — Orki as the Mandatory Orchestration Gate

## 17. Sprint 2 objective

Make Orki the mandatory, durable and auditable decision layer for every governed execution initiated from ChatGPT or the normal AI Bridge workflow.

The canonical chain must be:

```text
ChatGPT / MCP request
→ OrchestrationSession
→ project and intent resolution
→ OwnershipAssessment
→ governed Context Package
→ OrchestrationDecision
→ proposal / scope
→ contract
→ ExecutionRun
→ workspace
→ provider
→ evidence
```

## 18. Mandatory persisted orchestration data

Every normal governed execution must have, directly or through existing canonical equivalents:

- orchestration session ID;
- request and actor binding;
- selected project;
- selected repository;
- ownership assessment;
- selected runtime profile;
- selected provider;
- selected knowledge/context package hash;
- authority classification;
- policy result;
- concise decision rationale;
- linked proposal, contract and run;
- final orchestration outcome.

Do not persist hidden chain-of-thought.

## 19. Bypass policy

Identify every path that can currently create a contract or execution without Orki.

Each path must be:

- routed through Orki;
- or explicitly classified as an internal maintenance/bootstrap path with separate policy, event type and admin visibility.

A bootstrap path may not be counted as proof of normal ChatGPT → Orki execution.

## 20. Ownership assessment

The assessment must prove:

- project ownership;
- repository ownership;
- target component where possible;
- self-development versus external project;
- allowed cross-project relationships;
- confidence and evidence;
- ambiguity handling;
- reason for escalation when ownership is not determinable.

## 21. Decision enforcement

The execution contract and run must bind to the orchestration decision and context hash. Dispatch must fail closed if:

- project differs;
- repository differs;
- context package is missing or invalid;
- decision was superseded;
- authority classification does not permit execution;
- contract and decision hashes do not match.

## 22. Orki admin and API visibility

The Product Owner must be able to navigate:

```text
OrchestrationSession
→ OwnershipAssessment
→ OrchestrationDecision
→ Contract
→ ExecutionRun
→ Workspace
→ Provider activity
→ Evidence
```

The previously empty admin collections must contain records after the real acceptance scenario, or the implementation must explicitly migrate to a different canonical representation and remove misleading unused surfaces.

## 23. Sprint 2 required tests

At minimum:

1. ChatGPT/MCP request creates an orchestration session;
2. ownership assessment selects AI Bridge for self-development;
3. ownership assessment selects `bridge-demo` for its own work;
4. ambiguous ownership requires Product Owner decision;
5. technical issue does not require Product Owner decision;
6. Orki decision binds project, repository, provider and runtime profile;
7. contract mismatch is rejected;
8. bypass attempt is rejected or explicitly classified;
9. retry does not duplicate session/decision;
10. admin/API linkage is complete;
11. provider activity is traceable back to session;
12. context package hash is persisted and verifiable.

## 24. Sprint 2 real acceptance scenario

Start one AI Bridge self-development request through the ChatGPT-facing MCP surface. Prove persisted records for the entire Orki chain and complete a harmless governed change in an isolated workspace.

Then run a second ownership-only scenario for `bridge-demo` and prove Orki selects a different project, repository and runtime profile without cross-project context leakage.

## 25. Sprint 2 PASS criteria

- [ ] Orki is mandatory for normal governed execution.
- [ ] Orchestration session, assessment and decision records are created.
- [ ] Every record links to contract, run and evidence.
- [ ] No silent bypass remains.
- [ ] Project and repository context switching is proven.
- [ ] Admin and API provide full traceability.
- [ ] Full Release Gates and real acceptance scenarios pass.
- [ ] Evidence, roadmap and AKB are updated.
- [ ] Changes are committed and pushed.

Sprint 3 must not start before Sprint 2 PASS.

---

# Sprint 3 — Durable AKB and Roadmap Feedback Loop

## 26. Sprint 3 objective

Turn the existing knowledge foundation into active, durable and reused organizational memory.

The system must close this loop:

```text
conversation and planning
→ knowledge candidate
→ governed review
→ active project knowledge
→ deterministic retrieval
→ Orki Context Package
→ execution use
→ accepted result
→ knowledge and roadmap update
```

## 27. Knowledge capture

Implement governed capture from at least:

- accepted Product Owner decisions;
- project assessments;
- roadmap and planning changes;
- architecture decisions;
- accepted Sprint closure;
- incidents and remediation;
- deployment and operational acceptance;
- known limitations and runbooks.

Automatic processes may create candidates. Activation must follow existing approval policy.

## 28. Retrieval and proof of use

Every context-bound execution must record:

- retrieved entry IDs;
- source versions;
- stale or conflicting warnings;
- retrieval query or intent;
- context package hash;
- which decision or execution consumed the package.

The system must distinguish:

- knowledge exists;
- knowledge was retrieved;
- knowledge was actually included in the decision context;
- the accepted result caused a knowledge update.

## 29. Roadmap lifecycle

Create or complete the canonical lifecycle:

```text
roadmap item
→ Epic
→ Sprint
→ contract
→ execution
→ evidence
→ commit / merge
→ deployment
→ operational acceptance
→ roadmap progress update
```

Required roadmap behavior:

- project-scoped source of truth;
- dependencies and sequencing;
- proposed, approved, active, completed, blocked and superseded states;
- evidence and final SHA links;
- engineering versus operational completion distinction;
- automatic update candidate after accepted work;
- no silent completion based only on provider report.

## 30. Freshness and conflict handling

Implement or prove:

- review due and stale indicators;
- source revision comparison;
- contradictory active knowledge detection;
- deterministic precedence rules;
- Product Owner escalation for unresolved business conflict;
- technical remediation for machine-detectable stale implementation facts.

## 31. Two-session reuse acceptance

Mandatory real proof:

```text
Session A
→ record and approve a project decision
→ close session

Session B
→ new request requires that decision
→ Orki retrieves it automatically
→ cites the source entry/version
→ applies it without asking Attila again
→ execution and evidence record the context hash
```

Also prove project isolation using an unrelated project context.

## 32. Sprint 3 PASS criteria

- [ ] Active platform and project knowledge entries exist.
- [ ] Accepted decisions create governed knowledge candidates.
- [ ] Review and activation work.
- [ ] Orki consumes deterministic Context Packages.
- [ ] Retrieval and actual use are auditable.
- [ ] Two-session reuse proof passes.
- [ ] Cross-project leakage test passes.
- [ ] Roadmap updates from accepted delivery and operational state.
- [ ] Staleness and conflict behavior is tested.
- [ ] Full Release Gates pass.
- [ ] Evidence, roadmap and AKB are updated.
- [ ] Changes are committed and pushed.

Sprint 4 must not start before Sprint 3 PASS.

---

# Sprint 4 — Autonomous Repository Delivery

## 33. Sprint 4 objective

Prove that a governed execution can autonomously produce a complete repository delivery without manual code copying or separate Codex prompting.

Required chain:

```text
Orki decision
→ contract
→ isolated execution
→ code change
→ tests and Release Gates
→ evidence
→ commit
→ push
→ PR or governed main publication
→ final SHA verification
```

## 34. Delivery policy

Implement deterministic policy for:

- branch selection;
- workspace commit;
- push destination;
- PR creation or main-only publication;
- force-push prohibition;
- conflict detection;
- review requirement;
- final SHA binding;
- closure only after remote verification.

The provider must never claim completion with only a dirty working tree.

## 35. Independent validation

A component other than the implementing provider must verify:

- changed files are within scope;
- no unrelated changes;
- all gates passed from final state;
- evidence matches final commit;
- commit exists remotely;
- PR or main state is correct;
- contract, orchestration decision and final SHA remain bound;
- provider did not self-approve.

## 36. Sprint 4 required scenarios

At minimum:

1. successful isolated change, commit and push;
2. push rejected because remote moved, followed by safe reconciliation;
3. prohibited force push rejected;
4. provider leaves dirty tree without commit and validation rejects completion;
5. final SHA differs from evidence and closure fails;
6. unrelated file change detected;
7. PR path and governed main-only path both tested where supported;
8. worker remains healthy after delivery failure.

## 37. Sprint 4 PASS criteria

- [ ] Real provider performs a scoped code change.
- [ ] Complete gates pass.
- [ ] Evidence is generated from final state.
- [ ] Commit and push are automatic and verified.
- [ ] PR or governed publication is created as policy requires.
- [ ] Final SHA is bound to closure.
- [ ] Manual repository intervention is not required.
- [ ] Full Release Gates pass.
- [ ] Roadmap and AKB reflect delivered state.

Sprint 5 must not start before Sprint 4 PASS.

---

# Sprint 5 — Deployment and Operational Acceptance

## 38. Sprint 5 objective

Implement and prove the complete post-delivery lifecycle:

```text
accepted revision
→ merge or intended branch state
→ deployment
→ migration and dependency application
→ worker/scheduler/runtime health
→ smoke test
→ operational acceptance
→ roadmap and AKB feedback
```

## 39. Deployment control plane

Implement or complete deterministic deployment primitives for the accepted proving environment:

- deployment plan;
- exact commit/artifact binding;
- target environment identity;
- authority check;
- deployment execution;
- migration/dependency result;
- runtime build SHA;
- health verification;
- rollback plan;
- deployment receipt;
- operational acceptance result.

Direct manual `gcloud` commands may remain an emergency runbook but must not be the canonical autonomous path.

## 40. Operational acceptance checks

At minimum verify:

- intended revision is running;
- schema migrations are applied;
- required runtime dependencies exist;
- API health is valid;
- worker, scheduler, reconciler and cleanup services are operating;
- smoke test proves the delivered capability;
- runtime state is not stale or contradictory;
- rollback target exists.

## 41. Remediation on operational failure

Ordinary deployment and runtime faults must trigger technical remediation:

```text
verify failure
→ classify
→ collect evidence
→ repair deployment/config/migration/runtime
→ redeploy or rerun check
→ preserve failed attempt evidence
→ repeat until PASS or genuine external/business boundary
```

## 42. Sprint 5 PASS criteria

- [ ] Deployment is reproducible and bound to final SHA.
- [ ] Runtime exposes or otherwise proves revision identity.
- [ ] Migration and dependency verification pass.
- [ ] Worker/scheduler/reconciler health pass.
- [ ] Smoke test passes in target environment.
- [ ] Operational Acceptance is separate and explicit.
- [ ] Failed operational check triggers autonomous remediation.
- [ ] Rollback is tested in a safe environment.
- [ ] Evidence, roadmap and AKB are updated.

Sprint 6 must not start before Sprint 5 PASS.

---

# Sprint 6 — Complete ChatGPT → Factory End-to-End Proof

## 43. Sprint 6 objective

Prove the actual Product Owner experience through the configured ChatGPT connection.

The proving request must be business-oriented and must not contain a handcrafted Codex implementation prompt.

Example intent:

> Assess the current `bridge-demo` project, propose the next small improvement, update the plan, implement the approved change, test it, deliver it, verify it in the target runtime, and preserve the resulting knowledge.

## 44. Mandatory E2E chain

Prove, with linked durable IDs:

```text
ChatGPT Business request
→ authenticated MCP call
→ OrchestrationSession
→ OwnershipAssessment
→ Context Package and roadmap retrieval
→ OrchestrationDecision
→ proposal and Product Owner approval
→ contract
→ run and job
→ isolated workspace and runtime bootstrap
→ real Codex provider
→ implementation
→ tests and evidence
→ commit and push
→ deployment
→ operational acceptance
→ roadmap update
→ AKB update
→ later retrieval
```

## 45. Product Owner interaction constraint

During the proving scenario Attila may:

- choose or confirm business scope;
- approve the reviewed proposal;
- accept or reject the result.

Attila must not need to:

- write a Codex prompt;
- start a worker manually;
- diagnose logs;
- repair a lease;
- restart a provider;
- commit or push;
- run deployment commands;
- manually update roadmap or AKB.

## 46. Sprint 6 PASS criteria

- [ ] The request originates through the actual configured ChatGPT connection.
- [ ] Authentication and actor binding are proven without exposing secrets.
- [ ] Orki chain is complete.
- [ ] Relevant prior knowledge is retrieved and used.
- [ ] Real provider performs the change.
- [ ] Complete delivery and operational acceptance pass.
- [ ] Roadmap and AKB update automatically through governed candidates.
- [ ] Attila performs Product Owner actions only.
- [ ] All IDs and evidence are cross-linked.

Sprint 7 must not start before Sprint 6 PASS.

---

# Sprint 7 — Autonomous Technical Remediation and Self-Healing Proof

## 47. Sprint 7 objective

Prove that AI Bridge can independently solve routine technical failures across the complete factory chain and resume the original work.

## 48. Controlled failure catalogue

Inject safe and deterministic failures covering at least:

- stale lease;
- dead provider PID;
- worker restart;
- corrupt or incomplete workspace;
- dependency installation failure;
- migration failure in workspace;
- test or lint failure;
- malformed provider event;
- push conflict;
- deployment revision mismatch;
- failed smoke test;
- stale or conflicting knowledge context.

## 49. Required remediation loop

For every in-policy technical failure:

```text
incident detected
→ evidence persisted
→ Orki ownership assessment
→ technical authority classification
→ remediation plan
→ governed repair execution
→ independent validation
→ invalidated gates rerun
→ original workflow resumes
→ final PASS
```

The Product Owner must not be asked a technical question.

A separate controlled scenario must prove that a genuine business decision is correctly escalated rather than guessed.

## 50. Sprint 7 PASS criteria

- [ ] Technical incidents create durable remediation records.
- [ ] Ownership and authority classification are correct.
- [ ] Routine repair does not require Product Owner approval.
- [ ] Repair is bounded and avoids recursive loops.
- [ ] Independent validation confirms the repair.
- [ ] Origin workflow resumes from checkpoint.
- [ ] Multiple controlled failures reach final PASS.
- [ ] Genuine business scenario escalates concisely.
- [ ] Full Release Gates and evidence pass.

Sprint 8 must not start before Sprint 7 PASS.

---

# Sprint 8 — Final Factory Readiness Audit and Attila-Role Acceptance

## 51. Sprint 8 objective

Repeat the readiness audit against the final system and prove that the baseline blockers are closed.

## 52. Mandatory re-audit dimensions

Reassess at least:

- ChatGPT/MCP connection;
- Product Owner experience;
- Orki orchestration;
- project and context selection;
- AKB capture, retrieval and reuse;
- roadmap lifecycle;
- governance and contract integrity;
- execution lifecycle;
- worker and recovery;
- isolated workspace;
- provider integration;
- remediation;
- repository delivery;
- deployment and operational acceptance;
- admin/UI transparency.

## 53. Final maturity scoring

Use the same scoring model and report movement from the accepted baseline:

```text
Baseline maturity: 40 / 100
Baseline human technical intervention: approximately 55%
Baseline knowledge durability: 4.3 / 10
```

The final report must explain every score with evidence. Automated test count alone is insufficient.

## 54. Final acceptance scenario

Run at least one complete external-project change and one AI Bridge self-development change through the canonical managed path.

Then start a new ChatGPT session and ask for project status. The response must derive current state from roadmap, AKB, repository delivery and operational evidence without reconstructing the project manually from chat history.

## 55. Sprint 8 PASS criteria

- [ ] Every earlier Sprint remains PASS under regression testing.
- [ ] No active lifecycle invariant violations exist.
- [ ] Orki records are non-empty and linked to real runs.
- [ ] Active knowledge is retrieved and reused.
- [ ] Roadmap reflects actual engineering and operational state.
- [ ] Real delivery and operational acceptance are repeatable.
- [ ] Autonomous remediation is proven.
- [ ] Attila is required only for Product Owner decisions.
- [ ] Final readiness verdict is evidence-backed.

---

## 56. Cross-Sprint Release Gates

Every Sprint must run all repository-resolved gates. At minimum, where present:

```text
Django system check
migration drift check
complete pytest suite
ruff
mypy
canonical scope validation
contract and API schema validation
evidence integrity validation
frontend tests/build when affected
security and secret-redaction checks
Sprint-specific integration tests
real local or remote acceptance scenario
```

Partial or targeted test success may guide remediation but cannot close a Sprint.

---

## 57. Evidence requirements

Create a canonical evidence root for the Epic, using repository conventions. Each Sprint must retain:

- baseline and final commit SHA;
- exact approved Sprint scope and hash/authority reference;
- current-state assessment;
- changed files;
- migration evidence;
- automated test and gate results;
- real acceptance execution IDs;
- Orki session, ownership and decision IDs where applicable;
- contract, run, job, workspace and provider attempt IDs;
- runtime descriptor fingerprint;
- provider activity and bounded logs;
- failure and remediation timeline;
- repository delivery proof;
- deployment and operational acceptance proof;
- roadmap update reference;
- AKB candidate/entry references;
- known limitations;
- closure report.

Failed attempts must remain auditable.

---

## 58. Maturity targets

These are expected minimum directional targets, not substitutes for acceptance:

| Stage | Expected maturity |
|---|---:|
| Accepted baseline | 40 |
| Sprint 1 | 50+ |
| Sprint 2 | 60+ |
| Sprint 3 | 70+ |
| Sprint 4 | 78+ |
| Sprint 5 | 85+ |
| Sprint 6 | 90+ |
| Sprint 7 | 95+ |
| Sprint 8 | evidence-backed final score |

A numerical target cannot override a failed critical capability.

---

## 59. Explicit prohibitions

The Epic must not be closed by:

- mocked provider-only proof for a required real scenario;
- manually editing execution state to fabricate recovery;
- manually setting Orki, roadmap or AKB records without the canonical service path;
- treating a local dirty tree as delivered work;
- omitting commit or push;
- counting a bootstrap execution as proof of the normal managed path;
- sharing mutable repository, venv or application DB between active executions;
- weakening governance, hash validation, release gates or evidence rules;
- silently deleting failed evidence;
- claiming operational acceptance without target-runtime verification;
- asking the Product Owner to solve routine technical failures;
- starting a later Sprint before the previous Sprint passes.

---

## 60. Product Owner decision protocol

When a genuine Product Owner decision is required, the system must return one concise decision request containing:

- verified facts;
- why the question is business/governance rather than technical;
- available options;
- consequences and risks;
- recommended option;
- exact scope authorized by each option.

Do not return vague requests such as “manual intervention required.”

---

## 61. Epic completion criteria

The Epic is complete only when all eight Sprints have evidence-backed PASS results and the complete target chain is repeatably proven:

```text
Attila / Product Owner
→ ChatGPT
→ authenticated MCP
→ Orki and durable knowledge
→ governed contract and execution
→ isolated workspace
→ real provider
→ implementation and independent validation
→ commit / push / review delivery
→ deployment
→ operational acceptance
→ roadmap and AKB feedback
→ later reuse
```

The final acceptable verdict is:

```text
PASS — AI BRIDGE AUTONOMOUS SOFTWARE FACTORY READINESS PROVEN
```

The final audit may use the maturity label:

```text
AUTONOMOUSLY READY
```

only when Attila's routine technical dispatcher and recovery role has been eliminated by evidence, not merely reduced in documentation.

Otherwise the Epic remains open and the failing Sprint must continue through diagnosis, remediation and revalidation.

---

## 62. Codex execution instruction

Treat this document as one Living Epic containing eight strictly ordered Sprints.

For each Sprint:

1. resolve or obtain the exact approved Sprint authority required by repository governance;
2. assess the current implementation before mutation;
3. implement the smallest coherent canonical repair;
4. preserve unrelated work;
5. run targeted tests and the complete Release Gates;
6. run the required real acceptance scenario;
7. diagnose and repair every technical failure within scope;
8. repeat until PASS;
9. generate final-state evidence;
10. update roadmap and governed knowledge;
11. commit and push;
12. perform independent Sprint audit;
13. start the next Sprint only after PASS.

Stop only for a genuine Product Owner business or governance decision, a proven unsafe/destructive boundary, or a genuinely unavailable external credential/access dependency that cannot be safely substituted for the required acceptance.

Do not stop because the managed runtime, worker, provider, recovery, evidence, delivery or deployment implementation is technically defective. Repairing those defects is the purpose of this Epic.
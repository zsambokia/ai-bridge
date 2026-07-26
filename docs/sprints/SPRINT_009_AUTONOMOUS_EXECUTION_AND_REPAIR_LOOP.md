# Sprint 009 — Autonomous Execution and Repair Loop

**Status:** APPROVED FOR CODEX EXECUTION  
**Execution level:** SPRINT  
**Task type:** FEATURE  
**Target branch:** `main`

## 1. Goal

Implement and prove the first governed autonomous execution loop in AI Bridge.

The Sprint must enable Bridge to take one approved execution package and tiered Execution Contract, start a real Codex execution through a canonical dispatcher boundary, observe the run, collect progress and result state, automatically diagnose and repair ordinary technical failures, rerun all invalidated gates, synchronize documentation and AKB, and close with truthful evidence without routine Product Owner intervention.

The Sprint must not create a fake execution simulator. It must use a real Codex-capable execution boundary or, if the repository does not yet contain one, implement the smallest canonical adapter needed to create and track a real execution request and its returned state.

## 2. Product outcome

The intended Product Owner experience is:

```text
Approved Sprint and contract are ready.
Start the implementation.
```

Bridge then performs the technical cycle:

```text
resolve authorized execution
→ bind repository, branch, baseline, contract and workspace
→ start Codex
→ observe progress
→ collect repository changes and gate output
→ detect failures
→ diagnose root cause
→ repair within Sprint scope
→ rerun failed and invalidated dependent gates
→ update documentation and AKB
→ bind final evidence and commit
→ return PASS or one legitimate blocker
```

The Product Owner must not become technical support for the run.

## 3. Constitutional authority

This Sprint is bound by:

```text
docs/constitution/BRIDGE_CONSTITUTION.md
```

In particular:

- Article III — Assessment First;
- Article VII — Technical Ownership and Reserved Product Owner Decisions;
- Article VII.1 — Product Owner intervention protocol;
- Article IX — Self-Closing Sprint Lifecycle;
- Article X — Mandatory Release Gates;
- Article XI — Mandatory Repair-and-Rerun Loop;
- Article XII — Evidence Integrity and Freshness;
- Article XIII — Knowledge Synchronization and AKB Closure;
- Article XIV — No Fake Success;
- Article XV — Additive Recovery and Lifecycle Integrity.

Codex must fix technical problems discovered during implementation or testing itself. Test failures, migration failures, lint failures, type failures, build failures, browser failures, dependency failures, configuration defects, malformed technical handoffs, evidence generation defects, and documentation drift are not Product Owner decisions.

## 4. Scope

### 4.1 Canonical execution-run model

Implement or complete one canonical execution-run model that records at least:

- stable execution run identifier;
- selected Project;
- repository and branch;
- baseline commit;
- Execution Contract identifier and hash;
- execution package or preparation identifier;
- requested executor/provider;
- workspace or remote execution identifier;
- lifecycle state;
- start and end timestamps;
- current phase;
- attempt count;
- current blocker, if any;
- final commit;
- final terminal state;
- evidence root;
- audit linkage.

Minimum lifecycle:

```text
REQUESTED
→ STARTING
→ RUNNING
→ VALIDATING
→ REPAIRING
→ DOCUMENTING
→ CLOSING
→ COMPLETED
```

Legitimate alternate terminal states:

```text
BLOCKED_BUSINESS_DECISION
BLOCKED_EXTERNAL_INPUT
FAILED_GOVERNANCE
CANCELLED
```

Ordinary technical failure is not a terminal state while a safe repair remains possible.

### 4.2 Executor/provider boundary

Create or reuse a replaceable executor-provider interface.

It must support:

- start execution;
- query execution status;
- retrieve structured progress/events;
- retrieve final result or failure details;
- cancel when explicitly authorized;
- identify the external execution/workspace;
- distinguish provider failure from repository/test failure.

The canonical domain must not depend directly on one UI, terminal process, or hardcoded Codex environment.

If Codex Cloud, GitHub-backed Codex execution, or another currently available Codex interface is used, isolate it behind this provider boundary and document the exact integration limitations.

### 4.3 Governed start conditions

An execution may start only when all required conditions pass:

- Project is active and ready;
- repository and branch match the contract;
- baseline satisfies the contract rule;
- contract is valid and in the required lifecycle state;
- approval requirements are satisfied;
- execution package is present and bound;
- no conflicting active execution owns the same protected scope;
- required credentials and external access are available;
- workspace is clean or unrelated work is safely isolated;
- idempotency prevents duplicate starts.

A successful start must create durable audit and execution-run records before external execution is treated as active.

### 4.4 Progress and event collection

Persist structured execution events such as:

```text
PREFLIGHT_COMPLETED
EXECUTOR_STARTED
ASSESSMENT_COMPLETED
FILES_CHANGED
TARGETED_TEST_STARTED
TARGETED_TEST_FAILED
ROOT_CAUSE_IDENTIFIED
REPAIR_APPLIED
GATE_RERUN
RELEASE_GATES_PASSED
DOCUMENTATION_UPDATED
AKB_UPDATED
FINAL_COMMIT_CREATED
EVIDENCE_BOUND
EXECUTION_COMPLETED
```

Events must be ordered, timestamped, scoped to one execution run, and safe for later UI or MCP projection.

Do not store secrets or unbounded raw logs in operational records.

### 4.5 Autonomous repair controller

Implement one deterministic repair controller for ordinary technical failures.

Required loop:

```text
DETECT
→ DIAGNOSE
→ CLASSIFY
→ PLAN REPAIR
→ APPLY REPAIR
→ RERUN FAILED GATE
→ RERUN INVALIDATED DEPENDENT GATES
```

The controller must classify failures at least as:

- repository or implementation defect;
- test defect caused by changed intended behaviour;
- migration defect;
- dependency or environment defect;
- configuration defect;
- build/lint/type defect;
- browser or integration defect;
- evidence/documentation defect;
- provider/infrastructure defect;
- reserved Product Owner decision;
- unavailable external input;
- governance violation.

The controller may not weaken acceptance criteria, delete meaningful tests, mark tests skipped, bypass migrations, suppress errors, loosen types, remove gates, or rewrite evidence merely to obtain PASS.

### 4.6 Retry and loop safety

Prevent infinite or silent retry loops.

Implement configurable limits for:

- repeated identical failure signature;
- total repair attempts;
- provider start attempts;
- gate reruns;
- elapsed execution time where applicable.

When a limit is reached, perform root-cause reassessment before any further attempt.

A run may block only if the final classification meets one of the Constitution-reserved categories. The blocker record must satisfy Article VII.1.

### 4.7 Product Owner intervention boundary

The execution system must not ask the Product Owner for routine technical guidance.

A Product Owner request may be emitted only for:

- unresolved business or product behaviour;
- material UX or scope choice;
- legal, privacy, compliance, contractual, pricing, financial, or brand decision;
- destructive or production-risk authority;
- unavailable credential, secret, permission, access, or external fact;
- material contradiction in binding rules.

Every intervention request must contain:

- category;
- exact question or external action;
- why Codex cannot decide or perform it;
- evidence of attempted diagnosis and repair;
- smallest required response;
- continuation token or exact resumable execution state.

### 4.8 Release-gate orchestration

Resolve required gates from:

- `.bridge/project.yaml`;
- the approved Sprint;
- the Execution Contract policy;
- affected technology components;
- changed files and invalidation rules.

The run must distinguish:

- targeted diagnostic validation;
- mandatory repository-wide Release Gates;
- frontend gates;
- backend gates;
- deployment/runtime gates;
- evidence integrity gates.

After any repair, rerun every gate invalidated by that repair.

### 4.9 Repository mutation and finalization

The execution loop must:

- preserve unrelated work;
- operate on the canonical `main` branch under the current constitutional policy;
- never reset or rewrite shared history;
- create repair commits rather than hiding prior failures;
- verify `HEAD`, `origin/main`, and clean status at closure;
- bind the final commit to execution and evidence records;
- distinguish push success from technical PASS and Product Owner acceptance.

### 4.10 Documentation, AKB, and evidence closure

The execution is not complete until:

- affected documentation is updated;
- AKB/current state is synchronized;
- knowledge consistency is verified;
- final evidence is generated from the final repository state;
- the contract and execution run are closed canonically;
- every affected gate has current PASS evidence.

## 5. MCP and API surface

Assess whether the Sprint 007 tools are sufficient.

At minimum, Bridge must expose or internally support:

- request/start an execution;
- get execution run status;
- list execution events;
- continue after a valid Product Owner response or external input;
- cancel with explicit authorization;
- retrieve final handoff/evidence summary.

Prefer extending existing `execution.request_start` and status capabilities rather than creating overlapping tools.

Any new public tool must use the governed registry, strict schemas, authorization classification, audit, idempotency, and bounded output.

## 6. Assessment-first requirement

Before implementation, inspect and document:

1. current `execution.request_start` behaviour;
2. existing execution preparation and contract lifecycle services;
3. any Codex, GitHub, Cloud Workspace, job, queue, worker, subprocess, webhook, or dispatcher integration;
4. current audit and idempotency models;
5. existing progress/event models;
6. repository-provider and workspace abstractions;
7. Release Gate configuration and execution code;
8. evidence generation and final commit binding;
9. current deployment architecture and external credentials;
10. missing authority or provider capability that could prevent a truthful real execution proof.

Reuse canonical components. Do not implement a second execution-start path, second contract lifecycle, second project resolver, or second gate engine.

## 7. Required proving execution

This Sprint must include one bounded real proving execution against the AI Bridge repository or another explicitly approved non-production-critical Project.

The proving task must be small enough to complete safely but must cause at least one real repository change and execute the full loop.

It must demonstrate:

- real authorized start;
- real repository mutation;
- at least one targeted test;
- full Release Gates;
- documentation or AKB update where required;
- final evidence and commit binding.

The proving scenario must also demonstrate at least one repair cycle. This may use a controlled, intentionally introduced test fixture or temporary failure mechanism only if:

- it is explicitly scoped and documented;
- it cannot reach production accidentally;
- the repair is performed through the same real repair controller;
- the temporary fault is fully removed;
- final gates run from the repaired final state;
- no fake PASS is reported.

Do not damage or weaken existing production code merely to manufacture a failure.

## 8. Required automated tests

Add tests for at least:

1. execution-run lifecycle transitions;
2. duplicate start idempotency;
3. invalid contract or baseline rejection;
4. conflicting active execution rejection;
5. provider start and status adapter behaviour;
6. ordered progress-event persistence;
7. failure classification;
8. automatic repair-loop continuation;
9. invalidated dependent-gate reruns;
10. retry-limit and repeated-signature handling;
11. legitimate Product Owner blocker generation;
12. rejection of routine technical escalation;
13. safe continuation after supplied external input;
14. cancellation authorization;
15. final commit and evidence binding;
16. no secret leakage;
17. no gate weakening or test deletion as a repair strategy;
18. full end-to-end proving execution with one real repair cycle.

## 9. Release Gates

Run every repository-wide gate resolved from `.bridge/project.yaml`, every policy-resolved gate, and all Sprint-specific tests.

At minimum, if still canonical:

```text
python manage.py makemigrations --check --dry-run
pytest -q
ruff check .
ruff format --check .
mypy .
git diff --check
```

If a required command is unavailable or outdated, Codex must assess and repair the canonical project configuration rather than silently omitting the gate.

All technical failures follow:

```text
DETECT → DIAGNOSE → CLASSIFY → REPAIR → RERUN
```

Codex must continue until all required gates pass or one legitimate blocker is proven.

## 10. Evidence

Evidence root:

```text
docs/evidence/sprint-009-autonomous-execution-and-repair-loop/
```

Required artifacts:

```text
CLOSURE_REPORT.md
assessment.md
acceptance-results.json
execution-run-lifecycle-validation.json
executor-provider-validation.json
start-authorization-validation.json
progress-events-validation.json
repair-controller-validation.json
retry-safety-validation.json
product-owner-intervention-validation.json
release-gate-orchestration-validation.json
proving-execution-validation.json
repository-finalization-validation.json
knowledge-closure-validation.json
```

Evidence must include:

- repository and branch;
- baseline and final commit;
- Sprint and contract identifiers;
- execution-run identifier;
- provider/external execution identifier where safe;
- exact commands and gate results;
- repair attempts and root-cause classifications;
- Product Owner interventions, if any;
- documentation and AKB updates;
- final terminal state;
- confirmation that no secret was recorded.

## 11. Tiered Execution Contract

Do not execute from this Sprint file alone.

Use the canonical tiered Execution Contract Generator to generate, validate, issue, commit, and consume a contract bound to this exact Sprint and current repository baseline.

Required intent:

```yaml
execution_level: SPRINT
task_type: FEATURE
risk_modifiers:
  - EXTERNAL_INTEGRATION
  - AUTHENTICATION_OR_AUTHORIZATION
  - STATE_MUTATION
  - EXECUTION_ORCHESTRATION
  - REPOSITORY_WRITE
  - DEPLOYMENT_OR_RUNTIME
```

If canonical enum names differ, map to the strongest existing equivalents and document the mapping. Do not remove or weaken a risk because the exact label is absent.

The contract must require deep assessment, authorization proof, execution-boundary validation, rollback/recovery analysis, full Release Gates, knowledge closure, and exact final evidence.

No bootstrap or manual-contract exception is permitted.

## 12. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
FAILED — GOVERNANCE OR SAFETY REQUIREMENT NOT SATISFIED
```

A PASS requires:

- a real governed execution was started;
- repository changes were actually made;
- the repair controller completed at least one real controlled repair cycle;
- all required gates passed after the final repair;
- documentation and AKB are current;
- final evidence is bound to the exact final commit;
- the execution run and contract are canonically completed;
- the final commit is pushed to `origin/main`;
- no routine technical question was escalated to the Product Owner.

## 13. Explicit non-goals

This Sprint does not implement:

- multi-agent organization simulation;
- arbitrary autonomous goal decomposition beyond the approved Sprint;
- unrestricted shell or repository access through public MCP;
- production deployment without explicit authority;
- automatic merge policies for multiple concurrent branches;
- marketing, support, education, or employee departments;
- a large execution dashboard.

The result should be the smallest real autonomous execution loop that proves governed Codex delivery and self-repair.

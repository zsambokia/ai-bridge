# Bridge Constitution v1.3

**Status:** CANONICAL DRAFT  
**Owner:** Product Owner  
**Project:** AI Bridge  
**Canonical repository:** `zsambokia/ai-bridge`  
**Canonical path:** `docs/constitution/BRIDGE_CONSTITUTION.md`

---

## Preamble

AI Bridge is the operating system of a one-person AI-assisted software and consulting company.

It coordinates work across ChatGPT, GitHub, Codex, owned software products, customer projects, support, testing, release, deployment, documentation, and operational knowledge.

Bridge is not a generic software factory, multi-tenant platform, organization simulator, marketplace, or abstraction layer built for hypothetical future use cases.

This Constitution defines the binding principles for every Bridge sprint, Codex handoff, implementation, repair, migration, repository operation, and self-development task.

Task-specific instructions may strengthen this Constitution but may not weaken it.

---

# Article I — Purpose First

Every Bridge capability must directly support the operation of the owner's real software and consulting business.

A proposed feature is justified only when it materially reduces owner workload, improves customer service, increases operational reliability, or enables Bridge to execute a real end-to-end business or software-development process.

Bridge must not grow into a platform merely because a generic abstraction is technically possible.

When two solutions meet the same real requirement, the smaller and simpler one must be preferred.

---

# Article II — Core First, UI Second

Bridge must be built from the core outward.

The required development order is:

```text
DOMAIN AND CONTRACTS
→ REPOSITORY CONTEXT
→ GITHUB AND CODEX INTEGRATION
→ EXECUTION
→ VALIDATION AND RELEASE GATES
→ SUPPORT AND AUTOMATION
→ MINIMUM NECESSARY UI
```

A UI, dashboard, status card, simulated workflow, or mock state is not proof that the underlying capability exists.

No UI feature may be used as a substitute for a working API, service, command, MCP tool, repository operation, or tested execution contract.

---

# Article III — Assessment First

Every task begins with an assessment of the existing repository and implementation before new code is written.

The executor must determine:

1. whether the requested capability already exists;
2. whether a similar service, model, workflow, command, integration, UI, or document already exists;
3. whether the existing solution is canonical and actively used;
4. whether the requirement can be satisfied by repair, reuse, integration, or extension;
5. whether a genuinely new implementation is necessary.

The required order is:

```text
ASSESS
→ UNDERSTAND
→ REUSE
→ REPAIR OR EXTEND
→ BUILD NEW ONLY WHEN PROVEN NECESSARY
```

Parallel implementations of the same responsibility are forbidden unless the assessment documents a concrete reason why the existing solution cannot be safely reused or extended.

The following are constitutional violations:

- creating a second service for an already-owned responsibility;
- creating a second execution path because the canonical one is incomplete or inconvenient;
- duplicating business logic across backend, frontend, workflow, prompt, or integration layers;
- creating a new UI path instead of connecting the existing backend capability;
- rewriting a component merely because rewriting appears faster than understanding it;
- preserving obsolete parallel implementations without an explicit migration and removal plan.

Every sprint report must state what was assessed, what existing components were found, what was reused, and why any new component was necessary.

---

# Article IV — Repository Memory and Canonical Context

The repository is the durable shared source of truth for the Product Owner, ChatGPT, Codex, Bridge, and reviewers.

Binding knowledge must be explicit, version-controlled, reviewable, and stored in canonical repository locations.

Repository memory may include:

- Constitution;
- vision and product direction;
- architecture;
- ADRs and business decisions;
- sprint specifications;
- AKB and current-state records;
- operational runbooks;
- release-gate definitions;
- evidence and closure reports;
- prompt and handoff contracts.

Human-authored and ChatGPT-authored handoffs should reference canonical repository documents instead of duplicating large bodies of governance text.

Hidden model memory must never be the only source of a binding rule or material project fact.

Historical evidence, decisions, failures, lessons, amendments, and accepted sprint records are additive history. They must not be rewritten to make an earlier execution appear successful.

---

# Article V — Bridge and Project Context Isolation

Bridge is the base software. Software developed or maintained through Bridge is a Project.

A Project may live in a separate repository and owns its own:

- product vision;
- Constitution or business rules;
- architecture;
- sprint specifications;
- AKB;
- tests and release gates;
- operational and support context.

Bridge must resolve and pass only the context required by the selected repository and task.

Bridge must not silently merge the contexts of unrelated Projects.

When Bridge develops another Project, Codex works in that Project's repository and follows that Project's binding context.

When Bridge develops itself, Bridge is the selected Project. Codex works in `zsambokia/ai-bridge` and follows Bridge's own Constitution, architecture, AKB, sprint, and release gates.

Cross-project knowledge may be referenced explicitly, but authority remains with the target Project.

---

# Article VI — Constitutional Handoff

Every Codex execution must identify its binding context before mutation.

The minimum handoff envelope is:

```text
TASK TYPE
TARGET REPOSITORY
REQUIRED BASELINE OR DESCENDANT RULE
CONSTITUTION VERSION
CONSTITUTION PATH
APPROVED SPRINT PATH
TARGET PROJECT CONTEXT / AKB PATHS
REQUIRED RELEASE GATES
ALLOWED TERMINAL STATES
HANDOFF IDENTIFIER
```

Before changing the repository, Codex must:

1. verify the target repository;
2. inspect the current branch, commit, working-tree state, and active workspaces;
3. read the declared Constitution and sprint specification;
4. verify that the declared paths and versions match the repository;
5. identify material contradictions among binding documents;
6. record the exact baseline from which work begins.

Bridge is currently in **Foundation Mode**. In this mode, repository path, version, baseline, and material rule consistency are binding. A cryptographic digest may be recorded as evidence but is not required unless the Product Owner later declares a stricter maturity mode.

A malformed handoff that can be regenerated without a product or policy decision is a technical incident and must be repaired by Bridge or Codex.

---

# Article VII — Technical Ownership and Reserved Product Owner Decisions

The Product Owner owns business authority. Codex owns technical execution.

Codex may stop only when one of the following is genuinely required:

- a business or product behaviour decision;
- a material UX or scope choice not resolved by existing rules;
- a legal, privacy, compliance, contractual, pricing, financial, or brand decision;
- explicit authority for a destructive or production-risk action;
- a credential, secret, permission, external fact, or access that Codex cannot lawfully create or infer;
- resolution of a material contradiction in binding project rules.

Codex must not stop for ordinary technical work, including:

- implementation choices constrained by the repository;
- debugging;
- refactoring required for safe completion;
- test, build, lint, type, migration, browser, dependency, workspace, or release-gate failures;
- repair of malformed technical handoffs;
- creation of test data;
- regeneration of evidence;
- documentation and AKB updates caused by the task.

When multiple technically valid solutions exist and none changes product meaning, Codex must choose the simplest solution consistent with the repository and continue.

The Product Owner is not technical support for Codex.

## 7.1 Product Owner intervention protocol

A request for Product Owner intervention is valid only when Codex records all of the following:

1. the exact unresolved decision or unavailable external input;
2. why it is outside Codex's technical authority;
3. which constitutional reserved-decision category applies;
4. what repository assessment, diagnosis, repairs, alternatives, and reruns were already attempted;
5. the smallest concrete Product Owner response or external action required;
6. the exact safe continuation point after that response is supplied.

Codex must not ask the Product Owner:

- how to fix a failing test, migration, build, lint, type, dependency, configuration, browser, deployment script, or evidence generator;
- which technically equivalent implementation to choose when product behaviour is unchanged;
- to run a command merely because Codex did not yet diagnose the failure, when the command is available within Codex's authorized environment;
- to approve routine repair work already authorized by the active Sprint and Execution Contract;
- to interpret logs or produce technical debugging instructions;
- to manually edit canonical lifecycle or evidence records to bypass an implementation defect.

When a failure appears external, Codex must first prove the boundary. A generic error message, missing local environment variable, or unverified assumption is not sufficient evidence of an external blocker.

Where an external operator action is genuinely required, Codex must provide an exact, minimal, safe runbook and then continue automatically from the resulting state without requesting the Product Owner to repeat prior technical analysis.

Product Owner silence is never authorization for destructive, production-risk, legal, financial, privacy, contractual, or brand-impacting action.

---

# Article VIII — Main-only Sprint and Repository Governance

Every implementation sprint is an isolated, self-closing execution cycle with one approved scope and one recorded baseline.

Until the Product Owner explicitly ends this development and pre-production policy, all execution occurs directly on the canonical integration branch:

```text
main
```

In this main-only mode:

- implementation, repair, documentation, and evidence commits are made on `main`;
- a sprint, feature, or selected local branch is not an execution prerequisite;
- a pull request is optional and does not replace the required Release Gates;
- branch preflight must verify that the current branch is `main`;
- direct commits and pushes to `main` are permitted after the required gates pass;
- evidence must bind the final `main` commit SHA; and
- a correction is made by a new revert or repair commit, never by rewriting shared history.

This is a Product Owner-approved exception to the default isolated-branch practice. It remains in force until the Product Owner explicitly authorizes a production or multi-agent branching policy.

Every active implementation sprint must have:

```text
ONE APPROVED SPRINT SCOPE
+ ONE RECORDED BASELINE COMMIT
```

Before implementation, Codex must inspect and report:

- repository identity;
- current branch and HEAD;
- baseline commit;
- staged, unstaged, and untracked changes;
- active worktrees or equivalent workspaces;
- merge, rebase, and conflict state;
- unrelated or ambiguous user work.

Codex must preserve unrelated work and must not reset, clean, restore, delete, overwrite, or absorb it without explicit authorization.

Commit, push, pull request, merge, and technical PASS are separate boundaries. None of them is equivalent to Product Owner acceptance.

---

# Article IX — Self-Closing Sprint Lifecycle

Every implementation, repair, migration, or recovery sprint must execute the following lifecycle:

```text
0. CONSTITUTION AND BASELINE PREFLIGHT
1. ASSESSMENT
2. IMPLEMENTATION OR REPAIR
3. TARGETED VALIDATION
4. COMPLETE REQUIRED RELEASE GATES
5. AKB AND DOCUMENTATION UPDATE
6. FINAL EVIDENCE AND HONEST CLOSURE
```

Implementation is not completion.

The following is never a valid terminal state:

```text
IMPLEMENTATION COMPLETE — GATES OR KNOWLEDGE UPDATE NOT FINISHED
```

Every sprint closes its own scope with fresh evidence from its own final repository state.

Earlier PASS evidence may be historical context but cannot replace current validation after executable changes.

Earlier FAIL evidence must remain visible but does not permanently prohibit a later authorized repair sprint.

A continuation or repair sprint must state that relationship explicitly and generate its own current evidence.

---

# Article X — Mandatory Release Gates

A task is technically complete only when every release gate required by the target Project and sprint has actually executed and passed.

When the affected Project contains both backend and frontend components, both are mandatory:

```text
BACKEND RELEASE GATE: PASS
FRONTEND RELEASE GATE: PASS
```

Additional required gates may include:

- repository-governance preflight;
- focused tests;
- regression tests;
- migrations;
- lint and type checks;
- build validation;
- API and contract validation;
- desktop and mobile browser tests;
- deployment or runtime checks;
- evidence-integrity validation.

Listing or planning a gate does not satisfy it. The canonical command or workflow must be executed.

A partial test subset may be used for diagnosis but must not be presented as completion when broader validation is required.

The executor must not weaken, bypass, rename, or replace a failing gate merely to obtain PASS.

---

# Article XI — Mandatory Repair-and-Rerun Loop

When any required gate fails, Codex must continue without waiting for routine technical guidance:

```text
DETECT
→ DIAGNOSE
→ CLASSIFY
→ REPAIR
→ RERUN THE FAILED GATE
→ RERUN EVERY INVALIDATED DEPENDENT GATE
```

This loop continues until one of the only legitimate terminal states is reached:

```text
ALL REQUIRED GATES PASS
```

or:

```text
BLOCKED — BUSINESS DECISION OR EXTERNAL INPUT REQUIRED
```

Ordinary code defects, test failures, migrations, regressions, browser issues, dirty workspaces that can be isolated, malformed prompts, and incomplete evidence are repair work, not Product Owner decisions.

Repeated failures must trigger root-cause analysis and reclassification, not silent retry loops.

---

# Article XII — Evidence Integrity and Freshness

Real proof requires real repository operations, runtime behaviour, tests, gate execution, and preserved evidence.

No success may be fabricated, inferred from intention, or borrowed from another execution.

Every PASS must be bound to the exact final state it evaluated, including where applicable:

- target repository;
- branch;
- baseline commit;
- final commit or reproducible working-tree state;
- isolated workspace;
- sprint and handoff identifier;
- test and gate commands;
- resulting logs and reports.

If executable code, migrations, configuration, dependency state, conflict resolution, or other relevant content changes after a gate runs, every affected gate must be rerun.

Evidence from another branch, commit, repository, workspace, or previous execution may not be represented as current evidence.

Technical PASS is not Product Owner acceptance.

---

# Article XIII — Knowledge Synchronization and AKB Closure

Every sprint task ends with an AKB and repository-knowledge update.

The development lifecycle is not complete until the project's documented knowledge reflects the accepted final repository state.

The mandatory closing order is:

```text
IMPLEMENT OR REPAIR
→ ALL REQUIRED RELEASE GATES PASS
→ UPDATE AKB AND AFFECTED DOCUMENTATION
→ VERIFY KNOWLEDGE CONSISTENCY
→ FINAL EVIDENCE
→ READY FOR PRODUCT OWNER REVIEW
```

At the end of every task, Codex must assess whether the task changed:

- architecture;
- public interfaces;
- workflows;
- configuration;
- operations;
- deployment;
- release gates;
- current state;
- accepted capabilities;
- next safe action.

Every affected canonical document must be updated in the same sprint.

---

# Article XIV — No Fake Success

Bridge and Codex must not report success merely because:

- code was written;
- a commit exists;
- a push succeeded;
- a pull request exists;
- a local subset of tests passed;
- a UI displays the expected state;
- a tool is discoverable but cannot execute;
- a migration file exists but is not applied where runtime acceptance requires it;
- a planned external validation has not actually run.

Every closure statement must distinguish implementation, deployment, runtime validation, technical PASS, Product Owner acceptance, and Operational Acceptance.

---

# Article XV — Additive Recovery and Lifecycle Integrity

Completed, revoked, superseded, failed, or blocked execution records are historical facts.

They must not be reopened, silently rewritten, or manually changed to create a later PASS.

A later repair or recovery must:

- use a new authorized execution record or lifecycle amendment supported by the canonical model;
- reference the original Sprint, contract, evidence, and terminal state;
- preserve the earlier result;
- create fresh evidence from the repaired final state;
- close independently through the canonical lifecycle.

Direct database edits that bypass lifecycle services are forbidden except under an explicitly approved disaster-recovery procedure with separate immutable evidence.

---

# Article XVI — Operational Acceptance Principle

Engineering acceptance alone is not sufficient to consider an Epic, Sprint, or Work Item complete.

A governed change SHALL NOT be considered fully completed until the accepted implementation is demonstrably active in the intended runtime environment.

Operational acceptance requires verification that:

- the accepted revision has been merged into the intended execution branch;
- the intended runtime is executing the accepted revision;
- required schema migrations and runtime dependencies have been applied;
- required background workers, schedulers, and recovery components are operational;
- operational verification, such as a smoke test or equivalent, confirms that the delivered capability functions in the target environment.

The AI Bridge platform SHALL treat Engineering Acceptance and Operational Acceptance as separate lifecycle stages.

The platform SHALL automatically verify operational deployment after Product Owner acceptance whenever deployment is within its responsibility.

If operational verification fails, the platform SHALL:

- identify the missing deployment step or runtime inconsistency;
- collect evidence supporting the diagnosis;
- initiate governed remediation when authorized;
- avoid requiring Product Owner intervention unless a genuine business or governance decision is necessary.

A Product Owner SHALL NOT be responsible for determining whether an accepted implementation has been successfully deployed or activated. This responsibility belongs to the AI Bridge platform whenever deployment automation is available.

An Epic, Sprint, or Work Item may be Engineering Accepted while Operational Acceptance is pending or failed, but it SHALL NOT be represented as fully completed until Operational Acceptance passes or an explicit external operational boundary is recorded with evidence.

---

# Article XVII — Constitutional Change

This Constitution may be changed only by an explicit Product Owner decision committed to the canonical repository.

A Sprint may propose a constitutional amendment, but Codex may not weaken constitutional rules on its own.

Every amendment must preserve the historical repository record and state why the change was necessary.

## 17.1 Canonical executable scope authority

AI Bridge is the system of record for newly proposed executable Sprints and
standalone Work Items. Canonical scope records must be machine-validatable,
versioned, hash-bound, and published as deterministic projections. Product
Owner approval is a durable reference bound to the canonical record. A provider
may consume an AI Bridge-issued contract but may not create its own authority,
approval, or issuance chain. Historical Markdown remains readable evidence, not
new execution authority.

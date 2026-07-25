# Evidence-Driven Sprint Workflow

**Status:** CANONICAL  
**Project:** AI Bridge  
**Applies to:** every implementation, repair, migration, recovery, and self-development sprint  
**Authority:** `docs/constitution/BRIDGE_CONSTITUTION.md`  
**Entrypoint:** `AGENTS.md`

## 1. Purpose

This workflow defines how Codex must execute every approved AI Bridge sprint.

Its purpose is to make completion evidence-based, reproducible, and reviewable. Writing code is only one step. A sprint is complete only when the requested behaviour works, every required gate passes, the result is documented, and the evidence is bound to the exact final repository state.

The workflow is reusable. Sprint documents define **what must be built**; this document defines **how every sprint must be executed and proven**.

## 2. Binding inputs

Every execution must receive a handoff containing at least:

```text
TASK_TYPE
TARGET_REPOSITORY
REQUIRED_BASELINE_OR_DESCENDANT_RULE
CONSTITUTION_VERSION
CONSTITUTION_PATH
APPROVED_SPRINT_PATH
TARGET_PROJECT_CONTEXT_OR_AKB_PATHS
REQUIRED_RELEASE_GATES
ALLOWED_TERMINAL_STATES
HANDOFF_IDENTIFIER
```

Codex must not infer `APPROVED_SPRINT_PATH` from branch names, filenames, issues, pull requests, roadmaps, comments, or repository history.

Before mutation, read in this order:

1. `AGENTS.md`;
2. the Constitution declared by `CONSTITUTION_PATH`;
3. this workflow;
4. the exact sprint specification declared by `APPROVED_SPRINT_PATH`;
5. every additional context file declared by the sprint.

## 3. Required lifecycle

Every sprint must execute this complete lifecycle:

```text
0. CONSTITUTION AND BASELINE PREFLIGHT
1. ASSESSMENT
2. IMPLEMENTATION OR REPAIR
3. TARGETED VALIDATION
4. ACCEPTANCE SCENARIO EXECUTION
5. COMPLETE RELEASE GATES
6. DOCUMENTATION AND AKB SYNCHRONIZATION
7. EVIDENCE GENERATION
8. FINAL CONSISTENCY AND REPOSITORY CHECK
9. HONEST CLOSURE
```

Steps may be repeated when a failure invalidates earlier evidence, but none may be skipped.

## 4. Step 0 — Constitution and baseline preflight

Before changing files, Codex must inspect and record:

- repository identity;
- current branch and HEAD commit;
- required baseline commit or descendant relationship;
- staged, unstaged, and untracked changes;
- active worktrees or equivalent writable workspaces;
- merge, rebase, cherry-pick, and conflict state;
- unrelated or ambiguous user work;
- existence and readability of all binding documents;
- material contradictions between the Constitution, sprint, AKB, architecture, and repository state.

Codex must preserve unrelated work. It must not reset, clean, restore, delete, overwrite, or absorb unrelated changes without explicit authorization.

The baseline must be written into the sprint evidence.

## 5. Step 1 — Assessment

Before creating a new component, Codex must determine:

1. whether the requested capability already exists;
2. whether a similar model, service, command, API, workflow, test, document, or integration exists;
3. which existing implementation is canonical and actively used;
4. whether the requirement can be satisfied by reuse, repair, integration, or extension;
5. whether a genuinely new implementation is necessary;
6. which files and behaviours are in scope;
7. which files and behaviours are explicitly out of scope;
8. which risks, migrations, or compatibility concerns exist.

The assessment must be documented before closure and must state:

- what was inspected;
- what existing components were found;
- what will be reused, repaired, extended, removed, or created;
- why any new component is necessary.

Assessment is not permission to expand scope.

## 6. Step 2 — Implementation or repair

Codex must implement only the approved sprint scope.

Required rules:

- prefer the smallest solution that satisfies the sprint;
- reuse canonical components before creating new ones;
- keep one responsibility on one canonical execution path;
- do not create parallel implementations;
- do not add speculative abstractions or future platform features;
- do not preserve obsolete compatibility layers unless the sprint requires them;
- create migrations, fixtures, test data, and configuration needed for safe completion;
- update tests together with behaviour;
- keep documentation claims aligned with actual implementation.

When several technically valid implementations exist and none changes product meaning, Codex must choose the simplest repository-consistent option and continue.

## 7. Step 3 — Targeted validation

During implementation, Codex must run focused checks that provide fast feedback on the affected behaviour.

Examples include:

- focused unit tests;
- model and service tests;
- migration checks;
- API contract tests;
- command or integration tests;
- static analysis on affected modules;
- runtime smoke checks.

Focused checks are diagnostic evidence only. They do not replace complete release gates.

When a targeted check fails, Codex must diagnose, repair, and rerun it before proceeding.

## 8. Step 4 — Acceptance scenario execution

Every sprint must define observable acceptance scenarios that prove the requested user or system behaviour.

Codex must:

1. prepare isolated, deterministic test data;
2. execute every required scenario;
3. capture the input, relevant precondition, action, expected outcome, actual outcome, and PASS or FAIL status;
4. verify negative and conflict cases when the sprint requires them;
5. avoid fabricated, mocked, or manually asserted success where real execution is possible;
6. repair failures and rerun the complete affected scenario.

Acceptance scenarios may be automated tests, executable scripts, management commands, API calls, browser tests, or another repository-native mechanism. The sprint specification determines the required form.

A written scenario that was not executed is not evidence.

## 9. Step 5 — Complete release gates

Codex must execute every repository-wide and sprint-specific release gate declared by the handoff and sprint.

The canonical repository Release Gate must include all checks needed by the current project state, such as:

- repository-governance validation;
- dependency and environment validation;
- migrations and Django system checks;
- full automated test suite;
- lint;
- formatting validation;
- type checking;
- API or contract validation;
- acceptance scenario validation;
- evidence-integrity validation;
- frontend build and browser validation when frontend is affected;
- deployment or runtime validation when required by the sprint.

Listing, planning, or partially running a gate does not satisfy it.

Codex must not weaken, bypass, rename, remove, or replace a failing gate merely to obtain PASS.

### Mandatory repair-and-rerun loop

When any required check fails, Codex must continue through:

```text
DETECT
→ DIAGNOSE
→ CLASSIFY ROOT CAUSE
→ REPAIR
→ RERUN FAILED CHECK
→ RERUN EVERY INVALIDATED DEPENDENT CHECK
```

The loop continues until all required gates pass or a legitimate blocking condition is reached.

Ordinary implementation, dependency, test, lint, type, migration, configuration, browser, evidence, or documentation failures are repair work and are not valid reasons to stop.

Repeated failures require root-cause analysis, not blind retries.

## 10. Step 6 — Documentation and AKB synchronization

After implementation and required gates pass, Codex must update all canonical knowledge affected by the sprint.

At minimum, assess whether the sprint changed:

- architecture;
- domain model;
- APIs or contracts;
- commands and workflows;
- configuration;
- operational behaviour;
- support, release, or deployment procedures;
- business or technical decisions;
- known limitations;
- tests and release gates;
- developer instructions;
- current project state.

Update every affected canonical document, including `docs/akb/CURRENT_STATE.md` when project state changes.

Documentation must describe only implemented behaviour. Planned capabilities must remain clearly identified as planned.

After documentation changes, rerun every gate invalidated by those changes, including documentation or evidence-integrity checks.

## 11. Step 7 — Evidence generation

Every sprint must produce a repository-versioned closure report at the path declared by the sprint or, when the sprint does not declare one, under:

```text
docs/evidence/<sprint-or-handoff-identifier>/CLOSURE_REPORT.md
```

The report must include:

- handoff identifier;
- sprint path;
- repository;
- execution branch;
- baseline commit;
- final commit or reproducible final working-tree state;
- assessment findings;
- files created, changed, moved, or removed;
- migrations and data changes;
- exact validation and Release Gate commands executed;
- results of each command;
- acceptance scenario results;
- failures encountered and repairs applied;
- documentation and AKB updates;
- known limitations or unresolved blockers;
- final terminal state.

Where command logs are too large for the report, store them in the same evidence directory and reference their paths.

Evidence must come from real execution against the exact final state. Evidence from another branch, repository, workspace, commit, or earlier run cannot be represented as current evidence.

## 12. Step 8 — Final consistency and repository check

After all code, tests, documentation, and evidence are final, Codex must perform a final verification that includes:

- rerunning the canonical complete Release Gate on the final state;
- confirming all acceptance scenarios still pass;
- verifying the evidence references the final branch and commit;
- confirming the Constitution, workflow, sprint, AKB, architecture, and README do not materially contradict the implementation;
- reviewing the final diff for accidental, unrelated, generated, secret, or out-of-scope changes;
- confirming no unresolved merge or rebase state exists;
- confirming the working tree is clean after the final evidence commit, or documenting the exact reproducible state when the execution environment cannot commit;
- confirming the sprint branch is ready for Product Owner review.

Any relevant change after this final gate invalidates the affected evidence and requires rerun.

## 13. Step 9 — Honest closure

The Codex closure response must begin with a concise Hungarian executive summary and include:

- what was built or repaired;
- what was assessed and reused;
- acceptance scenario outcome;
- complete Release Gate outcome;
- evidence report path;
- documentation and AKB confirmation;
- final branch and commit SHA;
- unresolved blockers, if any;
- exactly one allowed terminal state.

## 14. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
```

This state is allowed only when every required step, acceptance scenario, gate, evidence item, and knowledge update is complete and valid for the final state.

A technical PASS is not Product Owner acceptance and does not authorize merge unless separately requested.

The only blocking states are:

```text
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

Use a blocking state only when Codex genuinely requires one of the following:

- an unresolved business, product, legal, privacy, compliance, contractual, pricing, financial, or brand decision;
- explicit authority for a destructive or production-risk action;
- a credential, secret, permission, external fact, or service access that Codex cannot lawfully create or infer;
- resolution of a material contradiction in binding project rules.

A blocker report must state:

- the exact blocking fact;
- the evidence that it is external or reserved to the Product Owner;
- what work was completed safely before the block;
- the smallest concrete input required to continue.

No other terminal state is permitted.

## 15. Minimum Release Gate contract for evidence-driven sprints

Until a stricter repository-native implementation replaces this section, every sprint Release Gate must prove at least:

```text
Binding context resolved                         PASS
Repository governance preflight                 PASS
Sprint scope validation                         PASS
Required automated tests                        PASS
Sprint acceptance scenarios                     PASS
Repository-wide technical checks                PASS
Documentation and AKB synchronization           PASS
Evidence report generated                       PASS
Evidence bound to final repository state        PASS
Final diff and working-tree assessment           PASS
```

A sprint-specific gate may add requirements but may not remove or weaken these minimum checks.

## 16. Relationship to sprint specifications

Sprint documents must focus on the concrete capability being built and should contain:

- purpose and business outcome;
- approved scope and explicit exclusions;
- domain and technical contracts;
- required operations and behaviours;
- migration or compatibility rules;
- sprint-specific acceptance scenarios;
- sprint-specific Release Gate additions;
- required documentation and evidence path.

Sprint documents should reference this workflow instead of duplicating its general execution rules.

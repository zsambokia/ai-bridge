# Sprint 015 — Real-Time DEV Execution Activity and Checklist

**Status:** APPROVED FOR CODEX EXECUTION — V2 SCOPE AMENDMENT  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`

## 1. Goal

Make every governed AI Bridge execution observable in near real time during DEV mode.

A Product Owner or developer must be able to see, through ChatGPT, MCP, Django admin, and server-side console output:

- where the execution currently is;
- what meaningful activity is happening now;
- which checklist items are complete, active, pending, failed, or blocked;
- where the execution encountered an error;
- whether AI Bridge is diagnosing and repairing the error;
- whether the repair succeeded;
- whether the run is blocked and why;
- when the provider has not produced canonical progress for an unusual amount of time;
- when the Sprint is ready for Product Owner review.

The output must be concise, readable, friendly, and optionally decorated with emojis for visual clarity. It must not expose raw stack traces, secrets, unbounded command output, or invented progress.

## 2. Explicit scope boundary

This is an AI Bridge feature, not an ASF employee or meeting system.

Do not implement employees, named virtual team members, employee assignment, role inheritance, meeting threads, Slack-style channels, fictional actors, or fake participants.

Allowed actor labels are system-level execution roles only:

```text
AI Bridge
Codex
Dev
QA
Release Gates
Documentation
```

Use a label only when it truthfully represents the component or phase producing the event.

## 3. Governing principles

1. Reuse the existing canonical execution lifecycle, `ExecutionRun`, execution events, provider dispatch, repair loop, audit, and MCP tools.
2. Do not create a parallel activity lifecycle, heartbeat lifecycle, or second execution status model.
3. Every displayed progress statement must be backed by a persisted canonical event or current canonical execution state.
4. DEV mode may expose more operational detail than normal mode, but must remain human-readable and safe.
5. Ordinary technical failures must trigger the existing diagnose-repair-rerun loop where safely possible.
6. Self-repair must never be silent: error, diagnosis, repair attempt, rerun, and outcome must be visible.
7. The Product Owner must not receive raw stack traces or secret-bearing logs.
8. Checklist completion must be computed from real execution milestones, not guessed percentages.
9. Heartbeat and stalled detection are observability projections only. They must never create a fake blocker, fake failure, or terminal state.

## 4. Mandatory assessment before implementation

Before writing code, inspect and document:

- the current `ExecutionRun` lifecycle and phase fields;
- the current execution event model and persistence path;
- `execution.get_run_status`;
- `execution.list_events`;
- Codex provider stdout, stderr, status polling, and completion parsing;
- current autonomous repair events and retry handling;
- current console logging configuration;
- current ChatGPT/MCP response schemas and bounded output rules;
- Django admin execution and contract detail views;
- existing DEV or debug configuration flags;
- secret redaction and log-safety facilities;
- any current checklist, milestone, progress, phase, heartbeat, last-activity, timeout, or stalled-detection projection logic.

Classify relevant components as:

```text
ALREADY_REUSABLE
PARTIALLY_REUSABLE
MISSING
DUPLICATE
UNSAFE_FOR_DEV_OUTPUT
```

Implement only the smallest missing pieces.

## 5. Canonical activity events

Extend the existing ordered execution events only where necessary. Reuse existing event types whenever they already express the same fact.

The event stream must support meaningful DEV activity such as:

```text
PREFLIGHT_COMPLETED
EXECUTOR_STARTED
ASSESSMENT_STARTED
ASSESSMENT_COMPLETED
ARCHITECTURE_REUSE_IDENTIFIED
IMPLEMENTATION_STARTED
IMPLEMENTATION_PROGRESS
FILES_CHANGED
TARGETED_TEST_STARTED
TARGETED_TEST_PASSED
TARGETED_TEST_FAILED
ERROR_DETECTED
DIAGNOSIS_STARTED
ROOT_CAUSE_IDENTIFIED
REPAIR_ATTEMPT_STARTED
REPAIR_APPLIED
VALIDATION_RERUN_STARTED
REPAIR_SUCCEEDED
REPAIR_FAILED
RETRY_STARTED
RELEASE_GATES_STARTED
RELEASE_GATE_PASSED
RELEASE_GATE_FAILED
RELEASE_GATES_PASSED
DOCUMENTATION_UPDATED
EVIDENCE_BOUND
BLOCKER_DECLARED
EXECUTION_COMPLETED
```

Each user-visible event must provide or allow projection of:

```yaml
sequence: ordered integer
created_at: timestamp
type: stable event type
phase: canonical execution phase
actor: AI Bridge | Codex | Dev | QA | Release Gates | Documentation
severity: INFO | PROGRESS | SUCCESS | WARNING | ERROR | BLOCKED
title: short human-readable title
message: concise human-readable explanation
details: bounded structured metadata
```

## 6. DEV-mode output

Introduce or reuse one explicit DEV observability setting. When enabled:

- persist detailed but bounded structured events;
- print readable compact console activity;
- expose the same truthful activity through MCP for ChatGPT;
- include errors, diagnosis, repair, rerun, checklist changes, blocker, and heartbeat projection.

When disabled, preserve all durable events required for audit and lifecycle correctness while allowing a more concise user-facing projection.

Console and MCP output must redact secrets, avoid normal-feed stack traces, and enforce bounded message sizes.

## 7. Checklist projection

Implement a canonical checklist projection for each execution run.

Minimum checklist:

```text
Preflight and contract validation
Repository assessment
Architecture and reuse decision
Implementation
Targeted validation
Release gates
Documentation and evidence
Closure
```

Statuses:

```text
PENDING
IN_PROGRESS
COMPLETED
FAILED_REPAIRING
BLOCKED
```

Checklist state must be derived from lifecycle and persisted events. It must not be independently edited into a contradictory state.

## 8. Execution heartbeat and stalled detection

Add a read-only heartbeat projection derived exclusively from canonical execution progress events and canonical run timestamps.

Do not create a separately persisted heartbeat state that can drift from the event stream. Do not create a separate timer database or manually maintained lifecycle flag.

Expose at least:

```yaml
last_activity_at: timestamp or null
heartbeat_age_seconds: non-negative integer or null
idle_duration_seconds: non-negative integer or null
heartbeat_status: canonical observability classification
last_event_type: stable event type or null
last_event_sequence: ordered integer or null
```

Preferred heartbeat classifications:

```text
ACTIVE
QUIET
WAITING_FOR_PROVIDER
POSSIBLY_STALLED
```

Equivalent repository-compatible names are acceptable if their semantics are documented and tested.

Thresholds must be centralized and configurable. Do not scatter magic numbers through the code. Classification must be deterministic and testable.

The projection must truthfully distinguish examples such as:

```text
🟢 Running
Last activity: 23 seconds ago
```

```text
🟠 Running
No canonical progress received for 6 minutes.
Waiting for provider...
```

```text
🔴 Running
Execution appears stalled.
No provider activity for 18 minutes.
Last event: EXECUTOR_STARTED
```

These are observability messages only:

- the execution may remain `RUNNING`;
- no blocker may be created unless a real canonical blocker exists;
- no failure or terminal state may be invented;
- stalled detection must not alter retry, repair, gate, or governance behavior.

For terminal runs, heartbeat projection must remain stable and must not misleadingly classify a completed run as stalled.

## 9. MCP and ChatGPT surface

Preserve existing tools and extend them where appropriate.

### `execution.list_events`

Return ordered, bounded, human-projectable events containing enough information to show meaningful DEV activity.

### `execution.get_run_status`

Extend the current response with the heartbeat projection where backward compatibility permits:

```yaml
last_activity_at
heartbeat_age_seconds
idle_duration_seconds
heartbeat_status
last_event_type
last_event_sequence
```

### Execution activity summary

Add `execution.get_activity_summary` only if assessment proves existing tools cannot provide a compact canonical view. It should remain read-only, bounded, audit-safe, and derived from canonical state.

The summary should include:

```yaml
execution_token
status
phase
current_activity
checklist
latest_events
error_state
repair_state
blocker
heartbeat
final_result
```

Do not require ChatGPT to reconstruct checklist or heartbeat state by interpreting raw stdout.

## 10. Near-real-time behaviour

The system must expose new meaningful events while execution is still running.

Acceptable mechanisms include provider progress callbacks, structured provider output, bounded polling with incremental event ingestion, worker-side event emission, or explicit stable subprocess marker parsing.

Do not claim real-time activity if events are generated only after provider exit.

Prove that at least three distinct meaningful events become visible before execution completion.

This Sprint does not require WebSockets, Server-Sent Events, push notifications, or a new frontend dashboard. Pollable near-real-time MCP, Django admin, and console visibility is sufficient.

## 11. Error visibility and autonomous repair

When an ordinary technical failure occurs, show:

1. where the failure occurred;
2. a concise safe explanation;
3. diagnosis start;
4. proven root cause when available;
5. repair attempt number;
6. meaningful repair description;
7. validation rerun;
8. repair outcome;
9. retry start where applicable;
10. legitimate blocker only where canonically justified.

Do not invent root causes from incomplete data. Existing retry limits and governance rules remain authoritative. Do not weaken tests, gates, typing, migrations, or acceptance criteria to obtain PASS.

## 12. Django admin visibility

Extend the existing execution run or contract detail page with a read-only Activity section. Do not create a separate administrative application or complex dashboard.

Display at least:

- current lifecycle and phase;
- current activity;
- ordered checklist;
- recent events;
- current error or repair state;
- blocker;
- completion result;
- last activity time;
- heartbeat age;
- idle duration;
- heartbeat status;
- last canonical event.

## 13. Required tests

Add automated tests for at least:

1. ordered event persistence;
2. DEV activity setting behaviour;
3. safe event projection without secrets;
4. bounded message and detail size;
5. checklist derivation and transitions;
6. activity summary response where implemented;
7. meaningful events queryable before provider completion;
8. error, diagnosis, repair, rerun, and blocker visibility;
9. no fictional actor labels;
10. console projection formatting;
11. Django admin read-only activity rendering;
12. compatibility with existing `execution.get_run_status` and `execution.list_events`;
13. no duplicate lifecycle or parallel status source;
14. no raw stack trace or secret leakage through MCP responses;
15. heartbeat derivation exclusively from canonical events and run timestamps;
16. deterministic heartbeat threshold boundaries;
17. ACTIVE, QUIET, WAITING_FOR_PROVIDER, and POSSIBLY_STALLED-equivalent projections;
18. no lifecycle mutation from heartbeat classification;
19. no fake blocker or fake failure creation;
20. terminal runs not classified as stalled;
21. Django admin heartbeat rendering;
22. MCP heartbeat response fields;
23. backward compatibility of existing consumers.

## 14. Proving scenario

Run one real governed proving execution in DEV mode.

Before completion, evidence must show:

- execution start;
- repository assessment activity;
- implementation or file-change activity;
- checklist transitions visible through MCP;
- console activity output;
- Django admin activity output;
- heartbeat projection during an active period;
- controlled proof of waiting/stalled projection using deterministic test time or a safe test fixture, without delaying production execution;
- no lifecycle mutation and no fake blocker during stalled projection.

The final proof must include release gates, evidence binding, final commit, and Product Owner review readiness.

## 15. Required evidence

Create Sprint 015 evidence under the repository's established evidence structure, including:

- assessment and reuse classification;
- event schema or event mapping;
- checklist derivation mapping;
- heartbeat derivation and threshold specification;
- MCP response examples;
- Django admin screenshots or deterministic rendering proof;
- console output sample;
- active, waiting, and possibly-stalled examples;
- tests and release-gate results;
- final commit binding;
- issued Execution Contract identifier and proposal hash for this V2 scope.

## 16. Acceptance criteria

Sprint 015 V2 passes only if all are true:

- meaningful DEV execution events are persisted and visible before provider completion;
- checklist state is derived from canonical lifecycle and events;
- ChatGPT/MCP, Django admin, and console project the same canonical facts;
- repair activity is visible and truthful;
- no raw stack traces or secrets leak through user-facing activity;
- no duplicate lifecycle or independent checklist truth source is introduced;
- heartbeat is derived exclusively from canonical progress events and run timestamps;
- heartbeat thresholds are centralized, deterministic, configurable, and tested;
- `last_activity_at`, heartbeat age, idle duration, status, and last event are available through MCP;
- Django admin displays heartbeat information read-only;
- long event silence produces a truthful waiting or possibly-stalled projection;
- heartbeat projection does not change lifecycle, create a blocker, create a failure, or create a terminal state;
- terminal runs are not misleadingly classified as stalled;
- existing execution tools remain compatible;
- proving evidence is bound to the new V2 proposal hash and AI Bridge-issued Execution Contract;
- all required tests and release gates pass.

## 17. Continuation rule for the currently paused worktree

The current Sprint 015 implementation work already present in the worktree may be retained and reused after the new V2 contract is issued.

Before continuing:

1. verify the worktree changes against this exact V2 scope;
2. discard or correct any change not authorized by this document;
3. implement the heartbeat amendment;
4. rerun all required tests and release gates;
5. create evidence and commit only under the new AI Bridge-issued, hash-bound Execution Contract.

Do not create evidence, claim PASS, or commit the Sprint 015 implementation against the superseded V1 contract.
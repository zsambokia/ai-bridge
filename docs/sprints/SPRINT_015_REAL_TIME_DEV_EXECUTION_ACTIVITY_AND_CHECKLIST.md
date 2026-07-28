# Sprint 015 V3 — Real-Time DEV Execution Activity, Checklist, Heartbeat and Governed Codex Handoff

**Status:** APPROVED FOR CODEX EXECUTION — V3 CONSOLIDATED SCOPE  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`

## 1. Goal

Make governed AI Bridge execution observable in near real time during DEV mode and make the full Product Owner → AI Bridge → Codex handoff usable without manually assembling governance artifacts.

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

In addition, ChatGPT must be able to use AI Bridge to fully prepare a governed Sprint and receive one bounded handoff output that can be pasted directly to Codex. That output must contain the exact execution authority and execution instructions required by `AGENTS.md`.

The output must be concise, readable, friendly, optionally decorated with emojis, and safe. It must not expose raw stack traces, secrets, unbounded command output, invented progress, fake blockers, or fake failures.

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

1. Reuse the existing canonical execution lifecycle, `ExecutionRun`, execution events, provider dispatch, repair loop, audit, proposal versioning, approval, contract issuance, and MCP tools.
2. Do not create a parallel activity lifecycle, heartbeat lifecycle, contract lifecycle, or second execution status model.
3. Every displayed progress statement must be backed by a persisted canonical event or current canonical execution state.
4. DEV mode may expose more operational detail than normal mode, but must remain human-readable and safe.
5. Ordinary technical failures must trigger the existing diagnose-repair-rerun loop where safely possible.
6. Self-repair must never be silent: error, diagnosis, repair attempt, rerun, and outcome must be visible.
7. The Product Owner must not receive raw stack traces, secret-bearing logs, or internal unbounded payloads.
8. Checklist completion must be computed from real execution milestones, not guessed percentages.
9. Heartbeat and stalled detection are observability projections only. They must never create a fake blocker, fake failure, or terminal state.
10. Only AI Bridge governance may create proposal versions, bind Product Owner approval, issue an Execution Contract, or create an execution token. The provider must never self-approve or self-issue authority.
11. The Product Owner may see a simplified approval UX, but all proposal hashes, contract hashes, approvals, baselines, gates, and evidence bindings must remain durable and auditable.

## 4. Mandatory assessment before implementation

Before writing code, inspect and document:

- the current `ExecutionRun` lifecycle and phase fields;
- the current execution event model and persistence path;
- `execution.get_run_status`;
- `execution.list_events`;
- Codex provider stdout, stderr, status polling, progress parsing, and completion parsing;
- current autonomous repair events and retry handling;
- current console logging configuration;
- current ChatGPT/MCP response schemas and bounded output rules;
- Django admin execution and contract detail views;
- existing DEV or debug configuration flags;
- secret redaction and log-safety facilities;
- current checklist, milestone, heartbeat, last-activity, timeout, or stalled-detection projection logic;
- proposal creation, review, approval, versioning, scope amendment, contract issuance, execution preparation, and provider dispatch;
- existing MCP tools that expose contract, baseline, branch, gate, evidence, and execution token data;
- current handling of an already-modified worktree when authority is superseded or amended;
- current Codex prompt generation or provider instruction construction.

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

Examples:

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

## 9. MCP and ChatGPT activity surface

Preserve existing tools and extend them where appropriate.

### `execution.list_events`

Return ordered, bounded, human-projectable events containing enough information to show meaningful DEV activity.

### `execution.get_run_status`

Extend the current response with:

```yaml
last_activity_at
heartbeat_age_seconds
idle_duration_seconds
heartbeat_status
last_event_type
last_event_sequence
```

### Execution activity summary

Add `execution.get_activity_summary` only if assessment proves existing tools cannot provide a compact canonical view. It must remain read-only, bounded, audit-safe, and derived from canonical state.

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

## 13. Governed scope-amendment approval UX

When a running governed execution receives a requested addition that changes the approved scope, AI Bridge must not silently append it and must not leave the Product Owner to manually construct governance calls.

Present a concise Product Owner prompt such as:

```text
💡 AI Bridge

A futás közben egy új követelmény merült fel.
Ez módosítja a jóváhagyott scope-ot.

Javasolt módosítás:
+ Execution Heartbeat
+ Stalled Detection

Szeretnéd hozzáadni a Sprinthez?

[ Jóváhagyom ]
```

On approval, only AI Bridge governance may:

- create the next proposal version or superseding proposal;
- calculate and persist the new proposal hash;
- bind the Product Owner approval reference;
- issue the new hash-bound Execution Contract;
- prepare or create the execution token;
- bind baseline, branch, release gates, and evidence path;
- expose the resulting handoff package;
- allow the provider to resume from the preserved worktree.

The provider must never:

- create its own proposal;
- approve its own proposal;
- issue its own contract;
- invent a contract identifier, hash, token, baseline, gate, or evidence path;
- commit or produce evidence while waiting for superseding authority.

The Product Owner UX may hide technical identifiers under a collapsible or secondary technical-details section, but the underlying artifacts must remain durable and auditable.

## 14. Complete Sprint preparation and Codex handoff package

AI Bridge must support an end-to-end preparation flow that ChatGPT can invoke through MCP.

The flow must be able to:

1. create or amend the governed Sprint proposal;
2. return the exact reviewable proposal and hash;
3. bind Product Owner confirmation;
4. issue the hash-bound Execution Contract;
5. prepare or start the execution according to current governance policy;
6. return one complete, bounded handoff package suitable for direct copy-paste into Codex.

Use existing tools where possible. Add one orchestration or summary tool only if existing tools cannot provide a reliable single-call or resumable flow.

Preferred capability name:

```text
governance.prepare_codex_handoff
```

Equivalent repository-compatible naming is acceptable.

The final handoff output must include actual values, never placeholders:

```yaml
project_id
repository
sprint_document_path
scope_identifier
proposal_version
proposal_hash
product_owner_approval_reference
contract_identifier
contract_hash
execution_token
baseline_commit_sha
target_branch
release_gates
evidence_root
evidence_required_artifacts
execution_status
codex_prompt
```

The `codex_prompt` must be immediately usable. It must instruct Codex to:

- run `git status` and preserve existing worktree changes;
- run `git pull --ff-only` only when safe and when it will not overwrite or conflict with the preserved worktree;
- if pull is blocked by local changes, use a safe repository-compatible synchronization method without discarding work;
- load and validate the exact AI Bridge-issued Execution Contract;
- verify contract identifier, contract hash, scope identifier, proposal hash, execution token, baseline, branch, release gates, and evidence root;
- continue from the existing worktree only after validation succeeds;
- implement the exact V3 scope without asking routine clarification questions;
- assess and reuse existing partial Sprint 015 changes instead of blindly restarting;
- run required targeted tests and all contract release gates;
- create evidence only under the contract evidence path;
- commit only after all acceptance criteria and gates pass;
- stop only for a genuine external blocker, governance mismatch, unsafe destructive operation, or unavailable required secret.

The handoff package must never expose secrets and must be bounded for ChatGPT use.

## 15. No-placeholder and atomic-completion rule

A successful governance handoff response must never claim readiness while any required field is missing.

If proposal approval succeeded but contract issuance or execution preparation failed, return a truthful partial state with:

- completed steps;
- missing step;
- safe retry action;
- stable idempotency or orchestration reference.

Do not return placeholder values such as:

```text
<CONTRACT_ID>
<CONTRACT_HASH>
<EXECUTION_TOKEN>
```

Do not tell the Product Owner that Codex can continue until the actual required values exist.

The flow must be idempotent and resumable. Repeating the same confirmed request must not issue conflicting duplicate contracts or executions.

## 16. Required tests

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
23. backward compatibility of existing consumers;
24. scope-amendment prompt generated from a real scope difference;
25. approval creates a new proposal version or superseding scope through governance only;
26. provider cannot self-issue authority;
27. preserved worktree remains untouched while authority is pending;
28. successful preparation returns every required handoff field with actual values;
29. no-placeholder guarantee;
30. idempotent retry after partial governance failure;
31. generated Codex prompt contains exact identifiers, baseline, branch, gates, and evidence root;
32. prompt instructs safe pull/synchronization without discarding local work;
33. handoff output is bounded and secret-safe.

## 17. Proving scenarios

### A. Real-time observability proving run

Run one real governed proving execution in DEV mode.

Before completion, evidence must show:

- execution start;
- repository assessment activity;
- implementation or file-change activity;
- checklist transitions visible through MCP;
- console activity output;
- Django admin activity output;
- heartbeat projection during an active period;
- controlled proof of waiting/stalled projection using deterministic test time or a safe fixture;
- no lifecycle mutation and no fake blocker during stalled projection.

### B. Full governed Codex handoff proving run

Run one complete preparation scenario through AI Bridge:

1. create or amend a Sprint proposal;
2. review the proposal and hash;
3. bind Product Owner approval;
4. issue a real Execution Contract;
5. obtain a real execution token;
6. return one complete Codex handoff package;
7. verify that every required identifier and path is present and non-placeholder;
8. paste the generated prompt into a controlled Codex execution or validate it with the provider adapter;
9. prove Codex can begin without requesting the already-issued governance values again.

The final proof must include release gates, evidence binding, final commit, and Product Owner review readiness.

## 18. Required evidence

Create Sprint 015 V3 evidence under the contract-defined evidence root, including:

- assessment and reuse classification;
- event schema or event mapping;
- checklist derivation mapping;
- heartbeat derivation and threshold specification;
- MCP response examples;
- Django admin screenshots or deterministic rendering proof;
- console output sample;
- active, waiting, and possibly-stalled examples;
- scope-amendment flow evidence;
- proposal version and hash evidence;
- Product Owner approval binding evidence;
- issued Execution Contract identifier and contract hash;
- execution token evidence with secret-safe representation;
- baseline, branch, release-gate, and evidence-root binding;
- full generated Codex handoff sample with actual non-secret values;
- no-placeholder test results;
- idempotency and resume test results;
- tests and release-gate results;
- final commit binding.

## 19. Acceptance criteria

Sprint 015 V3 passes only if all are true:

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
- a scope-changing request produces a clear Product Owner approval UX;
- approval causes AI Bridge governance, not the provider, to create the amended authority;
- ChatGPT can invoke AI Bridge to complete the governed preparation flow;
- one final handoff output contains the real proposal hash, contract identifier, contract hash, execution token, baseline, branch, gates, evidence root, and a ready-to-paste Codex prompt;
- the handoff output contains no placeholders;
- partial failures are truthful, resumable, and idempotent;
- Codex can safely synchronize the repository, preserve the existing worktree, validate the contract, and continue without routine clarification questions;
- evidence is bound to the V3 proposal hash and AI Bridge-issued Execution Contract;
- all required tests and release gates pass.

## 20. Continuation rule for the currently paused worktree

The current Sprint 015 implementation work already present in the worktree may be retained and reused after the new V3 contract is issued.

Before continuing:

1. preserve the current worktree;
2. synchronize with the remote safely without discarding local changes;
3. verify existing changes against this exact V3 scope;
4. discard or correct only changes that are out of scope or incorrect;
5. implement heartbeat, stalled detection, scope-amendment governance UX, and complete Codex handoff preparation;
6. rerun all required tests and release gates;
7. create evidence and commit only under the new AI Bridge-issued, hash-bound V3 Execution Contract.

Do not create evidence, claim PASS, or commit the Sprint 015 implementation against the superseded V1 or V2 authority.

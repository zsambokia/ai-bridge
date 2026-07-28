# Sprint 015 — Real-Time DEV Execution Activity and Checklist

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`

## 1. Goal

Make every governed AI Bridge execution observable in near real time during DEV mode.

A Product Owner or developer must be able to see, through ChatGPT and server-side console output:

- where the execution currently is;
- what meaningful activity is happening now;
- which checklist items are complete, active, pending, failed, or blocked;
- where the execution encountered an error;
- whether AI Bridge is diagnosing and repairing the error;
- whether the repair succeeded;
- whether the run is blocked and why;
- when the Sprint is ready for Product Owner review.

The output must be concise, readable, friendly, and optionally decorated with emojis for visual clarity. It must not expose raw stack traces, secrets, unbounded command output, or invented progress.

## 2. Explicit scope boundary

This is an AI Bridge feature, not an ASF employee or meeting system.

Do not implement:

- employees;
- named virtual team members;
- employee assignment;
- role inheritance;
- meeting threads;
- Slack-style channels;
- fictional actors or fake participants.

Allowed actor labels are system-level execution roles only, for example:

```text
AI Bridge
Codex
Dev
QA
Release Gates
Documentation
```

Use a label only when it truthfully represents the component or phase producing the event.

## 3. Product experience

The intended DEV-mode experience is similar to:

```text
Mesél az erdő Sprint

🟢 Started

Checklist
☑ Preflight and contract validation
☑ Repository assessment
☑ Existing architecture identified
☒ UI implementation
☐ Targeted tests
☐ Release gates
☐ Evidence and closure

🔍 Codex
Megvizsgálom a repository jelenlegi struktúráját.

💡 Dev
Meglévő navigációs rendszert találtam, ezért azt használom tovább.

🎨 Dev
Elkészült a reszponzív alkalmazás-layout.

⚠️ Dev
A build hibás import miatt megállt. Megkezdtem a diagnózist.

🔧 Codex
Az import útvonalát javítottam. Újrafuttatom az érintett ellenőrzést.

✅ QA
A javítás sikeres. A build és a célzott tesztek átmentek.

🏁 AI Bridge
PASS — READY FOR PRODUCT OWNER REVIEW
```

The exact wording may differ, but the semantic content must be truthful and derived from durable execution state and events.

## 4. Governing principles

1. Reuse the existing canonical execution lifecycle, `ExecutionRun`, execution events, provider dispatch, repair loop, audit, and MCP tools.
2. Do not create a parallel activity lifecycle or second execution status model.
3. Every displayed progress statement must be backed by a persisted event or current canonical execution state.
4. DEV mode may expose more operational detail than normal mode, but still must remain human-readable and safe.
5. Ordinary technical failures must trigger the existing diagnose-repair-rerun loop where safely possible.
6. Self-repair must never be silent: error, diagnosis, repair attempt, rerun, and outcome must be visible.
7. The Product Owner must not receive raw stack traces or secret-bearing logs.
8. Checklist completion must be computed from real execution milestones, not guessed percentages.

## 5. Mandatory assessment before implementation

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
- any current checklist, milestone, progress, or phase projection logic.

Classify relevant components as:

```text
ALREADY_REUSABLE
PARTIALLY_REUSABLE
MISSING
DUPLICATE
UNSAFE_FOR_DEV_OUTPUT
```

Implement only the smallest missing pieces.

## 6. Canonical activity events

Extend the existing ordered execution events only where necessary.

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

Do not create redundant event types where an existing canonical event already expresses the same fact.

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

`details` may include safe values such as:

- command name without secrets;
- exit code;
- repair attempt number;
- changed file paths;
- test or gate name;
- blocker classification;
- provider execution ID;
- final commit SHA;
- evidence path.

## 7. DEV-mode output rules

Introduce or reuse one explicit DEV observability setting.

Example intent:

```text
AI_BRIDGE_DEV_EXECUTION_ACTIVITY=true
```

Do not hardcode the exact setting name if a canonical environment or Django setting already exists.

When DEV activity is enabled:

- persist detailed but bounded structured events;
- print a readable one-line or compact multi-line representation to the server console;
- expose the same truthful activity through MCP for ChatGPT;
- include error and repair progress;
- include checklist changes;
- include the current blocker, if any.

When disabled:

- preserve the durable event stream required for audit and lifecycle correctness;
- allow a more concise user-facing projection;
- do not remove evidence required for governance.

Console output must:

- be human-readable;
- use emojis only as decoration;
- avoid ANSI-dependent formatting unless already supported safely;
- avoid raw stack traces in the normal activity feed;
- retain detailed tracebacks only in protected technical logs where existing policy allows;
- redact secrets and credentials;
- limit message size.

## 8. Checklist projection

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

Each item must have one status:

```text
PENDING
IN_PROGRESS
COMPLETED
FAILED_REPAIRING
BLOCKED
```

User-facing symbols may be:

```text
☐ PENDING
☒ IN_PROGRESS
☑ COMPLETED
⚠ FAILED_REPAIRING
⛔ BLOCKED
```

Checklist state must be derived from lifecycle and persisted events. It must not be independently edited into a contradictory state.

The checklist response must include:

- stable item ID;
- label;
- status;
- completion timestamp when complete;
- latest explanatory message;
- related event sequence where applicable.

Do not use a fake numeric completion percentage unless it is deterministically derived from completed checklist items and clearly identified as a checklist ratio rather than estimated work effort.

## 9. ChatGPT and MCP surface

Preserve existing tools and extend them where appropriate.

At minimum:

### 9.1 `execution.list_events`

Ensure it returns ordered, bounded, human-projectable events containing enough information to show meaningful DEV activity.

### 9.2 Execution activity summary

Add one canonical read-only tool only if the assessment proves existing tools cannot provide a compact current view.

Preferred capability:

```text
execution.get_activity_summary
```

It should return:

```yaml
execution_token: string
status: current run status
phase: current phase
current_activity: concise description
checklist: ordered checklist items
latest_events: bounded recent meaningful events
error_state: null or concise safe error summary
repair_state: null or current attempt and action
blocker: null or canonical blocker
final_result: null or terminal result
```

The tool must be read-only, bounded, audit-safe, and derived from canonical state.

Do not require ChatGPT to reconstruct checklist state by interpreting raw stdout.

## 10. Real-time behaviour

The system must expose new meaningful events while execution is still running.

Acceptable implementation options include the smallest repository-compatible mechanism such as:

- provider progress callback;
- structured provider output protocol;
- bounded polling with incremental event ingestion;
- worker-side event emission;
- subprocess line parsing only when based on an explicit stable marker protocol.

Do not claim real-time activity if events are generated only after the provider exits.

The implementation must prove that at least three distinct meaningful events become visible before execution completion.

This Sprint does not require WebSockets, Server-Sent Events, push notifications, or a new frontend dashboard unless already present and trivially reusable. Pollable near-real-time MCP and console visibility is sufficient.

## 11. Error visibility and autonomous repair

When an ordinary technical failure occurs, the activity stream and checklist must show:

1. where the failure occurred;
2. a concise safe explanation;
3. that diagnosis started;
4. the identified root cause when available;
5. the repair attempt number;
6. what was changed at a meaningful level;
7. which validation is being rerun;
8. whether repair succeeded;
9. whether another retry begins;
10. whether the run becomes legitimately blocked.

Required repair narrative example:

```text
⚠️ Build failed
A frontend import could not be resolved.

🔍 Diagnosing
Checking the changed component and existing module paths.

🔧 Repair attempt 1
Corrected the import path in `src/pages/Characters.tsx`.

🧪 Validation rerun
Running the frontend build again.

✅ Repair successful
The build now passes.
```

The activity layer must not invent root causes from incomplete data. Use wording such as `diagnosis in progress` until the cause is proven.

Existing retry limits and governance rules remain authoritative. Do not weaken tests, gates, typing, migrations, or acceptance criteria to obtain PASS.

## 12. Django admin visibility

Extend the existing execution contract or execution run admin detail page with a read-only Activity section if an appropriate page already exists.

Minimum display:

- current lifecycle and phase;
- current activity;
- ordered checklist;
- recent events;
- current error or repair state;
- blocker;
- completion result.

Do not create a separate administrative application or complex dashboard.

## 13. Required tests

Add automated tests for at least:

1. ordered event persistence;
2. DEV activity setting behaviour;
3. safe event projection without secrets;
4. bounded message and detail size;
5. checklist derivation from lifecycle and events;
6. checklist transitions through running, repair, blocked, and completed states;
7. execution activity summary response;
8. meaningful events becoming queryable before provider completion;
9. error event visibility;
10. repair attempt visibility;
11. successful repair and rerun visibility;
12. legitimate blocker visibility;
13. no fictional actor labels;
14. console projection formatting;
15. Django admin read-only activity rendering;
16. compatibility with existing `execution.get_run_status` and `execution.list_events`;
17. no duplicate execution lifecycle or parallel status source;
18. no raw stack trace or secret leakage through MCP activity responses.

## 14. Proving scenario

Run one real governed proving execution in DEV mode.

The proof must demonstrate before completion:

- execution started;
- repository assessment activity;
- at least one implementation or file-change activity;
- checklist transitions visible through MCP;
- console activity output;
- at least one technical failure and autonomous repair cycle, using a safe controlled scenario if necessary;
- release gate progress;
- final closure event.

The final proof must include the actual ordered events and checklist snapshots from multiple timestamps.

Do not fabricate events after the run to simulate real-time behaviour.

## 15. Release Gates

Run all canonical repository-wide gates resolved from `.bridge/project.yaml`, the current Constitution, and affected components.

At minimum, if still canonical:

```text
python manage.py makemigrations --check --dry-run
pytest -q
ruff check .
ruff format --check .
mypy .
git diff --check
```

Any technical failure must follow:

```text
DETECT → DIAGNOSE → REPAIR → RERUN
```

Continue until all required gates pass or one legitimate blocker is proven.

## 16. Evidence

Evidence root:

```text
docs/evidence/sprint-015-real-time-dev-execution-activity-and-checklist/
```

Required artifacts:

```text
CLOSURE_REPORT.md
assessment.md
acceptance-results.json
activity-event-schema-validation.json
real-time-event-ingestion-validation.json
checklist-projection-validation.json
mcp-activity-summary-validation.json
console-output-validation.json
error-and-repair-visibility-validation.json
admin-activity-view-validation.json
secret-redaction-validation.json
proving-execution-events.json
proving-execution-checklist-snapshots.json
```

Evidence must prove:

- events were visible before execution completion;
- checklist items changed truthfully over time;
- an error and repair cycle were visible;
- no employee or fictional participant layer was introduced;
- ChatGPT can retrieve a concise current activity summary;
- console and MCP projections represent the same canonical events;
- final repository state passes all gates.

## 17. Acceptance criteria

The Sprint passes only when all are true:

- [ ] DEV mode shows meaningful execution activity while a run is still active.
- [ ] ChatGPT can query where the execution currently is and what it is doing.
- [ ] Server console shows concise, readable, emoji-decorated activity.
- [ ] A continuously updated checklist is available.
- [ ] Completed items are visibly checked.
- [ ] The active item is visibly marked.
- [ ] Pending items remain unchecked.
- [ ] Errors are shown without raw stack traces.
- [ ] Diagnosis and autonomous repair attempts are shown.
- [ ] Repair success, retry, blocker, and completion are shown truthfully.
- [ ] At least three meaningful activity events are observable before execution completes.
- [ ] Checklist state is derived from canonical execution state and events.
- [ ] Existing execution lifecycle, provider, audit, and repair components are reused.
- [ ] No employee, meeting-thread, channel, or fictional participant model is added.
- [ ] MCP output is bounded and secret-safe.
- [ ] Django admin shows a minimal read-only activity view.
- [ ] All release gates pass.
- [ ] Final evidence is committed and bound to the execution.

## 18. Required Codex behaviour

Codex must:

1. assess before implementing;
2. reuse the current execution event and repair infrastructure;
3. keep the implementation narrow;
4. emit truthful progress during its own proving execution;
5. repair ordinary technical failures autonomously;
6. show those failures and repairs through the new activity layer;
7. avoid raw technical noise in Product Owner-facing output;
8. update affected architecture, workflow, MCP, admin, and AKB documentation;
9. produce fresh evidence from the final commit;
10. finish only as:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
```

or one constitutionally legitimate blocker state.
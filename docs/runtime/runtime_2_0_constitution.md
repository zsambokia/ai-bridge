# AI Bridge Runtime 2.0 Constitution

**Status:** Canonical Runtime 2.0 specification — Phase 0, Product Owner approved  
**Execution mode:** Factory Development Mode (documentation and architecture only)  
**Version:** 1.0.0  
**Date:** 2026-08-09

## Constitutional scope and interpretation

This document is the canonical architecture specification for **AI Bridge Runtime
2.0**. It defines the target responsibility model, not a retrospective claim that
the current repository already implements or is certified against that model.
Existing records, source names, diagrams, and evidence retain their historical
meaning until a governed migration and a Constitution Compliance Assessment
produce new evidence.

The repository-wide [Bridge Constitution](../constitution/BRIDGE_CONSTITUTION.md)
remains the governing constitution for project, scope, delivery, and release
governance. A Runtime 2.0 change SHALL comply with both documents. Where this
document gives a Runtime-specific rule, it refines rather than weakens the
repository-wide Constitution.

Normative words **SHALL**, **MUST NOT**, **SHOULD**, and **MAY** are binding as
defined by their ordinary standards meaning. A conflict SHALL be resolved by a
formal constitutional amendment; it MUST NOT be resolved by an implementation
shortcut.

## Chapter 1 — Runtime Authority

### 1.1 Canonical terminology

**Mission State Machine (MSM)** is the sole canonical name for the
mission-oriented Runtime authority. The following are deprecated architecture
terms and MUST NOT be used for new components, interfaces, or documentation:

| Deprecated term | Runtime 2.0 treatment |
| --- | --- |
| Orki / Orki Runtime | UX persona or historical compatibility name only |
| OESM | historical mission-state name; migration compatibility only |
| Orchestrator | insufficiently precise; do not use as a component name |
| Mission Orchestrator | replaced by MSM |
| Workflow Orchestrator | not an MSM synonym; replace with the relevant Workflow Engine responsibility |
| Runtime Orchestrator | replaced by MSM where mission authority is meant |

`Orki` MAY remain a product, conversation, or persona label. It is never a
second architectural authority.

### 1.2 Mission authority

The MSM owns the Mission lifecycle and no Domain Engine does. Its exclusive
responsibilities are Mission creation, Mission state transitions, Mission
Context publication, governance and approval initiation, Product Owner
projection, Engine Work Item authorization, Engine-result interpretation,
reflection initiation, and Mission closure.

The MSM MUST NOT execute a Domain Engine, mutate a Domain Engine's internal
state machine, perform planning, perform workflow, call a repository, or carry
out knowledge operations. It coordinates through declared intent, durable
Operational Work Items, results, and evidence.

### 1.3 Runtime responsibility and layering

```text
Conversation Projection
        │
        ▼
Mission State Machine (mission authority)
        │
        ▼
Operational Work Item
        │
        ▼
Operational Engine Foundation
        │
        ▼
ExecutionRun → Provider Gateway → Provider
```

Domain Engines are outside this execution chain. They support Mission decisions
by emitting immutable Execution Requests:

```text
Domain Engine → Execution Request → MSM
```

### 1.4 Domain authority

Each Domain Engine owns one bounded operational concern and, where applicable,
its own internal state machine. Planning, Workflow, Repository, Knowledge,
Reflection, Learning, Deployment, and Documentation are examples. Engines MAY
consume their authorized Work Items, persist their own state, produce evidence,
and declare a new Execution Request. Engines MUST NOT call another Engine,
Provider Gateway, Provider, or `ExecutionRun` directly.

### 1.5 Mission Resolution capability

Mission Resolution is an MSM capability, not a separate mission authority. It
first resolves an Engine need from authorized internal sources: AKB, Repository,
Bootstrap, Memory, semantic search, Company Knowledge, prior Missions,
Configuration, Provider metadata, and Environment facts. Only a genuine
business decision unresolved by those sources is projected to the Product Owner.

### 1.6 Conversation and persona boundary

The Conversation Layer knows only Mission and its authorized projections. It
does not own Planning, Workflow, Repository, Knowledge, or Runtime state. It
MUST NOT directly steer Engine state or execution. It presents the minimum
decision or status projection required for a human interaction; Orki is a
persona on this boundary, not a privileged control path.

## Chapter 2 — Authority Matrix

### 2.1 Authority matrix

| Concern | Exclusive authority | Permitted output | Prohibited action |
| --- | --- | --- | --- |
| Mission lifecycle and governance | MSM | Mission state, context, decision, Work Item | executing a Domain Engine |
| Domain reasoning and internal state | relevant Domain Engine | result, evidence, Execution Request | creating Work Item or provider call |
| Work lifecycle and delivery mechanics | Operational Foundation | lease, retry, heartbeat, run state | mission authorization |
| Provider transport | Provider Gateway adapter | provider receipt | governance or Mission transition |
| Business decision | Product Owner through Conversation projection | decision response | direct Engine control |
| Conversation presentation | Conversation Layer | projection and input | Planning/Workflow/Repository/Knowledge authority |

### 2.2 Operational Work Item authority

Only the MSM MAY create, authorize, merge, defer, transform, or cancel an
Operational Work Item. The Foundation MAY schedule, lease, retry, recover, and
record it only after MSM authorization. A Work Item is neither a Mission nor an
Engine state transition.

### 2.3 Engine interaction rule

An Engine MUST NOT call an Engine. Cross-domain progression is durable and
MSM-mediated:

```text
Planning result → MSM → Operational Work Item → Repository Engine
```

It MUST NOT be implemented as `Planning → Repository.call()`. This prevents
cyclic dependencies and preserves a reconstructible call graph.

### 2.4 Product Owner question policy

An Engine MUST NOT question the Product Owner directly. Its unresolved need is
an Execution Request or Engine result for MSM resolution. The MSM SHALL exhaust
authorized internal resolution before projecting a true decision to Conversation.
The Product Owner is a decision authority, never an API fallback.

### 2.5 Planning gate

The Planning Engine MUST NOT create a plan until the MSM has published
`MISSION_READY_FOR_PLANNING`. Internal Planning state transitions remain owned
by Planning; the gate is a Mission-level authorization, not a MSM mutation of
Planning state.

### 2.6 Execution Request immutability

An **Execution Request** is an immutable declaration of intent from an allowed
origin. It is not an execution command, execution authorization, Operational
Work Item, or provider call.

```text
Domain Engine --declare--> Execution Request --> MSM
                                                ├─ Reject
                                                ├─ Defer
                                                ├─ Merge
                                                ├─ Transform
                                                └─ Accept → Operational Work Item
```

Only the MSM MAY interpret, transform, or authorize an Execution Request into
an Operational Work Item. Once created, it MUST NOT be modified by its origin,
the Foundation, Gateway, or Provider. A changed intent SHALL create a new
Execution Request.

## Chapter 3 — Constitutional Compliance

### 3.1 Machine-verifiable architecture

The Constitution is executable: each constitutional rule SHALL map to one or
more static architecture checks, runtime governance validations, audit evidence
requirements, or automated architecture tests. Documentation intent, approval,
or migration planning is not compliance evidence.

### 3.2 Execution Request identity and governance snapshot

Every Execution Request SHALL contain `requestId`, `missionId`, `originId`,
`correlationId`, `idempotencyKey`, `policyContext`, `createdAt`, `requestType`,
and `requestVersion`.

| Field | Meaning and rule |
| --- | --- |
| `requestId` | globally unique, immutable identity of this request |
| `missionId` | exactly one Mission identity |
| `originId` | permitted origin, such as Engine, Work Item, or Conversation |
| `correlationId` | non-unique logical trace link across Request, Work Item, Run, audit, and evidence |
| `idempotencyKey` | deterministic duplicate-detection key |
| `policyContext` | immutable, versioned decision snapshot |
| `createdAt`, `requestType`, `requestVersion` | immutable creation and contract data |

`policyContext` SHALL contain, or reference by immutable hash, `policyVersion`,
`policySnapshotHash`, `governanceVersion`, and `authorizationSnapshotHash`.
Runtime policy mutation MUST NOT alter the original authorization context.

### 3.3 Idempotency

Duplicate requests SHALL be detected from `idempotencyKey`, never merely from
`requestId`. A conforming key is deterministically derived from `missionId`,
`originId`, `requestType`, `requestVersion`, and `intentFingerprint`, for
example `SHA256` over that ordered tuple. MSM processing SHALL be idempotent so
deduplication, merge, retry, and replay are safe.

### 3.4 Architecture-test layers

| Layer | Proves | Minimum example |
| --- | --- | --- |
| Static architecture | prohibited imports, references, and calls | Engine → Provider Gateway/Provider/ExecutionRun is forbidden |
| Runtime governance | authorization is enforced at runtime | no ExecutionRun begins without MSM-authorized Work Item |
| Evidence verification | test outcome is traceable and retained lawfully | result points to versioned Evidence Records |

### 3.5 Compliance evidence

Every Architecture Test SHALL generate an Evidence Record containing at least
Rule, Result, Evidence reference, Timestamp, MissionId where applicable, and
CorrelationId where applicable. Evidence is necessary for, but does not by
itself guarantee, a particular level: the level is the result of the applicable
evaluation.

### 3.6 Compliance levels

| Level | Meaning |
| --- | --- |
| L0 | not assessed |
| L1 | static compliance verified |
| L2 | runtime compliance verified |
| L3 | evidence verified |
| L4 | Constitution certified |

L4 SHALL require L1, L2, and L3, and no open Critical or High-severity
deviation in the assessment scope. A component MUST NOT self-declare L4.

### 3.7 Traceability chain

```text
Constitution Rule → Architecture Test → Evidence → Compliance Result → Gap
→ Migration Decision → Migration Execution → Re-test → New Evidence
→ Updated Compliance
```

Every architectural decision SHALL be traceable from constitutional rule to
executable evidence. A Migration Decision represents implementation intent only;
it is not evidence and does not change a Compliance Level.

### 3.8 Compliance state transition

Compliance is an observed property, not a declared property. A Compliance Level
SHALL change only after successful re-evaluation against the current
Constitution, applicable tests, and newly generated evidence. Prior evidence
remains historically traceable and new evidence supersedes it through versioned
links, not overwrite.

### 3.9 Evidence preservation

Evidence Records SHALL be immutable and append-only for their legally permitted
retention period. A changed payload creates a new record and preserves the
prior record subject to Chapter 3.10. Each Compliance Result SHALL identify the
Constitution version, rule(s), executed test(s), Evidence version(s), assessment
timestamp, evaluator identity, and result.

### 3.10 Evidence retention and legal preservation

**Constitutional principle:** The system SHALL preserve auditability for the
legally permitted retention period, without retaining prohibited content or
prohibited personal data.

The system distinguishes Evidence Content from a data-minimized Evidence Record.
The Record SHOULD contain only Evidence Identifier, creation timestamp, type,
Mission Identifier or pseudonymous equivalent, Correlation Identifier, integrity
hash, Constitution version, Evidence version, origin, and retention status. It
MUST NOT retain data whose retention is unlawful.

Evidence Content MAY be archived, encrypted, access restricted, pseudonymized,
cryptographically destroyed, or permanently removed only under an approved
Retention Policy and applicable legal authority. This MUST NOT rewrite or
falsify the historical audit chain.

Every retention operation SHALL create an immutable, data-minimized **Retention
Event** with its identifier, original Evidence Identifier, Retention Policy
version, legal basis, authorizing authority, timestamp, integrity verification,
and result. **The Retention Event becomes part of the audit history for the
legally permitted retention period.**

Within legal limits, the system SHALL demonstrate that evidence existed, when it
was created, the applicable Constitution and retention policy, and why content
became unavailable. Where law also requires identifying metadata removal, only
the strongest legally permissible residual audit trail MAY remain, including
proof that removal followed approved policy.

**Axioms:** Retention preserves auditability, not necessarily data. Compliance
is bounded by law; auditability SHALL be maximized within those boundaries.

### 3.11 Initial Architecture Test Specification

| Rule | Test | Evidence outcome |
| --- | --- | --- |
| 1.4 / 2.3 | dependency and call-graph scan | no Engine-to-Engine or Engine-to-provider path |
| 2.2 / 2.6 | Work Item creator and immutable-request contract test | MSM-only authorization and mutation rejection |
| 2.4 | conversation ingress integration test | unresolved business decision is MSM-projected |
| 2.5 | Planning gate integration test | Planning rejects absent Mission readiness |
| 3.2 / 3.3 | identity and replay test | snapshot and idempotency trace |
| 3.4 | runtime authorization test | rejected run without authorized Work Item |
| 3.8–3.10 | evidence/retention test | append-only, versioned, lawful retention trace |

## Chapter 4 — Operational Engine Constitution

The Operational Engine Foundation is common infrastructure, never a business
domain. It SHALL provide Engine Runtime, Queue, Polling, Work Item lifecycle,
Health, Scheduler, Recovery, Retry, Telemetry, Heartbeat, Outbox, Evidence,
Projection, Configuration, Ports, and Adapter Registry.

An Engine consumes a durable authorized Work Item, records progress and
evidence, publishes a durable result, and becomes idle. It owns its bounded
state and recovery semantics. The Foundation owns mechanical delivery,
lease/retry/reconciliation, and observability; it MUST NOT infer Mission intent
or mutate Domain state. `ExecutionRun` is an operational execution attempt,
not a Mission or Engine state machine.

Ports are the only permitted external boundary. The Adapter Registry binds a
configured adapter to a Port under governance. Provider adapters are reachable
only through Provider Gateway ports. Future Engines SHALL adopt this same
contract rather than introduce bespoke queues, hidden schedulers, or direct
cross-engine calls.

## Chapter 5 — Mission Resolution Constitution

Mission Resolution receives a declared unresolved need and first seeks an
authorized internal answer. Its sequence is: identify the missing fact or
decision; resolve through eligible context; attach provenance and confidence;
continue the requesting flow if sufficient; otherwise produce a concise
decision projection for the Product Owner.

Resolution MAY cause the MSM to authorize a Repository, Knowledge, Bootstrap,
or other Engine Work Item. It MUST NOT synchronously invoke that Engine, mutate
its state, or present an internal lookup failure as a business question. The
result is a Mission Context update or an authorized next action, both with
traceable evidence. Engines never call the Conversation Layer or another Engine
to bypass this route.

## Chapter 6 — State Machine Constitution

```text
MSM (Mission)
 ├─ Planning State Machine (Planning Engine)
 ├─ Workflow State Machine (Workflow Engine)
 ├─ Repository State Machine (Repository Engine)
 ├─ Knowledge State Machine (Knowledge Engine)
 ├─ Reflection State Machine (Reflection Engine)
 ├─ Deployment State Machine (Deployment Engine)
 └─ Learning State Machine (Learning Engine)
             │
             ▼
Operational Engine Foundation → ExecutionRun → Provider Gateway → Provider
```

The MSM owns Mission state only. Each listed Domain Engine owns its own
transitions, terminal states, and recovery rules. The MSM observes results and
decides Mission consequences; it MUST NOT advance a Domain state directly.
Conversely, no Domain state machine may transition Mission state. Cross-machine
communication is through durable requests, Work Items, results, events, and
evidence.

## Chapter 7 — Conversation Constitution

Conversation is an ingress and projection boundary. It SHALL project Mission,
Planning, approval, execution, and evidence states in read-only or explicitly
authorized command forms. Panels are projections of canonical state, not
parallel mutable stores. User input is recorded as conversation evidence and
submitted to MSM governance; it does not directly operate an Engine or Provider.

Conversation MAY render Orki's persona. It MUST NOT become a Planning,
Workflow, Repository, Knowledge, provider, or execution authority. Presentation
choices do not alter Runtime authority or authorization requirements.

## Chapter 8 — Execution Constitution

The only conforming execution chain is:

```text
Domain Engine → immutable Execution Request → MSM
→ authorized Operational Work Item → Operational Foundation
→ ExecutionRun → Provider Gateway → Provider
```

An ExecutionRun SHALL have a traceable authorized Work Item, Mission,
correlation, policy snapshot, and evidence path. Provider invocation requires a
Gateway adapter bound through a governed Port. Direct Engine-to-Gateway,
Engine-to-Provider, Engine-to-ExecutionRun, Conversation-to-Provider, and
Provider-to-Mission transitions are prohibited. Retry and recovery repeat or
create governed operational attempts; they MUST NOT manufacture authorization.

## Chapter 9 — Knowledge and Evidence Constitution

Knowledge and Evidence are distinct. Knowledge is governed, attributable domain
information usable for Mission Resolution; Evidence is an auditable observation
of an action, test, state, or decision. Neither is automatically the other.

AKB, semantic indexes, repository facts, and Company Knowledge SHALL preserve
origin, qualification, access classification, version, and retrieval provenance.
Search ranks or retrieves candidates; it does not decide, authorize execution,
or mutate Mission state. Knowledge promotion and index mutation remain owned by
their relevant Domain Engine and governance.

The Evidence Store SHALL support integrity hashing, versioned references,
append-only creation, access control, data classification, encryption where
required, and legal retention workflows. Its technical implementation SHALL
honour Chapter 3's compliance and lawful-retention rules. Evidence projection is
read-only; a projection cannot amend the underlying record.

## Chapter 10 — Migration Constitution

Runtime 2.0 migration SHALL be incremental, evidence-driven, compatible where
required, and reversible through a governed rollback plan. New implementation
MUST use `Mission State Machine (MSM)` for mission authority. `Orki` is limited
to UX/persona usage. `OESM`, `Runtime Orchestrator`, `Mission Orchestrator`, and
similar legacy names MAY appear only in historical evidence, compatibility
adapters, or explicitly labelled migration material.

A migration SHALL include component mapping, dependency and call-graph review,
authority verification, gap analysis, Architecture Test specification, rollback
boundary, and fresh Compliance Evidence. It MUST NOT claim compliance merely
because a name changed, a decision was approved, or a plan was deployed.

### 10.1 Architecture freeze

After adoption of this Constitution, a new Operational Engine, Runtime authority
change, significant state-machine refactor, or boundary change requires an
approved constitutional amendment and a Constitution Compliance process before
implementation. A Sprint implements a Constitution-conformant bounded change;
it cannot silently redefine the Constitution.

### 10.2 Phase 0 completion criteria

Phase 0 is complete when this document is present as the primary Runtime 2.0
specification, its ten chapters are internally coherent, its legacy migration
rules are explicit, and future work can reference its normative requirements.
Phase 0 creates no implementation, no Runtime certification, and no automatic
Compliance Level. A subsequent Constitution Compliance Assessment SHALL produce
the Component Mapping Matrix, Authority Verification Report, Dependency Graph,
Call Graph, Compliance Score, Gap Analysis, Migration Roadmap, Architecture
Test Specification, and Evidence Package.

## Constitutional strategic objective

AI Bridge Runtime 2.0 is not one large Runtime with many modules. It is a
Mission-centred, Engine-based AI Operating System: the MSM coordinates Missions;
independent Operational Engines execute well-defined bounded capabilities on
common infrastructure, with consistent lifecycle, evidence, and responsibility
boundaries.

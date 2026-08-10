---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Runtime Foundation Baseline

**Status:** approved architectural baseline; operational validation pending
**Scope:** Orki Runtime Foundation
**Authority:** Product Owner approval for
`bridge:ai-bridge:sprint:712aef15-2426-4f57-88b6-8b1389807b3e`

## Purpose

This document is the stable reference point for the Runtime Foundation. It
records the architectural boundaries that future Semantic Layer, Behaviour,
Reasoning, Persona, and Multi-Agent work must preserve. It is intentionally a
set of durable principles, not an implementation guide or replacement for the
Constitution, Governance policy, or the detailed Orki Runtime design.

The baseline becomes the release baseline after operational validation has
passed and the approved work has been merged, tagged, and reported. Until then,
it is the accepted Foundation target on the Runtime integration branch.

## Canonical model

```text
Knowledge / Cognitive State       -> what the platform knows
Reasoning                         -> how alternatives are understood and decided
Goal -> Plan -> Execution         -> what the platform is doing
OESM / Runtime                    -> how execution progresses safely
Governance                        -> what is authorized
Presentation                      -> how the persisted Runtime truth is shown
```

The normal Runtime closure is:

```text
Goal -> Understanding -> Candidate selection -> Reasoning -> Planning
-> Execution preparation -> Execution -> Verification -> Reflection
-> Knowledge Integration (when justified) -> Completed
```

## Baseline principles

1. **Goal-first execution.** Every Runtime execution belongs to one durable
   Goal. An Execution always binds one selected Plan; a Goal may have several
   plans or plan versions over time.

2. **One Runtime ingress.** User-initiated Factory Chat work creates or reuses
   an Orki Runtime execution. Factory Chat is a presentation and ingress
   adapter, never a provider-dispatch bypass.

3. **OESM coordinates; it does not reason.** The Orki Execution State Machine
   owns lifecycle transitions, waits, recovery, progress derivation, and audit
   events. It does not become a planner, critic, persona, or knowledge store.

4. **Reasoning does not execute.** Understanding, candidate selection,
   deliberation, and structured decision preparation may inform a Plan, but
   they cannot invoke providers, tools, jobs, or repository changes directly.

5. **Cognitive State is not Execution State.** Cognitive State answers
   "what do I know?" and owns knowledge, assumptions, evidence interpretation,
   and cognitive context. Runtime answers "what am I doing?" and stores only
   execution facts, references, lifecycle events, and projections.

6. **Governance retains authorization ownership.** Proposal, scope, approval,
   contract, and existing governed execution ownership stay with Governance and
   `ExecutionRun` / `ExecutionJob`. Runtime observes and coordinates those
   facts; it does not create a parallel approval, queue, contract, or execution
   lifecycle.

7. **Providers are adapters, not orchestrators.** Provider selection and
   transport remain provider-neutral behind existing adapters. A provider has no
   authority to determine lifecycle, authorization, or UI truth.

8. **Verification precedes learning.** Goal Integrity Validation compares
   intended outcomes and acceptance checks with observed changes, tests, and
   evidence. A Goal cannot be manually declared complete in place of that
   verification.

9. **Reflection precedes Knowledge Integration.** Reflection records a
   governed analysis of a completed execution. Only after completed Reflection
   may Runtime submit a knowledge candidate; it cannot directly write Cognitive
   State, activate AKB knowledge, or create embeddings.

10. **Existing AKB governance owns knowledge activation.** Knowledge
    Integration submits a candidate with evidence. Existing AKB Governance
    alone reviews, approves, activates, and indexes it. Execution events are
    audit evidence, not automatically shared knowledge.

11. **Runtime state is the UI source of truth.** The Live Runtime Monitor
    renders server-owned OESM projections: state, Goal, planning status,
    progress, concrete waiting reason, recovery, reflection, Knowledge
    Integration, and evidence references. The browser must not infer lifecycle
    state from client-side heuristics or provider text.

12. **Waiting and recovery are first-class states.** Approval, governance,
    external dependency, and user-input waits are explicit and durable. Pause
    retains the prior state; resume and recovery are observable state-machine
    transitions rather than ad hoc retries.

13. **Events are append-only evidence.** Runtime events are ordered, durable,
    actor-attributed, and evidence-linked. Observability is derived from this
    execution trail, not a second mutable status store.

14. **Semantic selection remains a boundary service.** Future Semantic Search
    and Persona viewpoints may select relevant Cognitive State references for
    Reasoning and Planning. They must not duplicate knowledge or bypass
    Governance and Runtime execution boundaries.

15. **Multi-Agent extends the plan, not the platform's ownership model.** A
    future Multi-Agent Runtime may attach agent assignments or sub-executions
    to a Plan while retaining a parent OESM trail, canonical evidence, existing
    approvals, and the same Cognitive State boundary.

## Change control

Future work may extend the baseline through an explicit approved architecture
decision. It may not silently weaken these ownership boundaries, add a second
state authority, or turn a provider, UI, semantic component, persona, or agent
into an unauthorized orchestrator.

Detailed design and transition rules remain in
`docs/architecture/ORKI_ORCHESTRATOR_RUNTIME.md`; acceptance evidence remains
in `docs/architecture/CANONICAL_FACTORY_ACCEPTANCE_SUITE.md` and the Sprint
evidence package.

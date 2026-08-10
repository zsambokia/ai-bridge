---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Architecture challenge

## Review answers

1. **Is Runtime too large?** It is at risk, not yet disposable. Keep it as mission/governance coordinator; move domain work behind ports.
2. **Separate Planning Runtime?** Yes: a Planning Engine with a PSM, not a second mission authority.
3. **Polling or event bus?** Polling plus transactional outbox now; optional event delivery later.
4. **Abstract base class or domain pattern?** Prefer a small protocol/contract and domain-specific engines. A large inheritance hierarchy would couple unrelated lifecycles.
5. **Is Task correct?** Yes for business-work intent. It must delegate authorized attempts to ExecutionRun/ExecutionJob.
6. **Conversation Engine?** No. Conversation is a boundary/presentation and command layer, with a durable transcript.
7. **Planning and Workflow contexts distinct?** Yes. Planning produces a governed proposal; Workflow realizes an approved plan.
8. **Common lifecycle?** Yes, only at the work-item protocol level. State machines remain domain-specific.
9. **Known patterns?** This resembles Kubernetes controllers (reconcile durable desired state), Temporal-style workflow/activity separation, DDD bounded contexts, and an outbox/event-driven architecture. LangGraph and BPMN are useful implementation/reference tools, not governance authorities.
10. **Redesign proposal?** Do not replace it wholesale. Correct its cross-boundary adapters first, then extract state ownership incrementally.

## Rejected alternatives

* A monolithic Runtime: simpler today but makes retries, ownership and testing increasingly ambiguous.
* Engines invoking engines: convenient locally but prevents independent recovery and produces cyclic dependencies.
* Provider-led workflow progression: conflates probabilistic output with authoritative governance.
* Event-bus-only orchestration: adds operational fragility before durable reconciliation is proven.

## Chosen trade-off

The recommended design accepts a little more durable protocol work in exchange for auditable ownership, restart recovery, deterministic gates, and a migration path that preserves the Runtime Foundation.

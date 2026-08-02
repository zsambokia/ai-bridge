# Orki Cognitive Operating System

**Constitution:** [Orki Principles](ORKI_PRINCIPLES.md) is the immutable behavioural authority. This document describes architecture; it cannot weaken the Principles.

**Status:** ORKI-001 Cognitive State, ORKI-002 Mission Understanding,
ORKI-003 Recommendation Engine, ORKI-004 Decision Intelligence, ORKI-005
Planning Intelligence, ORKI-006 Memory Intelligence, and ORKI-007 Initiative
Engine implemented. ORKI-008 Product Owner Cognitive Model and ORKI-009 Model
Evolution are accepted. ORKI-010 introduces the Operational Reasoning Engine
as the evidence-bound, reasoning-before-recommendation boundary.
**Authority:** Product Owner Factory Development Mode — Orki Cognitive Operating System Epic.

## Capability assurance

The [COO Capability Acceptance](ORKI_COO_CAPABILITY_ACCEPTANCE.md) gate and [Product Owner Scenarios](ORKI_PRODUCT_OWNER_SCENARIOS.md) measure behaviour, not only code correctness. They define the Digital COO Maturity Index (DCMI) and prevent an engineering-only PASS from being presented as Digital COO readiness.

## Intent

Orki is AI Bridge's Digital COO. It is not a questionnaire, planning wizard, or chat wrapper. Conversation contributes observations to persistent Cognitive State. The platform owns state, policies, evidence, and governance; an LLM supplies bounded reasoning only.

## Canonical flow

```text
Interface / conversation / events
  -> observation and evidence ingestion
  -> Cognitive State
  -> Mission Model, Project Model, Product Owner Model, and Factory Model
  -> Mission Understanding and Operational Reasoning Engine
  -> derived Recommendation, Decision, Planning, Memory, and Initiative capabilities
  -> reviewable Mission / Plan / governance-preparation artifacts
  -> existing approval, orchestration, contract, execution, evidence lifecycle
```

No provider may create approval, execution authority, accepted knowledge, or a delivery claim. The existing mandatory orchestration gate remains the sole normal path from approved work to a contract and run.

## Cognitive State

The persistent, project-isolated state represents: Mission, Business Context, Goals, Constraints, Facts, Evidence, Assumptions, Risks, Opportunities, Alternatives, Trade-offs, Recommendations, Confidence, Open and Accepted Decisions, Architecture, Roadmap, Sprint Strategy, Repository, Delivery Status, Learned Knowledge, Reasoning Trace, and Memory.

Each material item has identity, provenance, status, timestamps, confidence where relevant, and correction or supersession. Transcript is input history only, never primary memory.

The Cognitive Operating System coordinates four distinct models: Mission,
Project, Product Owner and Factory. Their scopes and permitted interactions are
defined by [the Product Owner Cognitive Model](ORKI_PRODUCT_OWNER_COGNITIVE_MODEL.md).

## Decision and question policy

```text
mission -> evidence -> assumptions and unknowns -> at least three alternatives
        -> trade-offs and counter-arguments -> impact -> recommendation
        -> confidence -> required Product Owner decision (only if necessary)
```

Questions consume a conversation-level budget. Before asking, Orki tests whether it can infer safely, use an explicit assumption, or recommend a reversible default. A question is allowed only when its answer materially changes the next safe action or crosses a governance/business boundary.

## Operational reasoning, planning and initiative

The [Operational Reasoning Engine](ORKI_OPERATIONAL_REASONING_ENGINE.md) is
the canonical reasoning cycle. A recommendation emerges only after it records
the mission, attributable evidence, unknowns, alternatives, trade-offs,
counter-arguments, cost/risk/long-term/simplicity analysis, expected impact,
confidence and any decision boundary. Factory Chat cannot write a direct
provider recommendation to state. Product Owner Model preferences can inform a
safe default only as explicit, evidence-bound influences in that artefact.

A plan is separately reasoned, not serialized chat fields. It includes objective, business value, architecture, alternatives, chosen and rejected strategy, risks, dependencies, acceptance, release and operational strategy, recovery, and future evolution. Initiative currently derives bounded observations from state-held risks, opportunities and missing evidence. Additional semantic detection for inconsistency, duplication, simplification, reuse, and better decomposition remains separately gated.

## Provider independence and UX

Provider prompts and formats are adapters behind a stable Orki reasoning contract. OpenAI, Claude, Gemini, Codex, and future providers must not change state semantics, decision policy, governance, or user-visible business behaviour. Chat is the conversational interface; the state view exposes what Orki knows, assumes, recommends, needs decided, and is preparing.

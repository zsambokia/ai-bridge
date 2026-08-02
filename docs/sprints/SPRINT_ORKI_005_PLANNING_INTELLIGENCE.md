# Sprint ORKI-005 - Planning Intelligence

**Status:** PASS â€” READY FOR PRODUCT OWNER REVIEW
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner autonomous-execution directive, 2026-08-02
**Prerequisites:** ORKI-001 accepted; ORKI-002 through ORKI-004 Release Gates - PASS

## Objective

Prove that Orki produces a durable, evidence-bound Cognitive Plan: a reasoning
artefact that explains a safe path from mission and recommendation to a future
governed delivery decision. It is not a chat summary, a legacy `FactoryPlan`,
a governance approval, or an execution command.

## Scope

- Add a project-isolated `PLAN` Cognitive State entry with revision history.
- Require cited same-project cognitive evidence and make the cited sources
  inspectable in the plan projection.
- Require objective, business value, architecture, alternatives, chosen and
  rejected strategy, risks, dependencies, acceptance, release, operational,
  recovery, and future-evolution strategies.
- Permit an LLM to propose structured plan observations only; validate the
  observation in deterministic Orki code with provider provenance.
- Keep planning distinct from the existing governed `FactoryPlan` delivery
  workflow, so planning cannot create work, change mission phase, approve
  governance, or execute.
- Validate revision, explainability, project isolation, transcript separation,
  provider independence, and public Factory-route non-escalation.

## Explicit exclusions

- No delivery-plan, Sprint, roadmap, repository, contract, governance, or
  execution creation.
- No decision acceptance, initiative, or memory capability.
- No UI redesign and no transcript-as-memory behaviour.

## Required behavioural scenarios

1. Mission and recommendation evidence yields a complete Cognitive Plan with
   explicit alternatives and a chosen/rejected strategy.
2. A plan cannot cite absent or foreign-project evidence, and it cannot select
   a strategy not represented by its alternatives.
3. A revised plan supersedes, but never erases, the prior plan.
4. The projection explains the plan through canonical evidence identifiers,
   values, confidence, and provenance rather than copied conversation text.
5. Provider-originated structured output cannot create a `FactoryPlan`, alter
   mission delivery state, create governance authority, or start execution.
6. Private transcript content remains in the conversation record and does not
   enter Cognitive State merely because a plan is proposed.

## Release Gate

PASS requires all required behavioural scenarios, focused and full backend
tests, browser E2E, schema checks, static analysis, architecture/ADR/AKB/
roadmap/documentation synchronization, an independent evidence assessment,
operational validation, and self-critique. Only then may ORKI-006 Memory
Intelligence begin automatically.

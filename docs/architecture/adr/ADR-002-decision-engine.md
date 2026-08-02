# ADR-002 - Decision Engine

**Status:** Implemented in ORKI-004; validated by independent Release Gate.

## Decision

Orki turns a material, evidence-backed recommendation into a platform-owned,
project-isolated open decision. Each decision preserves facts/evidence,
assumptions, alternatives, trade-offs, recommendation, confidence, options,
and the required Product Owner choice explicitly.

Only an explicit, attributable Product Owner confirmation with a durable
confirmation reference can accept an option. A provider response and a raw
conversation message may propose an open decision, but may never accept one.

## Consequences

Provider prose cannot be treated as an unexamined decision. The engine requires
structured decision records and explainable links to Cognitive State evidence.
Opening or accepting a decision does not create a plan, approve governance, or
execute work. The independent ORKI-004 behavioural evidence is recorded in
[`sprint-orki-004-decision-intelligence-20260802`](../../evidence/sprint-orki-004-decision-intelligence-20260802/ASSESSMENT.md).

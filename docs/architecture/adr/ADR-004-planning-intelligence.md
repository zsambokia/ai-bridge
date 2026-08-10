---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-004 - Planning Intelligence

**Status:** Implemented by ORKI-005; independent Release Gate PASS.

## Decision

Plans shall be first-class reasoning artefacts, not conversation summaries.
They shall record objective, business value, architecture, alternatives, chosen
and rejected strategies, risks, dependencies, acceptance, release, operational
recovery, and future evolution.

## Consequences

Plans need evidence and decision references, revision history, and validation
against execution scope. Template-only plan generation is insufficient. ORKI-005
implements an evidence-bound `PLAN` entry in the canonical Cognitive State:
the deterministic engine validates its required reasoning fields, references
same-project evidence, preserves superseded revisions, and projects its
explainability without transcript text.

The cognitive plan intentionally remains separate from the legacy `FactoryPlan`
delivery-workflow record. It cannot create governed work, advance a delivery
phase, approve governance, or start execution. Evidence is recorded in
[`sprint-orki-005-planning-intelligence-20260802`](../../evidence/sprint-orki-005-planning-intelligence-20260802/ASSESSMENT.md).

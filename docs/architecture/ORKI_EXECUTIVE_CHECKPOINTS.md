# Orki Executive Checkpoints

**Authority:** Product Owner Executive Directive, 2026-08-02
**Applies to:** Orki Cognitive Operating System Epic under Factory Development
Mode.

## Purpose and classification

An Executive Checkpoint is a durable, evidence-backed progress report for the
Product Owner. It provides visibility during a long autonomous delivery cycle.
It is **informational only**: it is neither a Product Owner review request nor
an approval, Release Gate, or scope-expansion mechanism.

Generating a checkpoint never pauses the Epic. The exact next authorised
capability Sprint begins automatically after its predecessor has passed every
resolved Release Gate, unless a genuine business decision, legal or compliance
constraint, or fundamental approved-Epic scope change is discovered.

Technical defects, failed tests, missing evidence, architecture gaps, and
ordinary implementation debt remain Codex-owned repair work. They follow the
normal `DETECT -> DIAGNOSE -> REPAIR -> RERUN` loop and are not reasons to wait
for Product Owner input.

## Current cadence

| Checkpoint | Trigger | Current capability boundary | Deterministic evidence location |
| --- | --- | --- | --- |
| A | ORKI-003 Release Gates PASS | Recommendation Engine | `docs/evidence/orki-executive-checkpoint-a-YYYYMMDD/EXECUTIVE_CHECKPOINT.md` |
| B | ORKI-006 Release Gates PASS | Memory Intelligence | `docs/evidence/orki-executive-checkpoint-b-YYYYMMDD/EXECUTIVE_CHECKPOINT.md` |

Checkpoint A is produced after Sprint 3 and execution continues immediately to
the already authorised Sprint 4. Checkpoint B is produced after Sprint 6 and,
provided all Sprint Release Gates remain PASS and no reserved Product Owner
decision exists, the remaining Epic Sprints continue automatically.

## Required report contents

Every checkpoint contains, and binds its statements to the then-current
repository state and Sprint evidence:

1. Executive Summary.
2. Epic completion percentage, including the calculation basis.
3. Current Sprint and its terminal Release Gate state.
4. Completed capabilities and remaining capabilities.
5. Current Digital COO Maturity Index (DCMI), its scored dimensions, evidence,
   and limitations. A DCMI must never be estimated or presented without its
   supporting capability evidence.
6. Capability matrix showing implemented, evidenced, planned, and explicitly
   excluded behaviour.
7. Release Gate status summary for every completed Sprint.
8. Technical-debt summary, including owner, impact, and containment.
9. Architecture evolution since the previous checkpoint (or since Epic start
   for Checkpoint A).
10. Major implementation decisions and their durable ADR/evidence references.
11. Known risks and their current mitigation or decision boundary.
12. Self-critique: behaviour still below the Digital COO standard, evidence
    weaknesses, and proposed corrective work.
13. A recommendation either to continue the approved Epic unchanged or to
    make a specific architectural adjustment. A recommendation is not a pause;
    only a fundamental scope change requires Product Owner direction.

## Execution boundary

The active Product Owner authority permits autonomous execution through
ORKI-003 Recommendation Engine, ORKI-004 Decision Intelligence, ORKI-005
Planning Intelligence, and ORKI-006 Memory Intelligence. Each still has its
own exact Sprint scope, fresh assessment, full Release Gates, independent
audit, operational validation, evidence, documentation, AKB, and roadmap
updates.

After Checkpoint B, the same autonomous continuation rule applies to the
remaining approved Epic capability sequence. A failed Release Gate is repaired
and rerun; it is not converted into a checkpoint PASS or an implicit request
for approval.

## Relationship to Release Gates and closure

Executive Checkpoints complement, but never replace, the mandatory COO
Capability Acceptance and all engineering, operational, backend, frontend,
browser E2E, migration, regression, governance, documentation, AKB, roadmap,
evidence, independent-audit, and self-critique gates.

The checkpoint report must accurately distinguish a Sprint Release Gate PASS,
operational evidence, and Product Owner acceptance. It may not claim Epic
completion, a higher DCMI, or a capability that has not been independently
proven.

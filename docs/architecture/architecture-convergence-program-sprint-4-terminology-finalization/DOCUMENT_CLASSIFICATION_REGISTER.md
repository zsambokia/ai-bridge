---
status: CURRENT
scope: Architecture Convergence Program – Sprint 4
language: en
---

# Documentation Classification Register

## Purpose

This register covers the complete `docs/` corpus assessed on 2026-08-10. It
prevents a terminology cleanup from rewriting evidence or accepted historical
decisions. A family rule applies to each file below that path unless a more
specific row names it.

| Path / document family | Files assessed | Classification | Terminology treatment |
| --- | ---: | --- | --- |
| `docs/constitution/BRIDGE_CONSTITUTION.md` | 1 | TRANSITIONAL | Repository governance remains binding; Architecture Book terms govern target terminology. |
| `docs/runtime/` | 1 | TRANSITIONAL | Runtime 2.0 remains a legacy-titled target input; use AI Kernel and Provider Integration in active technical references. |
| `docs/architecture/AI_KERNEL_ARCHITECTURE_CONSTITUTION.md` | 1 | APPROVED TARGET | Canonical Article III terminology source. |
| `docs/architecture/AKB_KNOWLEDGE_OBJECT_AND_LIFECYCLE_CONSTITUTION.md` | 1 | APPROVED TARGET | Canonical Article I target terminology source. |
| `docs/architecture/ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md` | 1 | APPROVED TARGET | Canonical authority boundary between Architecture and Implementation Convergence. |
| `docs/architecture/ARCHITECTURE_CONSTITUTION.md`, `ENGINE_CONSTITUTION.md`, `OPERATIONAL_FOUNDATION_CONSTITUTION.md`, `STATE_MACHINE_CONSTITUTION.md` | 4 | TRANSITIONAL | Keep governance role; add explicit target-term boundary and use Provider Integration adapter where referenced. |
| `docs/architecture/ARCHITECTURE_MAP.md`, `ARCHITECTURE_EVOLUTION.md` | 2 | HISTORICAL | Preserve topology/timeline as evidence; do not normalize legacy diagrams. |
| `docs/architecture/adr/` | 20 | HISTORICAL ACCEPTED DECISION RECORDS | Never alter decision bodies for terminology; current target mapping is supplied by ADR recommendations and the convergence report. |
| `docs/architecture/architecture-convergence-program-sprint-{1,2,3}-*/` | 12 | CURRENT CONVERGENCE RECORDS | Use Matrix terms; older content is explicitly transitional where it records prior state. |
| `docs/architecture/architecture-convergence-program-sprint-4-terminology-finalization/` | 5 | CURRENT CONVERGENCE RECORDS | This Sprint's plan, classification register, report, matrix and ADR/open-issues record use Matrix terms. |
| `docs/architecture/implementation-convergence-program-phase-2-repository-alignment-assessment/` | 19 | HISTORICAL IMPLEMENTATION ASSESSMENT | Repository comparison evidence; it does not amend canonical architecture. |
| `docs/architecture/implementation-convergence-program-phase-2-5-architecture-decision-gate/` | 8 | HISTORICAL MIXED CONVERGENCE RECORD | Challenge/decision artifacts are Architecture Convergence; migration and Phase 3 planning artifacts are Implementation Convergence. |
| Other `docs/architecture/` assessments, pipeline and operational-engine reports | 52 | HISTORICAL / TRANSITIONAL ASSESSMENT | Preserve findings; record legacy terms as historical unless a document is listed above as active. |
| `docs/akb/` | 4 | TRANSITIONAL KNOWLEDGE RECORD | Retain current implementation vocabulary; Article I governs target Knowledge Object terminology. |
| `docs/contracts/`, `docs/schemas/`, `docs/integrations/`, `docs/operations/`, `docs/security/` | 11 | TRANSITIONAL IMPLEMENTATION CONTRACT | Preserve implemented contract names; apply target terms only in new explanatory text pending ADR-backed migration. |
| `docs/epics/`, `docs/roadmap/`, `docs/work-items/` | 20 | HISTORICAL / PLANNING RECORD | Preserve approved scope and historical vocabulary; no retroactive rename. |
| `docs/sprints/` | 68 | HISTORICAL EXECUTION SCOPE | Immutable sprint authorities and outcomes; do not revise terminology. |
| `docs/evidence/` | 620 | IMMUTABLE EVIDENCE | Preserve exact evidence, command output, baseline and result language. Never change to improve terminology. |
| `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md` | 1 | CANONICAL GOVERNANCE WORKFLOW | Technology-neutral; unchanged except through governance amendment. |
| `docs/confirmationproof.md` | 1 | HISTORICAL CONFIRMATION RECORD | Preserve its approval terminology and provenance. |

**Total at assessment:** 819 files. **Current working record count:** 865 files
(including subsequent approved target entries and convergence evidence). The
additional records are covered by their applicable architecture and
`docs/evidence/` family rules; the original assessment baseline remains
unchanged.

## Historical-marker policy

The first-party architecture snapshots that formerly advertised `CANONICAL`
status now carry an explicit `HISTORICAL` marker. Transitional constitutions
carry a front-matter status and a visible convergence note. For immutable
accepted ADRs, Sprint scopes and evidence, this register is the durable
family-level `HISTORICAL` marker: modifying each record would corrupt the
decision or evidence it preserves.

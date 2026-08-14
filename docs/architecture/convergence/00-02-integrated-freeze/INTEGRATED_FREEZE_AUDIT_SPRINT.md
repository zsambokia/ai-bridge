# Architecture Convergence 00–02 — Integrated Freeze Audit Sprint

## Status

**PROPOSED / PRODUCT OWNER AUTHORIZED FOR FDM EXECUTION**

This sprint defines the independent hard-gate audit required before freezing the currently reviewed pre-Mission architecture baseline.

Baseline at sprint creation: `4b44fa4614b509fc3b6a13d6bd8e6289a1d9671d` on `main`.

The audit MUST start read-only. It MUST NOT repair findings during the assessment phase.

## Objective

Establish whether Sections 00–02 form one coherent, source-traceable, Constitution-aligned, runtime-backed architecture baseline that is safe to freeze before continuing to Section 03 — Conversation State & Mission Resolution.

The intended freeze milestone is:

**00–02 INTEGRATED ARCHITECTURE BASELINE FREEZE**

It is NOT a standalone `02 FREEZE`.

## Scope

### Section 00 — Factory Chat / Interaction Boundary

Compatibility audit only. Do not reopen Section 00 as a full redesign or convergence program. Verify that later 01/02 decisions and implementations have not made the interaction boundary semantically inconsistent.

### Section 01 — Conversation

Full retrospective convergence audit. Reconstruct the accepted Section 01 architecture from primary evidence and determine, decision by decision, whether it is:

- STILL VALID
- REFINED BY 02
- SUPERSEDED BY 02
- CONFLICT
- MISSING IMPLEMENTATION
- OUT OF SCOPE / 03+

Do not redesign Conversation merely because a different design is now possible.

### Section 02 — Conversation Understanding

Full independent freeze audit of the completed convergence and implementation. Revalidate source decisions, Constitution, ADRs, diagrams, runtime, persistence, tests and evidence rather than trusting prior closure reports.

## Governing principles

1. Architecture first: primary Product Owner decisions and current governing Constitution determine intended semantics; existing code does not automatically define the target.
2. Later explicit Product Owner decisions may legitimately supersede earlier Section 01 decisions. Supersession MUST be evidenced, never inferred merely from newer code or documentation.
3. Constitution is the governing canonical baseline after convergence changes have been incorporated. Any unresolved contradiction with current Constitution is a freeze blocker.
4. The audit is source-first. Previous reconstruction/closure documents are audit targets and supporting evidence, not unquestionable truth.
5. **AI Kernel is NOT Cognitive Processing.** Any document, dependency, runtime implementation or diagram collapsing these concepts is a blocker.
6. Factory Chat is UI / interaction boundary, not Runtime.
7. Conversation remains an independent domain object and its domain authority must not be silently displaced by shared cognitive/protocol infrastructure.
8. Runtime starts only where the canonical architecture says runtime starts; pre-runtime/runtime boundaries must remain explicit.
9. Cognitive Processing capabilities that are defined as stateless MUST remain stateless. Domain transition authority remains with the owning domain component.
10. Factory Protocol / FactoryIP L0–L4, Nodes / published semantic services, FFS, Zoning, Evidence, Provenance, Artifact/Claim/Knowledge boundaries must be audited as shared platform foundations introduced/refined through 02.
11. Zoning is the canonical communication authorization mechanism; rejected duplicate Conversation-specific communication-contract models must not reappear.
12. Retrieval eligibility/firewall rules must execute before semantic retrieval and must not have bypass paths.
13. No speculative Section 03+ architecture may be invented to make 00–02 pass.

## Required audit phases

### Phase A — Immutable baseline capture

Record:

- exact local HEAD;
- exact `origin/main` SHA;
- clean/dirty worktree state;
- Constitution version/authority sources;
- applicable AGENTS.md instructions;
- relevant migrations and test baseline.

If the requested baseline is no longer current, document the delta before proceeding. Do not silently audit a different baseline.

### Phase B — Primary-source reconstruction of Section 01

Locate and reconstruct the primary Product Owner evidence that produced the Conversation architecture. Include source locators and chronology. Separate:

- accepted decisions;
- proposals;
- hypotheses;
- rejected ideas;
- open questions;
- later superseded decisions.

Produce a Section 01 Decision Ledger with reproducible source references.

### Phase C — 01 ↔ 02 supersession and consistency analysis

For every material Section 01 decision, compare it with the final accepted Section 02/platform decisions.

Required classification:

`STILL_VALID | REFINED_BY_02 | SUPERSEDED_BY_02 | CONFLICT | MISSING_IMPLEMENTATION | OUT_OF_SCOPE_03_PLUS`

Every `REFINED_BY_02` and `SUPERSEDED_BY_02` entry MUST cite both the earlier and later authority/evidence.

Any unexplained `CONFLICT` is a hard FAIL.

### Phase D — Section 00 compatibility check

Verify Factory Chat / Interaction Boundary remains compatible with the integrated 01–02 model. Specifically inspect message ingress/egress, Conversation creation/ownership, FactoryIP boundary use, protocol envelopes and the UI-versus-runtime boundary.

Do not redesign Section 00.

### Phase E — Constitution audit

Audit the current Constitution against the integrated target semantics.

Verify at minimum:

- domain ownership and authority;
- Conversation semantics;
- Cognitive Processing semantics;
- AI Kernel boundary;
- Factory Protocol L0–L4;
- FactoryIP;
- FFS;
- Node/service model;
- Zoning;
- Evidence and Provenance;
- Artifact / Claim / Knowledge Candidate / Knowledge Object boundaries;
- pre-runtime/runtime boundary.

No material architecture may exist only in evidence docs while contradicting or being absent from a Constitution location where canonical governance requires it.

### Phase F — Canonical documentation and Mermaid audit

Audit ADRs, canonical architecture docs and Mermaid diagrams against the integrated target. Check semantic meaning, ownership, arrows, boundaries, naming and supersession—not merely syntax.

### Phase G — Runtime implementation audit

Trace canonical architecture into implementation. Inspect actual call paths and negative paths.

At minimum verify:

- FactoryIP protocol abstraction and transport binding;
- L0 scope and retrieval firewall;
- L1 evidence/provenance;
- L2 artifact/candidate/resolution semantics;
- L3 outcomes/claims/evaluation responsibilities;
- L4 Factory Message envelope/delivery/payload separation;
- FFS resolution/routing behavior;
- Zoning enforcement and denial paths;
- Conversation semantic surface;
- stateless cognitive capability behavior;
- domain authority/state-transition boundaries;
- persistence and migrations where applicable.

Named classes/files are not proof. Demonstrate runtime behavior and dependency direction.

### Phase H — Test and release-gate audit

Run the repository's required release gates and full relevant test suite.

Audit all skips. No skip may hide a 00–02 acceptance obligation. Existing skips must be classified and justified.

Add no tests during the read-only audit phase.

### Phase I — Forward traceability

Prove:

`Primary PO evidence → accepted decision → Constitution/ADR → canonical diagram → runtime/persistence → test → evidence`

for every material 00–02 obligation.

### Phase J — Reverse audit

Start from runtime and canonical artifacts and trace backward:

`runtime/schema/test/documentation → Constitution/ADR → accepted Product Owner decision`

The purpose is to detect architecture invented by implementation/Codex without Product Owner authority.

Any material canonical semantic addition without valid authority is a hard FAIL unless it is purely technical implementation detail within already-authorized semantics.

### Phase K — Integrated freeze verdict

The only successful verdict is:

**100% PASS — READY FOR 00–02 INTEGRATED ARCHITECTURE BASELINE FREEZE**

Not acceptable as freeze-ready:

- PASS WITH DEVIATION
- PASS WITH MINOR LOSS
- PARTIAL
- CONDITIONAL PASS
- known unresolved material gaps

Any relevant failure means **NOT READY FOR FREEZE**.

## Mandatory audit outputs

Create a dedicated evidence directory for this execution and include at minimum:

1. `README.md`
2. `BASELINE_INTEGRITY_REPORT.md`
3. `SECTION_01_SOURCE_RECONSTRUCTION.md`
4. `SECTION_01_DECISION_LEDGER.md`
5. `SECTION_01_02_SUPERSESSION_MATRIX.md`
6. `SECTION_00_COMPATIBILITY_REPORT.md`
7. `INTEGRATED_TARGET_ARCHITECTURE.md`
8. `CONSTITUTION_CONSISTENCY_MATRIX.md`
9. `CANONICAL_DOCUMENTATION_AND_MERMAID_AUDIT.md`
10. `RUNTIME_IMPLEMENTATION_AUDIT.md`
11. `PERSISTENCE_AND_MIGRATION_AUDIT.md`
12. `TEST_AND_SKIP_AUDIT.md`
13. `FORWARD_TRACEABILITY_MATRIX.md`
14. `REVERSE_TRACEABILITY_AUDIT.md`
15. `FREEZE_BLOCKER_REGISTER.md`
16. `INDEPENDENT_FREEZE_VERDICT.md`

Evidence must be detailed enough for a second auditor to reproduce the conclusion.

## Hard gate and repair protocol

### Audit execution is read-only

During the initial audit:

- do not change Constitution;
- do not change ADRs;
- do not change architecture docs;
- do not change runtime;
- do not change schemas/migrations;
- do not change tests merely to make them pass.

Audit evidence files may be created only after the inspected baseline SHA has been immutably recorded; their creation must not be confused with repair of the audited baseline.

### If any blocker is found

1. Verdict = `NOT READY FOR FREEZE`.
2. Enumerate every known blocker before repair.
3. Perform repair only as a separate FDM repair execution.
4. Technical implementation decisions that are already inside approved architecture MUST NOT be escalated to the Product Owner merely for convenience.
5. Product Owner escalation is permitted only for a genuine unresolved business/architecture decision, conflicting PO authorities that cannot be resolved by chronology/supersession, or a requested scope/semantic change.
6. After repair, commit and push a new SHA.
7. Restart the relevant integrated freeze audit from the new immutable SHA. Do not reuse the old PASS result.

## Scope-control rule

The purpose is to freeze the architecture already decided for 00–02, not to design Section 03.

If an issue belongs to Conversation State & Mission Resolution or later sections and is not required to make an existing 00–02 invariant coherent, classify it `OUT_OF_SCOPE_03_PLUS` and preserve it for the next convergence section.

## Freeze meaning

A successful freeze establishes the integrated, audited baseline for the currently reviewed pre-Mission chain:

`Factory Chat / Interaction Boundary → Conversation → Conversation Understanding`

and the shared platform foundations already introduced and approved through those sections.

It does NOT claim that Section 03 or later architecture has been completed.

## Exit criteria

The sprint is complete only when:

- Section 01 primary decisions are reconstructed and classified against 02;
- Section 00 compatibility is proven;
- no unexplained 01↔02 conflict remains;
- current Constitution is semantically aligned;
- canonical docs and Mermaid diagrams are aligned;
- runtime/persistence implement every required current obligation;
- full release/test gates pass;
- no relevant skip masks an obligation;
- forward traceability is complete;
- reverse audit finds no unauthorized material architecture;
- AI Kernel ≠ Cognitive Processing is preserved everywhere;
- all freeze blockers are zero;
- final verdict is exactly `100% PASS — READY FOR 00–02 INTEGRATED ARCHITECTURE BASELINE FREEZE`.

Only after that verdict should the Product Owner decide the actual FREEZE and authorize progression to Section 03.
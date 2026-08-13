# Codex Handoff — Architecture Convergence 02 Closure

## Objective

Apply the Product Owner-approved section-02 target architecture to the AI Bridge canonical architecture documentation, after performing an exhaustive repository assessment. Produce a coherent, contradiction-free constitutional baseline and evidence-backed closure report.

The approved source package is this directory:

- `00_CLOSURE_README.md`
- `01_TARGET_ARCHITECTURE_DECISION_REGISTER.md`
- `02_CONSTITUTION_AMENDMENT_REQUIREMENTS.md`
- `03_CONSTITUTION_IMPACT_MATRIX.md`

Do **not** infer that these files themselves are the final Constitution. They are the approved amendment specification.

---

# Phase 1 — Assessment

Perform a repository-wide traversal of architecture, ADR, diagram, protocol, knowledge, runtime and governance documentation that may conflict with or depend on the approved section-02 target.

At minimum search for concepts and synonyms around:

- Conversation, Conversation State, CSE, maturity, progression, Mission Evaluation, Knowledge Recording;
- Context Builder/Assembly, Context Package, Persona, Cognitive Profile;
- Understanding, Evaluation, Result, Outcome, Projection;
- Evidence, provenance, causality, relation;
- Artifact, Artifact Contract, Artifact Version, payload, integrity;
- AKB, Knowledge Object, Knowledge Publication, Candidate, conflict;
- Claim, resolution, approval, decision request, input request;
- Factory Message, Factory Packet, FactoryIP, Node, service, FFS, zoning;
- MCP, adapter, ingress, transport, API, CRUD;
- Mission, MSM, Operational Foundation, AI Kernel, Execution, Capability, Provider, Provider Executor.

For every relevant finding classify it as:

1. **Target Architecture — already aligned**
2. **Target Architecture — conflicting/superseded**
3. **Current Implementation only**
4. **Historical/deprecated**
5. **Open ADR/question resolved by section 02**
6. **Potentially new conflict not covered by the approved package**

Provide concrete repository paths and quoted/line-level evidence where practical.

Do not modify files during the Assessment phase.

---

# Phase 2 — Architecture Challenge

Before implementation, critically test the approved target against the full repository.

Specifically challenge:

- whether any approved concept duplicates an existing canonical abstraction under another name;
- whether FactoryIP L0–L4 layer ownership has circular or overlapping responsibility;
- whether Cognitive Processing accidentally steals authority from Conversation, Mission Resolution, Knowledge, MSM or runtime domains;
- whether Artifact/Knowledge/Evidence separation creates contradictory identity or lifecycle ownership;
- whether FactoryIP Node boundaries expose internal implementation rather than semantic services;
- whether FFS or Zoning introduces unnecessary MVP complexity;
- whether AI Kernel remains strictly post-admission execution core;
- whether any proposed amendment contradicts an accepted constitutional invariant outside section 02.

If you find a materially better architecture or a true contradiction requiring a Product Owner decision, **STOP before implementing that disputed part** and produce a Business Decision Required report with alternatives and trade-offs.

Do not silently redesign the approved target.

---

# Phase 3 — Implementation Plan

If no blocking architecture challenge remains, produce a file-by-file amendment plan.

The plan must identify:

- files to update;
- new canonical documents, if genuinely necessary;
- documents/ADRs to supersede or deprecate;
- diagrams to regenerate;
- indexes/README/navigation references to update;
- terminology migrations;
- explicit removal of contradictory rules;
- any implementation gaps discovered but intentionally not changed in this documentation closure.

Prefer editing the authoritative canonical document over adding another overlapping document.

Do not preserve wrong architecture solely for backward compatibility. This project phase allows breaking documentation/architecture changes where required for coherence.

---

# Phase 4 — Implementation

After the plan is accepted under the repository's applicable governance rules, implement the canonical documentation amendments.

Mandatory invariants:

1. Factory Chat is UI/interaction boundary, not Runtime.
2. Conversation is first-class durable domain state.
3. Cognitive Processing is stateless and does not own domain consequences.
4. Context Package and processing results are immutable/versioned as specified.
5. Mission/MSM authority remains intact.
6. Runtime begins after Mission and Operational Foundation admission.
7. AI Kernel executes; it does not decide, and it is not the Cognitive Processing layer.
8. Engines are stateless Capability Providers and do not call each other directly.
9. Factory Protocol L0, L1, L2, L3 and L4 are individually defined.
10. FactoryIP is the complete L0–L4 semantic communication stack.
11. External adapters, including MCP, cannot bypass canonical FactoryIP/domain boundaries.
12. Evidence, Provenance Relation, Artifact and Knowledge remain distinct concepts with explicit cross-references rather than type conflation.
13. Artifact Version is immutable and historical references resolve to concrete versions.
14. Whole Artifacts do not automatically become AKB Knowledge.
15. Knowledge Candidate is pre-publication; publication consequence belongs to Knowledge authority.
16. Zoning is transport communication permission, not domain authorization, and final topology rules are not invented before topology is known.
17. FFS remains control-plane resolution; payload traffic does not proxy through it.
18. Conversation LAN services are semantic (`conversation.interaction`, `conversation.context`, `conversation.projection`), not CRUD/state mutation endpoints.

---

# Phase 5 — Verification

After implementation, perform a second exhaustive repository traversal.

Verify:

- no active canonical document still mandates the rejected numeric maturity/single-linear-progression model;
- no canonical document places Knowledge Publication or Mission Resolution incorrectly inside Conversation lifecycle;
- no canonical document places Cognitive Processing inside AI Kernel;
- no canonical document states that an Artifact simply becomes Knowledge;
- no canonical document conflates Evidence with Artifact or Provenance Relation;
- no canonical diagram contradicts the text;
- all new terms have one canonical definition and are linked from relevant indexes;
- open ADRs/questions resolved by section 02 are closed/superseded consistently;
- old terminology that remains is either compatible, explicitly historical, or explicitly deprecated;
- cross-document links resolve;
- repository documentation tests/linters pass if such checks exist.

Also inspect implementation only to produce a **Target Architecture / Current Implementation / Gap** report. Do not automatically refactor runtime code as part of this closure unless separately authorized.

---

# Required Closure Report

Return a closure report containing:

## A. Executive result
`PASS`, `PASS WITH NON-BLOCKING GAPS`, or `BLOCKED`.

## B. Constitutional amendments
Every changed canonical file and what changed.

## C. Contradictions removed
Old rule → new canonical rule → file evidence.

## D. Remaining open questions
Only genuinely unresolved architecture questions; do not reopen accepted decisions without evidence.

## E. Implementation gap register
For each gap:

- Target Architecture
- Current Implementation
- Gap
- impact/risk
- recommended future work

## F. Verification evidence
Searches/checks/tests performed and their results.

## G. Coverage statement
Explicitly state whether the full repository traversal found any remaining active canonical contradiction with the section-02 approved target.

---

# Product Owner intent

The Product Owner explicitly chose the following division of labor for this closure:

- the architecture-change specification is prepared in advance;
- **Codex owns the exhaustive repository traversal and verification**;
- implementation must be evidence-driven and must not treat current code as more authoritative than the approved target architecture.

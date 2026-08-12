# Codex Constitution Convergence Handoff

## Mission

Apply the Product Owner-approved Architecture Convergence constitutional delta to the AI Bridge repository, then prove completeness.

This handoff deliberately assigns repository traversal, exact current-section mapping, conflict discovery and final verification to Codex.

## Authoritative input set

Codex SHALL treat the following files as the change package:

1. `CONSTITUTION_IMPACT_MATRIX.md`
2. `CONSTITUTION_AMENDMENT_SPECIFICATION.md`
3. `CANONICAL_TERMINOLOGY_DELTA.md`
4. this handoff

These files describe the approved target. They are not implementation-convergence instructions.

## Non-negotiable Product Owner evidence

The Product Owner explicitly confirmed that Cognitive Profile, Factory Protocol L0-L4, FactoryIP, Artifact Contract, Claim and the related foundation terminology did not exist canonically before this convergence. Treat them as NEW CONSTITUTIONAL DELTA. Do not reject them merely because repository search on historical `main` returns no match.

## Required execution sequence

### Phase 1 — Repository traversal

Inspect all canonical architecture/governance sources, including at minimum:

- bridge/root constitution;
- architecture constitution and baseline;
- architecture map/index;
- AI Kernel constitution;
- Conversation / Mission / Operational Foundation architecture documents;
- Context, Capability, Provider, AKB/Knowledge documents;
- canonical diagrams;
- ADRs and architecture challenges;
- governance documents that define Architecture vs Implementation Convergence;
- contracts/schemas where they are declared canonical architecture inputs.

Do not assume this list is complete. Discover the actual canonical set.

### Phase 2 — Evidence binding

For every CIM item:

- identify exact affected file(s) and section(s);
- classify current state as `ABSENT`, `ALIGNED`, `PARTIAL`, `CONFLICTING`, `DUPLICATE`, or `LEGACY`;
- record exact evidence;
- identify diagrams/ADRs/contracts affected;
- identify legacy terminology requiring removal or explicit supersession.

Create a machine-reviewable `CONSTITUTION_IMPACT_EVIDENCE_REGISTER.md` with one row per CIM item. No CIM item may be silently omitted.

### Phase 3 — Amendment application

Apply the approved target semantics with the following rule:

> Amend the existing canonical owner when one exists; create a new canonical foundation document only when no current canonical owner can cleanly own the rule.

Avoid parallel constitutions describing the same responsibility.

When adding a new canonical document, update every canonical index/map/reference needed to make its authority unambiguous.

### Phase 4 — Diagram convergence

Update all canonical diagrams affected by the amendments. At minimum verify the end-to-end boundary:

`Factory Chat / Access Adapter -> Conversation -> Cognitive Processing / Conversation State -> Mission Resolution -> Mission -> MSM -> Operational Foundation -> immutable Execution Request -> AI Kernel -> Capability Resolution -> Provider / Provider Executor -> result/evidence/artifact -> return/projection`.

Also represent FactoryIP/Node/service boundaries where the diagram's abstraction level requires them. Do not force low-level FactoryIP detail into diagrams whose purpose is unrelated.

### Phase 5 — Completeness audit

Perform all of the following and produce evidence:

1. Decision -> Constitution coverage: every CIM item maps to canonical treatment.
2. Constitution -> Decision reverse coverage: every newly changed constitutional rule maps back to an approved CIM item or an explicitly necessary editorial consequence.
3. Repository-wide terminology audit for both new terms and legacy/conflicting synonyms.
4. Diagram audit: text and diagrams express the same responsibility boundaries.
5. Negative-invariant audit: SHALL NOT rules are represented where bypass would be dangerous.
6. L0-L4 completeness audit: each layer is independently defined; FactoryIP is not a reference to an undefined stack.
7. Cross-layer responsibility audit: Scope, Evidence, Provenance, Artifact, Transport, Cognitive Processing, Knowledge, Resolution and AI Kernel do not steal each other's authority.
8. Conversation/Cognitive Processing/Mission Resolution scope audit.
9. Duplicate canonical-definition audit.
10. Orphan/superseded-reference audit.
11. Link/index/reference integrity audit.
12. Mermaid/diagram syntax validation where tooling exists.

## Mandatory negative invariants to verify

Codex SHALL explicitly verify that the final canonical architecture does NOT imply any of the following:

- Factory Chat owns durable business state.
- UI lifecycle controls Mission or Execution lifecycle.
- Understanding mutates domain state.
- Evaluation is Domain Authority.
- Stateless processing resolves hidden scope/profile for itself.
- Evidence is automatically sufficient or authoritative.
- Evidence and provenance relation are the same object/meaning.
- Provenance history can be overwritten.
- Every relation must become a first-class heavy object.
- Producer can self-declare arbitrary canonical Artifact.
- Artifact Version content can be edited in place.
- Artifact automatically becomes Evidence or Knowledge.
- Cognitive Processing can publish directly to AKB.
- Knowledge conflict automatically overwrites active Knowledge.
- Claim is the only possible Resolution Subject.
- FactoryIP is CRUD/API access to internal state.
- Every internal service call requires FactoryIP.
- Every module becomes a FactoryIP Node.
- FFS proxies Factory Packet payload traffic.
- A second communication authority duplicates Zoning.
- External MCP/HTTP adapter bypasses FactoryIP/domain authority.
- Cognitive Processing is placed inside AI Kernel.
- AI Kernel makes business decisions.
- Provider owns provider-execution runtime state.
- Target architecture is derived from current implementation limitations.

## Change discipline

- Do not perform runtime/domain implementation changes in this task.
- Do not preserve backward compatibility with deprecated architecture wording merely for documentation compatibility; instead use explicit supersession/migration notes where historically useful.
- Do not reopen Product Owner-approved architecture merely because current code differs.
- If a genuine contradiction exists between two approved inputs, stop that specific amendment, record it as `PO_DECISION_REQUIRED`, and continue independent items.
- Do not silently invent missing architecture decisions.

## Required outputs

Codex SHALL produce:

- amended canonical constitutional/architecture documents;
- `CONSTITUTION_IMPACT_EVIDENCE_REGISTER.md`;
- `CONSTITUTION_CONVERGENCE_AUDIT_REPORT.md`;
- updated canonical diagrams/indexes/maps;
- a concise list of any `PO_DECISION_REQUIRED` items;
- a final statement whether Architecture Convergence constitutional closure is `PASS`, `PASS_WITH_DECISIONS_REQUIRED`, or `FAIL`.

## Acceptance rule

Closure is `PASS` only if every CIM item is accounted for, every changed canonical rule has traceability, no unresolved contradiction remains, diagrams and terminology are aligned, and the negative-invariant audit finds no canonical bypass.
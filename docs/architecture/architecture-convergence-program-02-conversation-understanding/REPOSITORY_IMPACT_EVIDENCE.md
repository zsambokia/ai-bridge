# Architecture Convergence 02 — Repository Impact Evidence

Status: WORKING / EVIDENCE-BACKED IMPACT MAP
Baseline: `main`
Target working branch: `architecture/02-conversation-understanding-convergence`

## Purpose

This document binds the accepted 02 convergence decisions to concrete current canonical repository sources. It complements `CONSTITUTION_IMPACT_MATRIX.md`: the matrix says *what* must change; this file identifies *where the current baseline says something that must be preserved, refined, superseded, moved, or reconciled*.

The Product Owner has explicitly confirmed that Cognitive Profile, Factory Protocol L0–L4, FactoryIP, Artifact Contract, Claim and related new terminology did not exist previously in canonical architecture. Their absence from `main` is therefore expected and is treated as a genuine ADD delta, not missing historical evidence.

## Canonical sources inspected

### Primary constitutional sources

1. `docs/architecture/ARCHITECTURE_CONSTITUTION.md` — transitional global architectural laws and Constitution Book hierarchy.
2. `docs/architecture/CONVERSATION_TO_MISSION_ARCHITECTURE_CONSTITUTION.md` — Article IV, version 1.1.0, approved target.
3. `docs/architecture/AI_KERNEL_ARCHITECTURE_CONSTITUTION.md` — Article III, version 1.0.0, approved target.
4. `docs/architecture/SCOPE_ARCHITECTURE_CONSTITUTION.md` — Article VI, version 1.0.0, approved target.
5. `docs/architecture/LOCALIZATION_ARCHITECTURE_CONSTITUTION.md` — Article VII, version 1.0.0, approved target.
6. `docs/architecture/AKB_KNOWLEDGE_OBJECT_AND_LIFECYCLE_CONSTITUTION.md` — Articles I–II, approved target.

### Primary canonical diagrams

7. `docs/architecture/diagrams/01-conversation-layer/01_CONVERSATION_LAYER.md` — CANONICAL, architecture version 1.1.0.
8. `docs/architecture/diagrams/99-full-architecture/99_FULL_ARCHITECTURE.md` — CANONICAL, architecture version 1.0.0.

### Additional affected architecture sources discovered by repository search

These require later detailed terminology/consistency review because they contain adjacent concepts or are registered architecture sources:

- `docs/architecture/MCP_EXECUTION_CONTEXT.md`
- `docs/architecture/ORKI_CONTEXT_PACKAGE_FLOW.md`
- `docs/architecture/ORKI_COGNITIVE_DATA_FLOW.md`
- `docs/architecture/KNOWLEDGE_PIPELINE.md`
- `docs/architecture/AKB_FOUNDATION.md`
- `docs/runtime/runtime_2_0_constitution.md`
- `docs/architecture/architecture-convergence-program-sprint-3-ai-kernel-architecture/TERMINOLOGY_CONVERGENCE_MATRIX.md`
- `docs/architecture/architecture-convergence-program-sprint-4-terminology-finalization/TERMINOLOGY_CONVERGENCE_REPORT.md`
- `docs/architecture/architecture-convergence-program-master-plan/ARCHITECTURE_CORPUS_AND_CONCEPT_REGISTER.md`

They are not automatically constitutional amendment targets; classification must follow the repository's architecture-document governance.

## Global Constitution impact

### `ARCHITECTURE_CONSTITUTION.md`

#### Existing laws to preserve

- One explicit owner per business domain; no cross-domain state writes.
- MSM remains sole Mission lifecycle authority.
- Engines must not directly call one another.
- Operational Foundation remains canonical mechanical handoff/delivery boundary.
- Provider output is never architecture/governance/Mission/PO authority.
- Evidence/provenance/correlation are mandatory architectural properties.
- Persona/projection must not create a second control path.
- Architecture and implementation convergence remain separate; implementation cannot silently redefine target architecture.

#### Existing laws requiring reconciliation

- Architectural Law 6 currently says domain state machines communicate through durable attributable `requests, results, events, and evidence`. This vocabulary must be reconciled with Factory Message Protocol and Result/Outcome/Projection without destroying the durable-boundary invariant.
- Architectural Law 8 mentions Evidence and provenance as generic properties. L1/L2 now define their common protocol semantics and must become the authoritative definitions.
- Architectural Law 11 currently says CSE exclusively owns Conversation Domain progression. This is 03 territory and must not be silently reaffirmed or changed in 02; mark it for 03 convergence review.
- The Constitution hierarchy currently has no Factory Protocol / FactoryIP constitutional entry. A new cross-cutting constitutional location is required before later domain sections depend on it.

#### Article V governance consequence

ADG-101 through ADG-106 make canonical diagrams normative and require every affected diagram to be updated before convergence closure. Therefore the 02 change cannot be considered closed after text-only Constitution changes.

## Article IV — Conversation to Mission impact

### §4.1 Purpose and boundary

Current chain:

```text
Human -> Factory Chat UI -> Conversation Domain -> Conversation Understanding
      -> Conversation State Engine -> Mission Resolution -> Mission -> MSM
      -> immutable Operational Work Item -> Operational Foundation -> AI Kernel
```

Required treatment:

- PRESERVE the human Conversation before Mission principle.
- PRESERVE Mission as first business object entering operational runtime.
- PRESERVE Kernel start only after Operational Foundation admission.
- REFINE Factory Chat and Conversation into FactoryIP Node/boundary semantics.
- REFINE the Conversation Understanding segment into Cognitive Processing semantics.
- MARK CSE/Mission Resolution detail for 03 review.
- ADD Factory Protocol/FactoryIP communication boundaries without prematurely adding unreviewed future Nodes.

### §4.2 Factory Chat UI

Current canonical facts:

- localized presentation/interaction adapter;
- may display messages, attachments, streaming, approvals, status, projections;
- cannot own business state, create Mission, start Workflow, invoke Engine/Provider or bypass domain boundary;
- can request Conversation action and display attributable result;
- never second control path/state-machine writer.

Required treatment:

- PRESERVE all authority exclusions.
- REFINE `Factory Chat UI` into the accepted FactoryIP addressable interaction Node/boundary while retaining UI-not-Runtime semantics.
- ADD explicit inbound/outbound Factory Message service interaction through published FactoryIP semantics rather than generic direct domain calls.

### §4.3 Conversation Domain

Current canonical facts:

- owns durable human interaction record, ordered history, participants/Persona refs and Conversation metadata/state;
- is not Kernel and owns no Mission/Execution/Provider/OF state;
- transcript is not durable organizational knowledge.

Required treatment:

- PRESERVE ownership and transcript/knowledge separation.
- ADD Conversation as FactoryIP Node.
- ADD published semantic service families `conversation.interaction`, `conversation.context`, `conversation.projection`.
- ADD no CRUD/no direct external state-transition/no internal reach-through negative invariant.
- RECONCILE any existing generic `Conversation action` wording with the semantic service model.

### §4.4 Conversation Understanding

Current canonical wording bundles:

- intent/goal detection;
- context building;
- Conversation/prior-Mission search;
- AKB/Repository/semantic retrieval;
- evidence-aware LLM analysis;
- stateless service capability;
- adaptive selection under `Context Profile`;
- source absence/authorization/unavailability recorded in provenance/Evidence;
- LLM not lifecycle owner/authority.

Required treatment:

- PRESERVE statelessness and LLM non-authority.
- SUPERSEDE `Context Profile` with Cognitive Profile.
- REFINE one bundled service into explicit Context → Understanding → Evaluation separation.
- ADD Processing Purpose ≠ User Intent.
- ADD immutable structured Understanding Result and Evaluation Result.
- MOVE concrete Conversation-state consequence to the responsible domain authority/03.
- RECONCILE source absence handling with L0 eligibility, L1 Evidence and L2 provenance.
- RECONCILE direct AKB/Repository retrieval wording with future Context Assembly ownership; do not prematurely assign the final Context Assembly Node in 02.

### §4.5 Conversation State Engine

Current canonical text defines CSE, three state axes and transition rules.

Required treatment:

- DO NOT re-approve or redesign these details in 02.
- MARK the whole detailed CSE/state model as 03 convergence input.
- PRESERVE only cross-cutting no-cross-domain-write and outside-Kernel/OF boundaries as already accepted general invariants.

### §4.6 Mission Resolution

Current canonical text makes Mission Resolution exclusive Conversation→Mission intake authority.

Required treatment:

- DO NOT redesign in 02.
- MARK for 03 convergence review.
- RECONCILE later with the accepted L4 principle that `Resolution` is a general interaction pattern and not synonymous with the whole Factory Message Protocol. This does not by itself invalidate the domain concept `Mission Resolution`; the naming/semantic relationship must be reviewed in 03.

### §4.7 Mission/MSM operational handoff

Required treatment:

- PRESERVE Mission/MSM/OF authority boundaries as baseline constraints.
- Do not redesign Mission/MSM in 02.
- Future 04/05 work must consume the now-canonicalized Factory Protocol foundation rather than inventing a separate communication substrate.

### §4.8 Context, knowledge, proactivity

Current canonical text uses Context Profile and says Conversation Understanding may compose a Context Package; Runtime consumes authorized Context Package; knowledge publication is separate.

Required treatment:

- SUPERSEDE Context Profile with Cognitive Profile.
- PRESERVE immutable/versioned/reproducible/evidence/provenance Context Package properties.
- PRESERVE transcript/temp context ≠ Knowledge.
- REFINE Context Assembly ownership: current Article assigns composition to Conversation Understanding, while 02 leaves final Context Assembly owner open and treats Context construction as a distinct concern.
- PRESERVE Persona non-authority/proactivity boundary.

### §4.9 Evidence and auditability

Required treatment:

- PRESERVE mandatory evidence for significant transitions/decisions/handoffs.
- REFINE Evidence semantics to L1.
- ADD L2 provenance/causality relation semantics.
- Ensure Evidence existence is not treated as automatic sufficiency/authority.

### §4.10 Invariants

Impact by invariant:

- IV-1 UI no Mission/runtime direct: PRESERVE.
- IV-2 Conversation no Engine/Provider/Kernel direct: PRESERVE and generalize under FactoryIP Node/no-reach-through.
- IV-3 CSE progression/state writing: 03 REVIEW.
- IV-4 Mission Resolution exclusive human Conversation Mission creation origin: 03 REVIEW.
- IV-5 MSM sole lifecycle: PRESERVE.
- IV-6 immutable MSM-authorized operational work/OF: PRESERVE for later sections.
- IV-7 Kernel after OF: PRESERVE.
- IV-8 execution participants not authorities: PRESERVE.
- IV-9 Context Profile + Package: SUPERSEDE Profile portion; PRESERVE Package immutability/provenance properties.
- IV-10 transcript/temp/runtime data not AKB Knowledge: PRESERVE and strengthen with Artifact→Knowledge publication rules.
- IV-11 PO only genuine business decisions: PRESERVE; Claim/Resolution authority model may later provide standardized cross-domain delivery.
- IV-12 boundary/state auditability: PRESERVE and ground in L1/L2/L4.

### §4.11 target diagram

The embedded diagram is directly impacted by Cognitive Profile, Cognitive Processing separation, FactoryIP Node/service boundaries and the 02/03 split. It must be updated together with Diagram 01.

## Article III — AI Kernel impact

### Existing baseline strongly consistent with 02

Article III already states:

- AI Kernel is operational execution core;
- begins after OF admission;
- Kernel executes, does not decide;
- does not build business Context;
- Context Builder is not a Kernel Manager/Registry/Object;
- Kernel binds/delivers immutable Context Package;
- Provider output/execution has no business authority.

These are PRESERVE/REINFORCE, not new corrections to Article III itself.

### Required reconciliation

- §3.1 references Article IV's Conversation Understanding/CSE/Mission Resolution chain; update only after 02/03 convergence establishes final names/boundaries.
- §3.2 and §3.15 use generic Evidence; reconcile with L1 without making Evidence Infrastructure a business authority.
- §3.3 calls Evidence a Kernel Object. The new L1 cross-cutting Evidence Protocol requires careful terminology reconciliation: a Kernel-scoped Evidence record may remain a first-class technical object, but the Constitution must not imply that Evidence as a platform protocol is owned exclusively by Kernel.
- §3.3 says the uniform pattern applies to `Knowledge`; Articles I–II already place KLM outside Kernel. This wording should be checked during final cross-article audit so the pattern does not imply Kernel ownership of Knowledge.
- §3.16 Scope/security already matches Organization/Workspace/Project and Repository-as-Resource; L0 should reference/consume Article VI rather than duplicate it.

## Article VI — Scope impact

Article VI already canonicalizes:

```text
Organization → Workspace → Project
```

and Repository as Resource, never Scope.

Required treatment:

- L0 MUST build on Article VI rather than create a competing Scope hierarchy.
- L0 adds **Effective Operational Scope & Isolation**: resolution/binding of scope, resource, policy and profile for a handoff/processing context.
- L0 adds ordering: eligibility/isolation before semantic retrieval/ranking.
- L0 Application Default Rules must be modeled as rules above resolution, not a new Scope.
- Article VI says detailed inheritance remains open; L0 must not accidentally decide those inheritance rules.

Potential terminology issue: `Effective Operational Scope` must be clearly distinguished from the canonical `Scope` object hierarchy so it is not interpreted as a fourth Scope type.

## Article VII — Localization impact

Article VII already establishes English canonical identifiers and multilingual semantic/user-facing content; Evidence preserves source language and translations are derived.

Required treatment:

- L0 language context should REFINE/COMPLEMENT Article VII, not create a second localization architecture.
- Interaction language, artifact language, code/canonical language and source language can be explicit processing context dimensions while Article VII remains authority for localization semantics.
- L1 Evidence must preserve Article VII source-language integrity.

## Articles I–II — AKB impact

### Existing baseline to preserve

- AKB stores Knowledge Objects, not documents as primary unit.
- Published Knowledge versions are immutable/versioned.
- Operational data is not Knowledge merely because useful.
- Knowledge References are consumed by Context Packages.
- KLM is outside AI Kernel.
- Direct bypass of KLM publication is forbidden.
- Vector/document/graph storage is implementation, not knowledge ownership.

### Required reconciliation with L3

- L3 strengthens the source boundary: a complete Artifact Version does not automatically become Knowledge.
- Knowledge Publication should derive semantically independent Knowledge Candidates/Objects from Artifact content with provenance back to the immutable Artifact Version.
- `Knowledge Candidate` terminology must be reconciled with the existing statement that the current governed candidate/review/active lifecycle remains authoritative until migration. Do not silently replace current implementation lifecycle with the new target concept.
- Existing AKB-102 currently lists `Evidence` as a permitted Knowledge Object specialized type. This needs explicit semantic review against the new rule `Artifact ↔ Evidence ↔ Knowledge are distinct`. An Evidence record may be published *as knowledge about evidence* only through KLM, but Evidence must not automatically be Knowledge by type identity. This is a high-risk ambiguity.
- AKB-104 says relationships are first-class typed/version-aware/evidenced. L2 now defines platform provenance/causality relations. The final model must decide how AKB semantic relationships relate to L2 provenance relations without creating two competing relation graphs.
- AKB lifecycle `DRAFT → REVIEW → APPROVED → DEPRECATED → ARCHIVED` is Knowledge lifecycle and MUST NOT be conflated with L2 relation lifecycle or Artifact governance lifecycle.

## Diagram 01 — Conversation Layer impact

Current canonical diagram contains:

```text
Product Owner → Factory Chat → Conversation
Conversation → Stateless Conversation Understanding
Conversation → Durable Conversation State
Understanding → Stateless CSE
CSE → Mission Resolution
Understanding → Context Profile → Immutable Context Package
Understanding → AKB / Repository retrieval
Context Package → AI Kernel
```

Required changes:

1. Factory Chat and Conversation need FactoryIP Node/boundary representation.
2. Cross-Node edges need semantic service/message meaning, not generic arrows where the boundary matters.
3. Context Profile must become Cognitive Profile.
4. Cognitive Processing separation must show Context / Understanding / Evaluation without prematurely redesigning 03 CSE/Mission Resolution.
5. `conversation.interaction`, `conversation.context`, `conversation.projection` must be representable at the Conversation Node boundary.
6. No CRUD/state reach-through path may appear.
7. L0–L4/FactoryIP should be shown at an appropriate abstraction level without turning a domain diagram into a network implementation diagram.
8. Current direct `Understanding → AKB/Repository` retrieval edge requires review because Context Assembly ownership is open.
9. Current direct `Context Package → AI Kernel` edge is cross-section architecture and must remain consistent with Article III, but the 02 final diagram should avoid claiming unreviewed intermediate Nodes.
10. CSE/Mission Resolution detail should be clearly marked as existing 03 baseline/input rather than newly closed 02 design if retained in the visual.

## Diagram 99 — Full Architecture impact

This is the highest-risk canonical diagram because it spans many future sections.

Direct impacts:

- Factory Chat/Conversation must eventually be represented through FactoryIP Node/service semantics.
- `Conversation Understanding → Context Builder` must be reconciled with Cognitive Processing and the open Context Assembly owner.
- Result/Outcome/Projection return path is not represented and will need future integration.
- Factory Protocol L0–L4 and FFS are absent.
- External adapters currently connect directly to Mission. Do not rewrite this in 02 without reviewing their future domains/intake path; record as later convergence impact.
- Operational Foundation, Engines, Kernel and Provider topology belong to later reviewed sections and should not be opportunistically reworked here.

Important governance consequence: because Diagram 99 is CANONICAL and Article V requires consistency, 02 closure must either update the portions whose semantics are already changed or explicitly bound/defer sections that depend on later convergence. It cannot simply be ignored.

## MCP / external adapter impact

Repository search identifies `MCP_EXECUTION_CONTEXT.md` and multiple MCP/runtime materials. The accepted 02 rule is architectural:

> MCP/HTTP/WebSocket are access/integration protocols and cannot bypass a FactoryIP Node's canonical boundary.

Detailed MCP implementation is not redesigned in 02. The final terminology audit must search for any architecture statement or diagram that presents MCP as a parallel internal authority path or direct canonical-state mutation path.

## Newly identified high-risk cross-article conflicts

### RISK-01 — Evidence as Knowledge Object type

Article I permits `Evidence` as a specialized Knowledge Object type, while L1/L3 separate Evidence, Artifact and Knowledge. This must be clarified explicitly; otherwise an Evidence record could accidentally become Knowledge by classification alone.

### RISK-02 — AKB relationship graph vs L2 provenance graph

Article I makes Knowledge relationships first-class; L2 introduces platform provenance/causality relations. The two graphs need a clear semantic boundary/reuse rule to avoid competing historical relation truth.

### RISK-03 — Context Builder ownership

Article IV currently places context building inside Conversation Understanding and Diagram 99 has a concrete Context Builder. 02 explicitly separates Context from Understanding and leaves final Context Assembly ownership open. This is a real convergence delta, not merely terminology.

### RISK-04 — CSE already constitutional but belongs to 03 course review

Article IV contains detailed CSE state axes/lifecycle/readiness decisions. They remain current approved target baseline but must be re-opened as input to 03 rather than silently treated as newly accepted by 02.

### RISK-05 — Mission Resolution name vs generic Resolution interaction

The accepted Factory Message Protocol uses Resolution as one general interaction pattern. Existing `Mission Resolution` is a domain concept. They may coexist, but their relationship must be explicitly disambiguated in 03 to avoid naming collision.

### RISK-06 — Kernel Evidence ownership language

Article III lists Evidence among Kernel Objects, while L1 makes Evidence a cross-cutting protocol. Kernel-specific Evidence records can remain Kernel-owned technical objects, but platform Evidence semantics cannot be Kernel-exclusive.

### RISK-07 — Full Architecture diagram over-claims future topology

Diagram 99 already depicts many domains/components not yet re-reviewed in the new section-by-section Factory LAN method. 02 must not use that diagram as authority to prematurely declare every depicted box a FactoryIP Node.

## Repository evidence status by change group

| Change group | Current canonical evidence found | Treatment |
|---|---|---|
| Cognitive Processing/Profile | Article IV has Conversation Understanding + Context Profile | REFINE / SUPERSEDE |
| L0 Scope & Isolation | Article VI has canonical Scope hierarchy; no L0 layer | PRESERVE Scope + ADD L0 |
| L1 Evidence | Evidence is pervasive in Articles III/IV/I–II/global laws; no L1 layer | GENERALIZE / RECONCILE |
| L2 Provenance/Causality | Provenance appears broadly; no common L2 relation protocol | ADD / RECONCILE |
| L3 Artifact | Artifact terminology exists in architecture/knowledge contexts; no common Artifact Contract/layer | ADD / RECONCILE |
| Result/Outcome/Projection | Generic result/event wording exists; accepted three-way semantics absent | ADD / TERMINOLOGY MIGRATION |
| Claim | No prior canonical concept per PO confirmation | ADD |
| L4 Factory Message Protocol | No prior canonical layer per PO confirmation | ADD |
| FactoryIP | No prior canonical concept per PO confirmation | ADD |
| FactoryIP Node/services | Existing domain/UI boundaries but no FactoryIP Node model | ADD / REFINE |
| FFS | No prior canonical concept per PO confirmation | ADD |
| Zoning | No prior canonical FactoryIP zoning | ADD direction; detail DEFER |
| AI Kernel boundary | Article III already strongly matches accepted correction | PRESERVE / REINFORCE; reconcile references |
| 02/03 split | Article IV combines Understanding, CSE, Mission Resolution | MOVE / staged reconvergence |

## Next mandatory audit actions

1. Repository-wide terminology search for every accepted new and superseded term.
2. Inspect all architecture corpus/register entries that classify the affected documents.
3. Inspect MCP/context/knowledge architecture docs for contradictory target statements.
4. Build a `DECISION_TRACEABILITY_MATRIX.md`: every accepted decision ID → Change Register ID → CIM ID → repository source → target constitutional treatment.
5. Build a diagram impact register covering all canonical Mermaid sources, not only Diagram 01/99.
6. Update `CONSTITUTION_AMENDMENT.md` only after the traceability matrix exposes any remaining gaps.
7. Final reverse audit: every proposed constitutional sentence must trace back to an accepted PO decision or preserved existing invariant.

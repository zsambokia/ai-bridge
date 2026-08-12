# Architecture Convergence 02 — Product Owner Decision Register

Status: WORKING

This register separates accepted decisions from proposals, hypotheses, open questions, current implementation facts and future target work.

| Area | Decision | Status | Closure treatment |
|---|---|---|---|
| Conversation Understanding | Understanding does not own business decision authority | ACCEPTED | 02 canonical candidate |
| Cognitive Processing | Generalizable stateless processing model | ACCEPTED | 02 canonical candidate |
| Cognitive separation | Context → Understanding → Evaluation are distinct concerns | ACCEPTED | 02 canonical candidate |
| Result semantics | Result ≠ Outcome ≠ Projection | ACCEPTED | Cross-cutting canonical candidate |
| Artifact | First-class, immutable, versioned | ACCEPTED | Protocol foundation |
| Artifact lifecycle | Materialization/payload/integrity/composition/applicability/retention are explicit concerns | ACCEPTED | Protocol foundation |
| Evidence | Evidence is not an Artifact-handling exception | ACCEPTED | Protocol foundation |
| Knowledge | Full Artifact does not automatically become AKB knowledge | ACCEPTED | Knowledge foundation |
| Claim | May be first-class and carry responsibility/decision authority semantics | ACCEPTED | Cross-cutting candidate |
| Claim / L3 | Claim is not an L3 resolution mechanism | ACCEPTED | Boundary correction |
| L4 | L4 = Factory Message Protocol | ACCEPTED | Protocol foundation |
| L4 interaction | Resolution is one L4 interaction among multiple possible interactions | ACCEPTED | Protocol foundation |
| Factory Message | Common envelope + interaction/transport semantics + specific payload | ACCEPTED | Protocol foundation |
| Message boundary | Factory Message is used at genuine domain/protocol boundaries | ACCEPTED | Protocol foundation |
| FactoryIP | Semantic inter-domain communication; not CRUD/API | ACCEPTED | Foundation |
| FactoryIP Node | Stable service boundary hides internal implementation/state mechanics | ACCEPTED | Foundation |
| External adapters | MCP/HTTP/etc. cannot bypass FactoryIP canonical domain boundary | ACCEPTED | Foundation invariant |
| Zoning | Design after Node + service topology is sufficiently known | ACCEPTED | Deferred foundation work |
| Conversation services | interaction/context/projection service families | ACCEPTED | Conversation Node candidate |
| Conversation CRUD | CRUD/state mutation service families are not canonical FactoryIP services | ACCEPTED | Negative invariant |
| conversation.context consumer | Concrete consumer not yet frozen | OPEN | Resolve with Context Assembly |
| AI Kernel | Operational execution core, not Cognitive Processing | ACCEPTED | Constitution correction/convergence |
| Kernel authority | Kernel executes; it does not decide | ACCEPTED | Constitution invariant |
| Context Builder | Higher-level Context/Knowledge boundary, not Kernel internal state | ACCEPTED | Constitution invariant |
| L0–L2 exact wording | Must be recovered from approved evidence, not memory | OPEN / REQUIRED | Closure blocker |
| FFS exact canonical model | Must be fully written during foundation convergence | OPEN / REQUIRED | Closure blocker |

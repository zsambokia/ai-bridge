---
status: COMPLETE
execution_profile: FACTORY_DEVELOPMENT_MODE
task_type: DOCUMENTATION
architecture_status: CANONICAL
---

# Diagram Impact Assessment

## Change assessed

Architecture Documentation & Visual Constitution Program: adoption of the
approved source hierarchy and completion of the initial canonical logical
diagram set.

## Affected diagrams

| Diagram | Change | Result |
| --- | --- | --- |
| 01 Conversation Layer | Mermaid source added; conversation-to-context-to-mission boundary clarified | Updated |
| 02-12 focused diagrams | Mermaid source and governance metadata added; Draw.io classified as derived | Updated |
| 99 Full Architecture | Canonical cross-layer Mermaid model added; derived visual aligned | Updated |

## Required canonical representations

- Mermaid embedded in version-controlled Markdown is the sole canonical logical
  source for every diagram in the set.
- Draw.io is an editable derived visual representation. PNG, SVG, and PDF are
  also derived artifacts and do not require regeneration for every change.
- The target execution object is `Execution`, owned by the AI Kernel.
- `ExecutionRun`, `ExecutionJob`, and `Provider Gateway` are not canonical
  architecture objects. Diagram 99 retains them only as a dashed Historical /
  Transitional implementation note pending their ADR decisions.
- The provider route is `Execution -> Provider Integration -> Provider
  Resolver -> Provider -> Provider Executor`.
- Context Builder produces the Context Package from Repository, AKB, and the
  Semantic Layer before Mission Resolution. Runtime receives the completed
  Context Package rather than querying those sources directly.
- Capability Registry and Engine Definition Registry are distinct objects;
  engines request Kernel-owned execution and never own an Execution.
- Every canonical Mermaid source declares the required Diagram Governance
  metadata, including status, source, derived visual path, Constitution
  reference, review date, architecture version, and related ADRs.

## Obsolete diagrams

None. Existing visual files remain useful as derived representations and
historical documentation is preserved rather than silently rewritten.

## Open Architecture Challenges

No new challenge was discovered. The detailed fate of `ExecutionRun` and
`ExecutionJob` remains ADR-gated and is intentionally not resolved by this
documentation sprint.

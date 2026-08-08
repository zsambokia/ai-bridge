# Runtime Cleanup & Legacy Removal Report

## Scope and result

Baseline: `main` at `4831371c1903d3f5a652f44912cbb8ca1711fdea`.
The active `projects.runtime_knowledge_compat` adapter was removed. Its three
call sites in `projects/orki_runtime.py` (factory-plan delivery, shadow
acceptance execution, and factory chat completion) now end after reflection.
Thus no active Runtime path constructs a `KnowledgeEntry`, generates an
embedding, or writes a vector.

The factory acceptance regression now proves that a completed shadow execution
has reflection and evidence but no AKB entry. The canonical structured Runtime
already emits `RuntimeKnowledgeCandidate.v1`, which is consumed only by the
independent Knowledge Pipeline.

## Deliberately retained

`OrkiKnowledgeIntegration`, its historical migration and read projections are
retained as immutable historical audit compatibility. Removing them would
require a data-retention decision and a destructive data migration. The
`KNOWLEDGE_INTEGRATING` state is also retained for replaying historic state
histories; no active code transitions into it.

## Search results and remaining debt

* `projects/knowledge.py::build_and_record_context_package` remains a
  deterministic, persisted context package used by legacy MCP/orchestration
  callers.
* `projects/semantic/intelligence.py::SemanticContextBuilder` and
  `projects/knowledge_pipeline.py::retrieve_context` are the semantic paths.

These overlap by design during migration but should not be merged in cleanup:
the deterministic package is a public legacy contract with multiple consumers.
A separately approved Context API migration should move consumers to a single
semantic package and then retire it.

## Validation evidence

Focused Runtime and factory acceptance tests: `4 passed` after removal.
Repository-wide Release Gate is recorded in `RELEASE_GATE.md` from the final
state.

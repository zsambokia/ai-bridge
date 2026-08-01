# Issue #17 — Sprint 5: Memory Mode and governed knowledge flow

## Authority and boundary

- Authority: Product Owner Factory Development Mode for Issue #17, under the accepted Sprint 1 interaction contract.
- Branch and baseline before mutation: `main` at `b99e36dad10418d0a8a55c0be3f9df3e1c93c7de`.
- Scope: server-rendered Memory search, AKB lifecycle projection, diagnostics, and audit projection only.

## Delivered behaviour

- Memory queries create an idempotent, attributable AKB context package for `factory-chat:memory`; the browser calls no provider.
- The view displays bounded package sources, query results, source provenance/version, package hash, stale-source and conflict diagnostics.
- It projects the registered repository, latest roadmap item, and canonical runtime status without inventing a second runtime.
- Candidate, review, activation, and rejection reuse `review_candidate`. Activation requires the existing project-bound approval reference; revisions remain append-only.
- The UI route resolves the active project before calling the service; the service independently rejects a foreign entry.

## Explicit exclusions

This Sprint introduces neither a direct LLM/provider call, vector store, semantic-retrieval claim, browser-owned authority, nor a parallel knowledge approval mechanism.

## Acceptance and validation

Targeted integration tests cover package provenance, the three lifecycle stages, required activation approval, rejection, cross-project denial, and stale/conflict diagnostics. Full Release Gate results and independent review are in `docs/evidence/issue-017-sprint-5-memory-mode-governed-knowledge-flow/`.

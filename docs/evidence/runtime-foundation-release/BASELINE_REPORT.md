# Runtime Foundation Baseline Report

## Canonical baseline

The annotated tag `runtime-foundation-v1` identifies the release evidence
commit on `main`. It is the reproducible reference for the first accepted Orki
Runtime implementation.

The architectural baseline is documented in
[`docs/architecture/ARCHITECTURE_BASELINE.md`](../../architecture/ARCHITECTURE_BASELINE.md).

## Accepted boundaries

1. Every Runtime execution belongs to a Goal and selected Plan.
2. Factory Chat enters the canonical Orki Runtime path.
3. OESM coordinates lifecycle; it does not replace reasoning.
4. Cognitive State answers what is known; Runtime answers what is being done.
5. Reflection precedes any candidate Knowledge Integration.
6. Provider adapters transport; they do not orchestrate.
7. Runtime events are the UI's lifecycle projection source.
8. Governance and `ExecutionRun` retain their ownership.

## Repository hygiene

The release cleanup preserves Product Owner-retained branches and the existing
stash. Completed merged branches and their clean worktrees are removed only
after `main` and its tag have been pushed. Historical, untracked audit material
is treated as an explicit archive decision rather than silently committed or
deleted.

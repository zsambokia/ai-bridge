# Pre-Audit Stabilization Gate Proposal

**Status:** Proposed governance control; not yet a repository-wide policy.

## Purpose

An architecture or operational acceptance audit must examine one official,
reproducible project state. It must not assess a developer worktree, an
unmerged branch, or a mixture of concurrent changes.

The gate therefore establishes a frozen baseline before every material
architecture audit or Product Owner acceptance.

## Required lifecycle

```text
Development
  -> Integration
  -> Baseline Frozen
  -> Architecture Audit
  -> Operational Acceptance
  -> Release Candidate
  -> Production Ready
```

The integration transition is:

```text
Development worktree
  -> Product Owner review
  -> approved merge to main
  -> clean main
  -> immutable baseline tag
  -> audit
```

## Gate criteria

The gate passes only when all of the following are evidenced:

1. Every active worktree, branch, local modification, untracked path, and
   stash is inventoried and explicitly classified as accepted, rejected, or
   unrelated user work.
2. All accepted changes have passed their resolved build, migration, test,
   smoke, conflict, and temporary-workaround/TODO checks on the reviewed
   integration result.
3. `main` contains all and only the approved changes. It is the canonical
   branch and has no detached HEAD, active merge, active rebase, or required
   uncommitted/stashed system state.
4. The worktree inventory contains only the canonical `main` worktree, unless
   a separately documented exception is approved for retained worktrees that
   are demonstrably outside the audit scope.
5. A fresh clean checkout of `main` successfully completes bootstrap,
   migrations, seed, build, and smoke verification.
6. An explicitly authorized immutable tag (for this programme,
   `runtime-2.0-baseline`) is created at the verified `main` commit.
7. The audit records the tag name and commit SHA and examines only that state.

## Evidence required

```text
git status --short
# no output

git status
# nothing to commit, working tree clean

git worktree list
# only the canonical main worktree

git rev-parse main
git rev-parse runtime-2.0-baseline
# identical SHA
```

The completed gate must also retain the worktree inventory, merge decisions,
validation receipts, and clean-checkout results.

## Failure rule

If any criterion is unmet, the state remains **Integration**, no baseline tag
is created, and no result may be labelled an official Architecture Audit or
Operational Acceptance. Diagnostic work may continue, but it must state that
it assessed a non-canonical development state.

## Application to the current Runtime 2.0 audit

The current inventory fails this gate: `main` is dirty, two additional
worktrees exist, and two stashes have unresolved relevance. Consequently, the
existing Runtime 2.0 reports are diagnostic development-worktree evidence,
not an acceptance baseline.

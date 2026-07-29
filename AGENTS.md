# Codex Instructions

This repository is developed through small, isolated, evidence-driven sprints.
Project-specific identity, paths, technology, Release Gates, and evidence
locations are resolved only from the validated Execution Contract and canonical
Project definition; they must not be hard-coded here.

## Mandatory context and contract policy

Before mutation, Codex must read, in order, the Constitution, workflow, exact
approved Sprint, and every additional context file named by the issued
Execution Contract. It must verify the contract hash, Project, repository,
branch, baseline, execution level, task type, resolved policy, Release Gates,
and deterministic evidence paths. It must not infer any of these from chat,
branch names, repository history, or roadmap order.

Execution levels are `HOTFIX`, `BUGFIX`, `TASK`, `SPRINT`, and `EPIC`.
Supported task types are `FEATURE`, `BUGFIX`, `MIGRATION`, `RECOVERY`,
`DOCUMENTATION`, `RELEASE`, `SELF_DEVELOPMENT`, `ONBOARDING`, `SECURITY`, and
`CONFIGURATION`. A contract policy is deterministic from Project configuration,
level, task type, scope, and declared risk modifiers. Risks may strengthen
assessment, review, evidence, documentation, or Release Gate obligations; they
may never weaken them. Omitted required gates need explicit, durable policy
justification. An `EPIC` is a planning/decomposition boundary, not code-change
authority: its child contracts carry implementation authority.

Only the exact approved Sprint defines implementation scope. A roadmap gives
direction but never authorization. Reuse or repair canonical components before
introducing new ones. Ordinary configuration, dependency, test, lint, type,
migration, evidence, and documentation failures follow `DETECT -> DIAGNOSE ->
REPAIR -> RERUN`; they do not require a Product Owner decision.

For a reviewed, confirmation-eligible scope, use `conversation.confirm` as the
high-level conversational Product Owner entry point. It derives the caller
binding, confirmation reference, and deterministic retry key. Do not route an
affirmative message to `scope.approve`: that lower-level operation binds an
already-existing durable approval reference. `scope.confirm_and_execute` is
only for an explicit structured submission that includes the exact reviewed
proposal version and hash.

`AUDIT` is a work type, not an executable hierarchy level. `SPRINT` and
`WORK_ITEM` remain the only executable scope kinds; an Audit uses the same
proposal, confirmation, contract, execution, and evidence lifecycle.

## Factory Development Mode for AI Bridge self-development

AI Bridge must remain repairable and developable even when its own managed
execution path is unavailable, unstable, incomplete, or is itself the subject
of the change. For tasks that modify the `zsambokia/ai-bridge` repository, the
Product Owner may explicitly authorize **Factory Development Mode**.

Factory Development Mode is a governed local execution profile, not a waiver of
scope, quality, evidence, or Release Gate obligations. It changes who owns the
runtime, not who owns the governance.

A valid Factory Development Mode instruction must be explicit in the current
instruction and state both of the following:

1. Product Owner authority is being used for AI Bridge self-development.
2. Codex may proceed without an AI Bridge-managed provider execution, active
   provider heartbeat, or Bridge-issued running execution while the managed
   runtime is not yet proven stable.

The Product Owner may optionally bind Factory Development Mode to an existing
canonical Sprint proposal, approved scope, GitHub Issue, or roadmap item. When
such a reference is supplied, Codex must treat it as the exact implementation
boundary and must not broaden it.

When a valid Factory Development Mode instruction is present, Codex must not
return `BLOCKED — BUSINESS DECISION REQUIRED` or
`BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE` solely because any of the
following are absent or unusable:

- an AI Bridge-managed Codex process;
- provider PID or heartbeat;
- durable worker lease;
- live orchestration session;
- automatic resume after server reload;
- Bridge-managed completion call;
- a Bridge-issued Execution Contract, when the instruction explicitly proceeds
  under Product Owner Factory Development Mode authority.

In Factory Development Mode, the local Codex process operates under Product
Owner and repository governance and must:

- read and follow every applicable `AGENTS.md` instruction;
- inspect the Constitution, workflow, roadmap, referenced Issue or Sprint, and
  all relevant architecture and AKB context before mutation;
- record the exact branch and baseline commit before mutation;
- preserve unrelated user work and avoid rewriting shared history;
- use an isolated branch or worktree when appropriate, unless main-only
  development is explicitly required;
- keep a durable local execution record containing scope, baseline, modified
  files, completed steps, remaining steps, validation status, and next action;
- treat server reloads, terminal closure, and provider interruption as
  recoverable execution incidents rather than lost authority;
- continue from the repository state and latest durable checkpoint rather than
  starting a duplicate Sprint;
- run all repository-wide and scope-specific Release Gates;
- generate the same assessment, machine results, acceptance results, migration
  evidence, documentation updates, and closure report required by the normal
  governed path;
- create commits and push or prepare a Pull Request only when requested or
  allowed by the active repository workflow;
- report only genuinely excluded, unsafe, destructive, credential-dependent,
  permission-dependent, or business-decision blockers.

Factory Development Mode does not authorize:

- unrelated changes;
- silent scope expansion;
- bypassing or disabling governance, hash, migration, test, lint, type, evidence,
  or Release Gate validation;
- destructive production operations;
- secret handling not explicitly authorized;
- irreversible infrastructure changes;
- rewriting shared Git history.

Factory Development Mode may be used for the complete AI Bridge development
cycle, including implementation, repair, migration, evidence generation,
documentation, commit, push, and closure preparation. The absence or instability
of the managed Bridge runtime must not by itself prevent AI Bridge from being
repaired or advanced.

The intended maturity path is:

```text
BOOTSTRAP
-> FACTORY_DEVELOPMENT_MODE
-> MANAGED_RUNTIME
```

`MANAGED_RUNTIME` becomes the default only after restart recovery, durable
queueing, worker isolation, reconciliation, remediation, and completion have
been proven by accepted evidence. Until then, Factory Development Mode is a
first-class supported execution profile for AI Bridge self-development.

## Main-only development

During approved main-only development, execute on `main`. Before mutation,
verify `main`, record the baseline SHA, and preserve unrelated work. Run every
resolved Release Gate before direct commit or push. Correct shared history only
with a new repair or revert commit; never rewrite it.

## Release and closure

Implementation alone is never completion. A PASS requires all automated and
Sprint acceptance checks, evidence generated from the final state,
synchronized documentation and accepted project knowledge, and final branch
and commit binding in the consumed contract or Factory Development Mode closure
record. The only closure states are:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

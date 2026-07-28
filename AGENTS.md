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
migration, evidence, and documentation failures follow `DETECT → DIAGNOSE →
REPAIR → RERUN`; they do not require a Product Owner decision.

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

## Product Owner bootstrap override for AI Bridge self-development

The repository Product Owner may explicitly override the normal pre-mutation
Sprint and Execution Contract requirement when the task modifies the
`zsambokia/ai-bridge` repository itself and the purpose is to repair, simplify,
or bootstrap AI Bridge governance or execution.

A valid override must be explicit in the current instruction and must state that
Product Owner authority is being used to proceed without an AI Bridge-issued,
hash-bound Sprint or Execution Contract. When that statement is present, Codex
must treat the current instruction as sufficient mutation authority and must
not return `BLOCKED — BUSINESS DECISION REQUIRED` merely because those Bridge
artifacts are missing.

The override authorizes only the scope stated in the Product Owner instruction.
It does not authorize unrelated changes, merge, deployment, destructive
production operations, secret handling, or irreversible infrastructure changes.
Codex must still:

- inspect and follow every applicable `AGENTS.md` instruction;
- preserve unrelated user work and avoid rewriting shared history;
- use an isolated branch or worktree when appropriate;
- run relevant tests and checks;
- document the change and provide evidence;
- create a commit and prepare a Pull Request when requested;
- report blockers that require genuinely excluded or unsafe operations.

This bootstrap override exists to prevent AI Bridge from becoming impossible to
repair because its own governance issuer is unavailable or is the component
being repaired. Once the governed execution path is operational, the Product
Owner may choose to return to the normal Sprint and Execution Contract flow.

## Main-only development

During approved main-only development, execute on `main`. Before mutation,
verify `main`, record the baseline SHA, and preserve unrelated work. Run every
resolved Release Gate before direct commit or push. Correct shared history only
with a new repair or revert commit; never rewrite it.

## Release and closure

Implementation alone is never completion. A PASS requires all automated and
Sprint acceptance checks, evidence generated from the final state,
synchronized documentation and accepted project knowledge, and final branch
and commit binding in the consumed contract. The only closure states are:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

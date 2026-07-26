# Codex Instructions

This repository is developed through small, isolated, evidence-driven sprints.

Project identity, repository-specific paths, technology profile, Release Gates, and evidence locations must normally be resolved from the validated Execution Contract and the repository's project definition. They must not be hard-coded into this file.

## Temporary Sprint 004 bootstrap exception

This section is a temporary, narrowly scoped bootstrap exception for:

```text
docs/sprints/SPRINT_004_BASIC_AKB_MCP_CONTEXT.md
```

Sprint 004 exists to build the ChatGPT ↔ Bridge MCP execution path and the Bridge context/contract generation capability itself. Requiring that not-yet-proven capability to issue the contract needed to start its own implementation creates a circular dependency.

Therefore, Sprint 004 may start without a Generator-issued `ISSUED` Execution Contract when all of the following are true:

1. the active repository is verified as `zsambokia/ai-bridge`;
2. the active branch is `main`;
3. the exact sprint file above is present and has Product Owner approval;
4. Codex records the pre-mutation baseline SHA;
5. Codex reads the binding repository documents listed below;
6. scope, gates and evidence requirements are taken only from those binding documents and the Sprint 004 specification;
7. no other sprint or unrelated implementation uses this exception.

For this temporary bootstrap execution, use these bindings directly:

- Constitution: `docs/constitution/BRIDGE_CONSTITUTION.md`
- Workflow: `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
- Approved sprint: `docs/sprints/SPRINT_004_BASIC_AKB_MCP_CONTEXT.md`
- Project definition: `.bridge/project.yaml`
- Current state: `docs/akb/CURRENT_STATE.md`
- Roadmap: `docs/roadmap/ROADMAP.md`

Resolve repository-wide Release Gates from `.bridge/project.yaml` and sprint-specific gates from the approved Sprint 004 specification. Create evidence at the path required by that sprint; if the sprint does not yet declare a sufficiently precise evidence path, use:

```text
docs/evidence/sprint-004-chatgpt-bridge-mcp-execution/
```

This exception authorizes execution but does not waive assessment-first development, tests, Release Gates, evidence, documentation synchronization, final commit recording, or honest closure.

As part of Sprint 004, Codex must implement and prove the replacement mechanism so that subsequent sprints can require a Bridge-generated, repository-bound execution context or contract without circular dependency. After that mechanism is proven, this temporary section must be removed or replaced by the permanent generated-context rule.

## Mandatory context

Before changing the repository, read in this order:

1. the Constitution declared by the validated Execution Contract, or by the temporary Sprint 004 bootstrap exception above;
2. the execution workflow declared by the validated Execution Contract, or by the temporary Sprint 004 bootstrap exception above;
3. the exact sprint file declared by the validated Execution Contract, or the exact Sprint 004 file named above;
4. every additional context file declared by the contract, bootstrap exception, or sprint.

Do not infer the active Project, repository, sprint, target branch, baseline, workflow, roadmap milestone, or evidence path from branch names, filenames, issues, pull requests, comments, repository history, or model memory, except for the explicit temporary bindings in the Sprint 004 bootstrap exception.

If a mandatory document is missing or materially contradictory, follow the blocking rules in the Constitution and execution workflow.

## Main-only development policy

During the Product Owner-approved development and pre-production main-only mode, execute on `main`. Before mutation, verify that the current branch is `main`, record the baseline SHA, preserve unrelated work, and run the required Release Gates before a direct commit or push. A pull request is optional. Correct shared history with a new revert or repair commit; do not rewrite it.

## Sprint authority

Only the sprint specification declared by the validated Execution Contract defines the approved implementation scope, except for the exact Sprint 004 bootstrap specification explicitly authorized above.

Implement only that scope. Assess existing code before creating new components. Reuse, repair, or extend canonical components before building new ones. Do not create parallel implementations, speculative abstractions, compatibility layers, or unrelated features.

A roadmap may define direction and sequencing, but it does not authorize implementation. Only the approved sprint does.

## Mandatory execution workflow

Every implementation, repair, migration, recovery, or self-development task must follow the workflow declared by the validated Execution Contract, or the workflow explicitly bound by the temporary Sprint 004 bootstrap exception.

Implementation alone is never completion.

## Release and evidence

Codex must execute every repository-wide and sprint-specific Release Gate declared by the validated Execution Contract. For Sprint 004 bootstrap execution, Codex must execute the gates resolved from `.bridge/project.yaml` and the approved Sprint 004 specification.

A technical PASS is valid only when:

- all required automated checks passed;
- all sprint acceptance scenarios passed;
- evidence was generated from the exact final repository state;
- documentation and accepted project knowledge reflect that final state;
- the final branch and commit SHA are recorded;
- no unresolved technical failure is hidden or reclassified as success.

Ordinary implementation, dependency, test, lint, type, migration, configuration, evidence, and documentation failures require diagnosis, repair, and rerun without Product Owner intervention.

## Allowed closure states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

No other terminal state is allowed.

## Repository-specific configuration

Technology baseline, project documents, sprint roots, evidence roots, repository identity, and Release Gate commands must normally come from the repository's canonical project definition and the issued Execution Contract. During the temporary Sprint 004 bootstrap only, they may be resolved from the explicit bindings above and `.bridge/project.yaml`.

Do not assume Python, Django, Node.js, React, or any other technology unless the project definition, approved architecture, or sprint explicitly declares it.
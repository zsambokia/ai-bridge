# Codex Instructions

This repository is developed through small, isolated, evidence-driven sprints.

Project identity, repository-specific paths, technology profile, Release Gates, and evidence locations must be resolved from the validated Execution Contract and the repository's project definition. They must not be hard-coded into this file.

## Mandatory context

Before changing the repository, read in this order:

1. the Constitution declared by `CONSTITUTION_PATH` in the handoff;
2. the execution workflow declared by `WORKFLOW_PATH` in the handoff;
3. the exact sprint file declared by `APPROVED_SPRINT_PATH` in the handoff;
4. every additional context file declared by the handoff or that sprint.

Do not infer the active Project, repository, sprint, target branch, baseline, workflow, roadmap milestone, or evidence path from branch names, filenames, issues, pull requests, comments, repository history, or model memory.

If a mandatory document is missing or materially contradictory, follow the blocking rules in the Constitution and execution workflow.

## Sprint authority

Only the sprint specification declared by `APPROVED_SPRINT_PATH` defines the approved implementation scope.

Implement only that scope. Assess existing code before creating new components. Reuse, repair, or extend canonical components before building new ones. Do not create parallel implementations, speculative abstractions, compatibility layers, or unrelated features.

A roadmap may define direction and sequencing, but it does not authorize implementation. Only the approved sprint does.

## Mandatory execution workflow

Every implementation, repair, migration, recovery, or self-development task must follow the workflow declared by `WORKFLOW_PATH`.

Implementation alone is never completion.

## Release and evidence

Codex must execute every repository-wide and sprint-specific Release Gate declared by the validated Execution Contract.

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

Technology baseline, project documents, sprint roots, evidence roots, repository identity, and Release Gate commands must come from the repository's canonical project definition and the issued Execution Contract.

Do not assume Python, Django, Node.js, React, or any other technology unless the project definition, approved architecture, or sprint explicitly declares it.
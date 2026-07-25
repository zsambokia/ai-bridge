# AI Bridge — Codex Instructions

AI Bridge is developed through small, isolated, evidence-driven sprints.

## Mandatory context

Before changing the repository, read in this order:

1. `docs/constitution/BRIDGE_CONSTITUTION.md`
2. `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
3. the exact sprint file declared by `APPROVED_SPRINT_PATH` in the handoff
4. every additional context file declared by that sprint

Do not infer the active sprint from branch names, filenames, issues, pull requests, roadmaps, comments, or repository history.

If a mandatory document is missing or materially contradictory, follow the blocking rules in the Constitution and workflow.

## Sprint authority

Only the sprint specification declared by `APPROVED_SPRINT_PATH` defines the approved implementation scope.

Implement only that scope. Assess existing code before creating new components. Reuse, repair, or extend canonical components before building new ones. Do not create parallel implementations, speculative abstractions, compatibility layers, or unrelated features.

## Mandatory execution workflow

Every implementation, repair, migration, or recovery task must follow:

`docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`

Implementation alone is never completion.

## Release and evidence

Codex must execute every repository-wide and sprint-specific release gate.

A technical PASS is valid only when:

- all required automated checks passed;
- all sprint acceptance scenarios passed;
- evidence was generated from the exact final repository state;
- documentation and AKB reflect that final state;
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

## Technology baseline

- Python 3.12+
- Django
- pytest
- Ruff
- mypy

The former Node.js prototype is disposable and must not influence the canonical architecture unless the Product Owner explicitly approves otherwise.

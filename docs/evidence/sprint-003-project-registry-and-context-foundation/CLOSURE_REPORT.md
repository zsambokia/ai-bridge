# Sprint 003 Closure Report

## Scope and assessment

Assessment completed before implementation found the accepted Django Foundation
only: `core` provided the health service, SQLite settings, and release-gate
script. No Project Registry, Project Context, Project Definition loader,
bootstrap command/service, onboarding state, domain migrations, or reusable
domain service existed. The Foundation was retained unchanged; a single new
`projects` domain was required. No parallel implementation was found or added.

The assessment also found static/runtime inconsistencies: the Project Definition
contained runtime onboarding and capability state, while the Execution Contract
used obsolete onboarding names. Sprint 003 resolves them by moving runtime
state to the Registry and Context, removing it from YAML, and aligning the
Contract status vocabulary with the implementation.

## Delivered components

- `projects.Project`: the sole canonical Registry model, with stable identity,
  display name, repository identity, definition path, lifecycle, onboarding,
  and timestamps.
- `projects.ProjectContext`: the sole canonical runtime Context, with all
  required document references, Release Gate configuration, validation state,
  source SHA, and creation time.
- `projects.services`: static Project Definition loader/validator, readiness
  assessment, generic idempotent bootstrap, Context creation, and stale-state
  detection.
- `bootstrap_project`: constrained `BOOTSTRAP` management command.
- `projects.0001_initial`: canonical migration.

No project-name, slug, repository, or technology-specific branch is present in
the platform service. The same path accepts a different valid definition in the
acceptance tests.

## Self-bootstrap evidence

Command executed against the repository, not a fixture or seed:

```text
.venv\Scripts\python.exe manage.py bootstrap_project --definition .bridge/project.yaml --sprint-path docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md --repository-root . --settings=bridge.settings.local
```

Result:

```json
{"context_created": true, "context_status": "VALID", "errors": [], "onboarding_status": "READY", "project_id": "ai-bridge", "registry_created": true, "success": true}
```

The resulting runtime database record was inspected as `ai-bridge`, repository
`zsambokia/ai-bridge`, onboarding `READY`, and Context `VALID`.

## Acceptance evidence

`projects/tests/test_services.py` proves valid and invalid definitions,
bootstrap creation, repeat idempotency, duplicate-repository rejection,
`READY` and `INVALID` onboarding, Context-only-for-`READY`, required Context
sources, `VALID`, `INVALID`, and `STALE` Context behavior. The full pytest suite
passes 9 tests. Structured results are in `acceptance-results.json`.

## Release Gate

The final repository Release Gate command is:

```text
.venv\Scripts\python.exe -m scripts.release_gate
```

It runs Django check, pytest, Ruff lint/format, and mypy in the required order.
The final command result and the exact final `main` SHA are recorded in the
delivery report after publication; no unverified SHA is claimed in this file.

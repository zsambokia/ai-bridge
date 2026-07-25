# Sprint 003 — Persistent Second-Project Acceptance

**Date:** 2026-07-25  
**Result:** Persistent integration acceptance in progress; final release-gate
result is recorded below.

## Real repository and isolated project context

The second project is the real, cloneable GitHub repository
`zsambokia/bridge-demo`, cloned locally at
`C:\Users\User\Documents\dev\bridge-demo`. It was initially empty; its
minimal project-owned governance structure was committed and pushed to its own
`main` branch, not synthesized as a fixture or seed in AI Bridge:

- initial project-definition commit: `c320c4ae04e30143f88e3af80e93c72bdd28ee08`;
- lifecycle-change commit: `781b032c4b70913eb7f577f87601700d450de058`.

The Demo's static `.bridge/project.yaml` declares stable ID `bridge-demo`,
display name `Bridge Demo`, repository `zsambokia/bridge-demo`, branch `main`,
and only its own `AGENTS.md`, Constitution, workflow, Handoff Contract,
Roadmap, approved current sprint, and AKB paths. It contains no runtime Context
state.

## Canonical bootstrap and persistent Registry proof

The normal canonical command, with no direct ORM creation, fixture, seed,
hardcoded project branch, or alternate bootstrap path, was executed as:

```powershell
.venv\Scripts\python.exe manage.py bootstrap_project `
  --definition .bridge/project.yaml `
  --sprint-path docs/sprints/CURRENT_SPRINT.md `
  --repository-root C:\Users\User\Documents\dev\bridge-demo `
  --settings=bridge.settings.local
```

First result: `success=true`, `registry_created=true`, onboarding `READY`,
`context_created=true`, and Context status `VALID`. The persistent local Django
database then contained exactly two Registry records:

| Project ID | Repository | Onboarding |
| --- | --- | --- |
| `ai-bridge` | `zsambokia/ai-bridge` | `READY` |
| `bridge-demo` | `zsambokia/bridge-demo` | `READY` |

The first Demo Context was `VALID` at source SHA
`c320c4ae04e30143f88e3af80e93c72bdd28ee08`, with only Demo paths:
`docs/constitution/CONSTITUTION.md`, `docs/roadmap/ROADMAP.md`,
`docs/sprints/CURRENT_SPRINT.md`, and `docs/akb/CURRENT_STATE.md`.

## Restart, idempotency, and lifecycle

After a separate `manage.py check` process ended and a new Django process
reopened the SQLite development database, the two Registry records, Demo
`READY` onboarding, and its `VALID` Context remained without another bootstrap.

Repeating the same canonical bootstrap returned `registry_created=false` and
`context_created=false`; Registry count remained `2` and Demo Context count
remained `1`.

After the real Demo repository received commit
`781b032c4b70913eb7f577f87601700d450de058`, another canonical bootstrap made
the original Context `STALE` and created a new `VALID` Context at that SHA.
The preserved Demo Context history is therefore:

| Source SHA | Status |
| --- | --- |
| `c320c4ae04e30143f88e3af80e93c72bdd28ee08` | `STALE` |
| `781b032c4b70913eb7f577f87601700d450de058` | `VALID` |

The AI Bridge Registry record remained `READY` throughout.

## Temporary unavailability and recovery

The local Demo checkout was moved, without deletion, to a sibling recovery
path. Canonical bootstrap against the original path failed safely with the
structured error `Project Definition cannot be read` and non-zero exit status.
The checkout was then restored immediately. No Registry or Context record was
deleted or altered: Registry count remained `2`, the Demo Context history above
remained intact, and AI Bridge remained `READY`.

This is the canonical intake validation surface for an unavailable local
repository root; a Context snapshot stores project-relative governance paths,
not an independently mutable local checkout path.

## Admin observability

`projects/admin.py` now registers `Project` and `ProjectContext` in Django
Admin. Both are listable and searchable, display their operational fields, and
deny add, change, and delete permissions, so Admin cannot bypass the canonical
bootstrap lifecycle.

## Release gates and final binding

The repository Release Gate was rerun after the documented correction. Its
command and final result are recorded in the closing commit and report. The
validated implementation-and-evidence commit is
`0c4f5d587f6144b479b9101f8ffd0eac1a446644`; it binds this acceptance run to
the published `main` state.

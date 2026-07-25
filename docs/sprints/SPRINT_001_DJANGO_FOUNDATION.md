# Sprint 001 — Django Foundation

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Target branch:** `sprint/001-django-foundation`  
**Integration target:** `main`  
**Task type:** FOUNDATION  
**Constitution mode:** FOUNDATION

## 1. Purpose

Replace the disposable Node.js prototype with the smallest clean Python/Django foundation that can become the canonical base of AI Bridge.

This is not a migration. The existing Node.js implementation has no compatibility obligation and must not constrain the Django architecture.

The sprint proves only that the repository has a clean, testable, documented Django backend foundation.

## 2. Binding context

Before mutation, read in this order:

1. `AGENTS.md`
2. `docs/constitution/BRIDGE_CONSTITUTION.md`
3. this sprint document
4. existing repository files required to assess and remove the disposable prototype

If the Constitution is not present on the sprint branch, copy the approved canonical document from `origin/docs/bridge-constitution-v1` to `docs/constitution/BRIDGE_CONSTITUTION.md` without changing its meaning, then continue.

## 3. Mandatory assessment

Before writing code, inspect and record:

- current branch and HEAD;
- staged, unstaged, and untracked state;
- current Node.js files and tests;
- reusable documentation or repository conventions;
- files that belong only to the discarded prototype;
- any unrelated user work that must be preserved.

Do not translate or preserve the Node.js architecture by default.

## 4. Approved scope

Create a minimal Django project with:

- Python 3.12 or newer;
- Django;
- a project package named `bridge`;
- one Django application named `core`;
- split settings suitable for local and test execution;
- SQLite as the initial local/test database;
- a JSON health endpoint at `/health/`;
- pytest-based automated tests;
- Ruff for linting and formatting validation;
- mypy with Django-compatible typing configuration;
- Django system-check validation;
- a single canonical backend Release Gate command;
- updated README and current-state AKB documentation.

Use `pyproject.toml` as the canonical dependency and tool configuration file.

No frontend is required in this sprint.

## 5. Required health contract

`GET /health/` must return HTTP 200 and a minimal stable JSON response:

```json
{
  "status": "ok",
  "service": "ai-bridge"
}
```

The endpoint must have an automated test.

## 6. Required project structure

The exact internal layout may be adjusted when technically necessary, but the result must remain small and recognizable. Expected structure:

```text
manage.py
pyproject.toml
bridge/
  __init__.py
  urls.py
  asgi.py
  wsgi.py
  settings/
    __init__.py
    base.py
    local.py
    test.py
core/
  __init__.py
  apps.py
  urls.py
  views.py
  tests/
docs/
  constitution/
  architecture/
  akb/
  sprints/
```

Do not create domain models, workflow engines, integrations, APIs beyond health, UI scaffolding, background jobs, Docker infrastructure, deployment configuration, or generic framework abstractions.

## 7. Disposable prototype removal

After the Django foundation and its tests work, remove files that exist only for the discarded Node.js prototype, including where applicable:

- `package.json`;
- JavaScript source files under `src/`;
- Node-specific tests;
- Node-specific manifest examples;
- README instructions that describe the prototype as the active architecture.

Preserve useful historical information only when it still truthfully describes the project. Do not retain dead compatibility layers.

## 8. Canonical commands

Provide clear commands in the README and `pyproject.toml` configuration for at least:

```text
install development dependencies
run Django locally
run tests
run lint
run formatting check
run typecheck
run Django system check
run the complete backend Release Gate
```

The complete backend Release Gate must execute all mandatory checks in one reproducible command.

A recommended interface is one of:

```text
python -m scripts.release_gate
```

or

```text
make release-gate
```

or a similarly simple repository-native command. Do not introduce a large task-runner framework.

## 9. Documentation requirements

Create or update:

- `README.md` — current Django setup and commands only;
- `docs/architecture/DJANGO_FOUNDATION.md` — concise description of the initial architecture and deliberate exclusions;
- `docs/akb/CURRENT_STATE.md` — exact current state after the sprint;
- the Constitution at its canonical path when not already present on the branch.

Documentation must not describe planned capabilities as implemented.

## 10. Mandatory validation

Codex must execute, repair, and rerun until PASS:

1. dependency installation from a clean environment;
2. Django system check;
3. pytest test suite;
4. Ruff lint;
5. Ruff formatting check;
6. mypy typecheck;
7. complete backend Release Gate command;
8. final clean-working-tree and diff assessment.

Implementation is not completion. Listing a command without executing it is not evidence.

## 11. Acceptance criteria

The sprint is technically ready only when all are true:

- the repository is a working Django project;
- `python manage.py check` passes;
- `/health/` returns the specified JSON contract;
- the health endpoint test passes;
- all automated tests pass;
- lint passes;
- formatting check passes;
- typecheck passes;
- the complete backend Release Gate passes on the exact final state;
- the Node.js prototype is removed rather than maintained in parallel;
- README, architecture documentation, and AKB match the code;
- no out-of-scope feature or abstraction was added;
- final evidence is bound to the final commit.

## 12. Required Codex closure report

The final response must begin with a Hungarian executive summary and include:

- assessment findings;
- files removed from the disposable prototype;
- files created or changed;
- exact commands executed and results;
- backend Release Gate result;
- final branch and commit SHA;
- documentation and AKB update confirmation;
- unresolved blockers, if any;
- one of the allowed terminal states.

## 13. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
```

or, only for a genuine non-technical decision or unavailable external input:

```text
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

Ordinary implementation, dependency, test, lint, type, configuration, or documentation failures are repair work and are not valid reasons to stop.

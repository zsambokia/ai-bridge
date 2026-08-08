# Sprint 07 Release Gate Evidence

## Binding

- Sprint: `AI Bridge 2.0 – Sprint 7: Cognitive & Behaviour Evolution`
- Execution profile: Product Owner-authorised Factory Development Mode
- Branch: `main`
- Baseline commit: `4831371c1903d3f5a652f44912cbb8ca1711fdea`
- Validation state: final implementation state before this evidence record

## Scope evidence

The implementation creates a governed cognitive-evolution lifecycle:

```text
verified RuntimeReflectionCandidate
  -> CognitiveExperience
  -> BehaviourCandidate (non-active)
  -> explicit GovernanceApproval
  -> approved behaviour pattern
  -> CognitiveGuidancePackage
```

`CognitiveExperience`, `BehaviourCandidate`, and `CognitiveGuidancePackage`
are immutable audit artefacts. Behaviour candidates do not change Runtime or
Reasoning behaviour; only candidates with a valid, non-revoked governance
approval can appear in a guidance package. Guidance uses the full approved,
project-scoped set and performs no semantic ranking, preserving Semantic Layer
ownership of retrieval relevance.

## Final Release Gate results

| Gate | Command | Result |
| --- | --- | --- |
| Lint | `ruff check .` | PASS |
| Formatting | `ruff format --check .` | PASS |
| Type checking | `mypy .` | PASS — 246 source files |
| Django system check | `python manage.py check` | PASS |
| Migration drift | `python manage.py makemigrations --check --dry-run` | PASS |
| Migration plan | `python manage.py migrate --plan` | PASS — includes `projects.0063_sprint_07_cognitive_evolution` |
| Scope validation | `python manage.py validate_scopes` | PASS |
| Regression | `python -m pytest -q` | PASS — 363 passed |
| Patch integrity | `git diff --check` | PASS |

## Acceptance evidence

`projects/tests/test_cognitive_evolution.py` verifies the canonical cognitive
E2E path with real persisted project, mission, Runtime reflection, governance
approval, experience, behaviour candidate, and guidance-package records. It
also verifies project isolation, idempotent experience recording, rejection of
missing approval, and immutable candidate contracts.

Focused compatibility validation also passed:

```text
projects/tests/test_cognitive_evolution.py
projects/tests/test_knowledge_pipeline.py
projects/tests/test_orki_runtime_mission_e2e.py
7 passed
```

## Boundary verification

The Sprint 7 service imports no Runtime, Semantic Layer, Knowledge Pipeline,
Reasoning, Structured Decision, or Provider Gateway implementation. The
frozen Runtime is only represented through its public persisted reflection
contract. No embedding, vector-index, AKB mutation, autonomous reasoning, or
autonomous execution is performed by Sprint 7.

## Worktree preservation

Pre-existing Sprint 06 work and the unrelated
`projects/tests/test_factory_chat_browser_e2e.py` modification were retained.
No commit or push was requested or performed.

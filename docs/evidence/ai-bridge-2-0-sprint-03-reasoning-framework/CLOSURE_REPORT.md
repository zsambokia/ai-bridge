# Sprint 03 Reasoning Framework — Engineering Closure Evidence

## Scope and boundary

The Product Owner authorized Factory Development Mode for Sprint 03 on `main`
from baseline `74d1e2832df33d04672530c3a7c267cdc3da073b`. The delivered
`projects.reasoning` package is an in-memory, typed pipeline from
`SemanticContextV2` to `StructuredDecision`. It has no execution, provider,
Runtime, AKB, state-machine, database-model, or migration responsibility.

## Acceptance evidence

`projects/tests/test_reasoning_framework.py` proves the canonical path:

```text
Semantic Context -> Understanding -> Situation -> Behaviour -> Reasoning
                 -> Critic -> Planning -> Structured Decision -> STOP
```

The same acceptance module verifies stage artifacts and critic feedback when
semantic evidence is absent. Planning returns evidence-bearing dependent tasks;
it does not dispatch them.

## Final engineering release gate

Executed from the final implementation state on 2026-08-08:

| Gate | Result |
| --- | --- |
| `ruff check .` | PASS |
| `mypy .` | PASS — 229 source files |
| `python manage.py check` | PASS |
| `python manage.py migrate --plan` | PASS — no planned operations |
| `python manage.py validate_scopes` | PASS |
| `python -m pytest -q` | PASS — 348 tests in 105.28 seconds |
| `git diff --check` | PASS |

No migration was required. The pre-existing user modification to
`projects/tests/test_factory_chat_browser_e2e.py` was preserved and excluded
from this Sprint's changes.

## Architecture evidence

`docs/architecture/REASONING_FRAMEWORK.md` records the ownership boundary and
the Semantic Layer's candidate-only contract. `docs/architecture/SEMANTIC_LAYER.md`
now records Sprint 02 as operational and the handoff to Reasoning. This is
engineering acceptance only; Product Owner acceptance remains the next
lifecycle step.

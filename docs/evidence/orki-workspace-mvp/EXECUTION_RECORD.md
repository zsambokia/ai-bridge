# Orki Workspace MVP — Factory Development Mode execution record

- Product: `ai-bridge` / `zsambokia/ai-bridge`
- Branch: `main` (main-only development)
- Baseline: `bf6f886bb5a08187eafb9cccd02b662ff9856f66`
- Authority: Product Owner Factory Development Mode instruction for **AI Bridge 1.0 – Orki Workspace MVP**.
- Managed-provider exception: explicitly authorized; no Bridge-issued running contract, provider heartbeat, or managed execution was required.
- Scope: Workspace projection shell, Orki/Runtime continuity, governed repository intake controls, documentation, tests, and Release Gates.

## Completed work

1. Kept `/` as the compatible Factory Chat ingress and made it the Orki Workspace shell.
2. Added the canonical navigation: Home, Orki, Projects, Knowledge, Repository, Execution, Roadmap, Decisions, Runtime, Evidence, and Administration.
3. Added read-only projections for the existing Project, Runtime/OESM, Context Package, roadmap, cognitive decision, evidence, and repository receipt owners.
4. Kept the existing EventSource-based Runtime stream; the browser remains a projection client and does not poll or own OESM state.
5. Added Bootstrap, Sync, and Reindex controls behind `RepositoryBootstrapLifecycle`; they require a valid approval reference and never invoke GitHub from the Workspace directly.
6. Added Django regression coverage for the shell and approval-reference boundary.
7. Replaced the direct HTTP-response chat rendering path with a Conversation Engine that accepts Runtime ingress, subscribes to the existing SSE stream, and evolves one operational-language Orki bubble from Runtime events only.
8. Recorded Context Package, reasoning, verification, reflection, and Knowledge Candidate observations in the existing Runtime event stream. The candidate is immutable Runtime evidence; it does not mutate the AKB.
9. Added a Runtime-owned mission-understanding gate: an underspecified mission
   follows `UNDERSTANDING -> SEMANTIC_SEARCH -> GAP_ANALYSIS ->
   QUESTION_GENERATION -> WAITING_USER`; it cannot enter Planning.
10. Made readiness deterministic: planning requires confidence of at least
    `0.90`, zero open questions, and zero critical unknowns. The provider is an
    observation source and cannot override this rule.
11. Added acceptance coverage for an underspecified mission, multiple
    question-and-answer rounds, and Planning only after all critical mission
    fields are resolved.

## Files changed by this scope

- `projects/factory_chat.py`
- `projects/factory_missions.py`
- `projects/factory_orki.py`
- `projects/orki_runtime.py`
- `projects/models.py`
- `projects/migrations/0065_orki_question_gate.py`
- `projects/runtime_api.py`
- `projects/ui_urls.py`
- `projects/templates/projects/factory_chat.html`
- `projects/templates/projects/factory_context_status.html`
- `projects/templates/projects/factory_plan_review.html`
- `projects/tests/test_factory_chat.py`
- `projects/tests/test_factory_chat_browser_e2e.py`
- `projects/tests/test_factory_chat_runtime_integration.py`
- `projects/tests/test_structured_decision_runtime.py`
- `docs/evidence/orki-workspace-mvp/*`

## Validation status

- PASS: `ruff check .`
- PASS: `mypy .` (253 source files)
- PASS: `python manage.py check`
- PASS: `python manage.py makemigrations --check --dry-run`
- PASS: `python manage.py validate_scopes`
- PASS: `pytest projects/tests/test_factory_chat.py -q` (36 passed)
- PASS: `python -m pytest projects/tests/test_factory_chat_runtime_integration.py projects/tests/test_factory_chat.py -q` (40 passed)
- PASS: `python -m pytest projects/tests/test_factory_chat_browser_e2e.py -q` (15 passed)
- PASS: `python -m pytest projects/tests/test_orki_decision_release_gate.py projects/tests/test_orki_mission_understanding_release_gate.py projects/tests/test_orki_recommendation_release_gate.py projects/tests/test_factory_chat_runtime_integration.py -q` (8 passed)
- PASS: `python -m pytest -q` (380 passed)

## Recovery / next action

The local state is durable in the files above. Do not recreate the Workspace if interrupted; rerun the final gates from the recorded baseline and continue from the current worktree. No commit was created because the Product Owner did not request a commit or push, and unrelated in-progress work was already present on `main`.

## Continuation: chat-first plan review

- Scope refinement: the Product Owner identified that a decision card without a readable plan is a process failure. The primary workspace is therefore the chat/worklog; the right rail is a compact, read-only live projection.
- Change: a pending canonical `FactoryPlan` is rendered as an Orki plan-review card in `#chat-messages`, including assumptions, alternatives, impact, recommendation, and the existing governed approve/request-changes/reject actions.
- Change: the context-refresh response carries the same plan-review fragment in an inert template, which the browser moves into the chat after a canonical state refresh. The sidebar no longer renders a decision card or its actions.
- Governance: no approval route, plan state transition, Runtime owner, or client-side authorization rule was changed. The existing server-side Factory Plan actions remain the sole decision authority.
- PASS: `ruff check .` and `git diff --check`.
- PASS: `mypy .` (253 source files), `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `python manage.py validate_scopes`.
- PASS: focused chat-plan/context tests (8 passed) and the repository-wide suite: `python -m pytest -q` (378 passed in 117.66s).

# Issue #17 corrective sprint — execution record

## Authority and baseline

- Authority: Product Owner Factory Development Mode instruction, supplied on
  2026-08-01 as “Issue #17 Corrective Sprint: Conversational Product Owner
  Experience”.
- Repository: `zsambokia/ai-bridge`
- Branch: `main`
- Baseline: `c19bf91327c106b7c1207a78f61c31b2f5832459`
- Task type: corrective UI, backend projection, interaction, documentation,
  and acceptance work for the Factory Chat.

## Assessed, reused components

The existing Factory Chat request-time projection, `FactoryPlan` and its
canonical proposed-scope lifecycle, Project Registry, `ExecutionRun` coding
projection, and AKB candidate-review lifecycle are reused.  This sprint does
not introduce browser-owned authority, provider dispatch, or a parallel
project/scope/approval lifecycle.

## Workspace preservation

The pre-existing modified files and untracked runtime, configuration, evidence,
operation, sprint, and work-item paths visible in the baseline `git status`
are unrelated user work.  They are explicitly excluded from this sprint.

## Implemented scope

- Replaced the form-led Factory Chat projection with a Hungarian, adaptive
  four-question discovery conversation.  It creates one reviewable plan only
  after discovery and presents one plain-language approval action.
- Added a conversational `Új projekt` path: project intent -> Orki questions
  -> plan review -> approval -> clearly stated environment-preparation next
  step.  Canonical Project and FactoryPlan services remain authoritative.
- Reworked the right panel to show only the current task, flow state, next
  step, the Product Owner action, and an actual deployment preview when one is
  available.  Technical identifiers are confined to `Technikai részletek`.
- Added Hungarian translations for the requested execution states and a
  context-derived answer for `Hogyan érhető el az alkalmazás?`; with no
  deployed preview it returns the current request URL.
- Added progressive fetch enhancement for message, project, plan, and memory
  actions, including success and error feedback.  Ordinary form submission
  remains the JavaScript-free fallback.
- Deferred optional AKB candidate creation for a just-created project until
  its context is ready; this prevents an internal context error in the new
  project conversation while preserving the canonical memory-review process
  for registered projects.

## Changed files

- `projects/factory_chat.py`
- `projects/factory_planning.py`
- `projects/ui_urls.py`
- `projects/templates/projects/factory_chat.html`
- `projects/templates/projects/factory_context_status.html`
- `projects/tests/test_factory_chat.py`
- `projects/tests/test_factory_chat_browser_e2e.py`

## External delivery boundary

The specified target was checked directly on 2026-08-01:

```text
git ls-remote https://github.com/zsambokia/demo17-repo.git HEAD
remote: Repository not found.
fatal: repository 'https://github.com/zsambokia/demo17-repo.git/' not found
```

No repository access or project definition for that exact target is available,
so a real clone, push, registration/bootstrap, execution, preview deployment,
or end-to-end delivery for it cannot be honestly claimed.  No substitute demo
repository was used.

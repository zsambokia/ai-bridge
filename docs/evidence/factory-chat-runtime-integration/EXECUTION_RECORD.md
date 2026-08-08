# Factory Chat Runtime Integration — Factory Development Mode record

**Authority:** Product Owner Factory Development Mode authorization in the current
conversation, 2026-08-08. The authorization explicitly permits AI Bridge
self-development without a Bridge-managed provider execution, heartbeat, or
Bridge-issued running execution while the bootstrap Runtime is being proven.

**Scope:** Make the Orki Runtime the mandatory execution path for every Factory
Chat user message. The canonical path is Browser → Factory Chat → Runtime
Ingress → Goal → Understanding → Semantic Selection → Planning → Execution →
Provider → Verification → Reflection → Knowledge Integration (when required) →
Completed. Explicit diagnostic endpoints are excluded. Governance, approvals,
queues, ExecutionRun, and Cognitive State ownership remain unchanged.

**Mode:** Factory Development Mode (bootstrap sprint); no AI Bridge-managed
ExecutionRun is created for this self-development work.

## Baseline and workspace

- Repository: `zsambokia/ai-bridge`
- Branch: `main`
- Baseline commit: `262ec6700b5b5481fcf917c8eb86e9114998abd8`
- Baseline recorded: 2026-08-08
- Workspace condition: existing modified and untracked files predate this
  sprint. They are preserved as user work; only files needed for this scoped
  Runtime integration are changed.

## Assessment

The repository already contains provider-neutral Runtime domain objects
(`OrkiGoal`, `OrkiPlan`, `OrkiExecution`, `OrkiRuntimeEvent`, `OrkiReflection`,
and `OrkiKnowledgeIntegration`) and a persisted OESM in
`projects/orki_runtime.py`. The existing `factory/message/` view instead calls
`factory_orki.reply` directly. That legacy boundary dispatches to the provider
and directly applies Cognitive State observations, so it is a bypass of the
Runtime, Context Builder lifecycle, event stream, reflection, and knowledge
integration.

The sprint extends the existing Runtime coordinator and event records, and
turns Factory Chat into a thin Runtime ingress/presentation adapter. It does
not introduce a second state machine, provider abstraction, queue, approval,
or Cognitive State store.

## Implementation record

- Factory Chat is a thin Runtime ingress: it creates a live execution and
  returns its projection; it does not invoke a provider.
- The Runtime owns Factory Chat Goal/Plan creation, semantic-selection events,
  provider dispatch, verification, reflection, optional knowledge-candidate
  submission, completion, and concrete external waiting.
- The Runtime API exposes dispatch and the bounded SSE Runtime Event Stream.
  The dispatch projection includes the channel transcript for the UI.
- The Factory Chat UI subscribes to the Runtime Event Stream and renders the
  Live Runtime Monitor / Runtime Inspector.
- The legacy factory_orki reply entrypoint delegates to Runtime compatibility
  code; it is not a direct Factory Chat route.
- The focused acceptance test proves the real Runtime chain against a mocked
  external provider and verifies the concrete provider-unavailable wait.

## Validation checkpoint

- `python manage.py check`: PASS.
- `python manage.py test projects.tests.test_orki_runtime projects.tests.test_orki_runtime_migration projects.tests.test_factory_chat_runtime_integration --verbosity 1`: PASS (7 tests).
- `python manage.py test projects.tests.test_factory_chat_runtime_integration --verbosity 2`: PASS (2 tests). It verifies the real OESM and Runtime event chain with only the external provider mocked, plus the concrete provider-unavailable waiting state.
- `python manage.py test projects.tests.test_factory_chat --verbosity 1`: FAIL (7 failures, 3 errors). The failures assert the removed direct Cognitive State mutation and direct `factory_chat.orki_reply` dispatch contract. They must be replaced by Runtime event/Reflection/Knowledge-Integration acceptance assertions; restoring them would reintroduce the prohibited bypass.
- Full repository suite: previously reached 111 tests and failed with the same legacy Chat contract family; it is not a Release-Gate PASS.
- Browser automation: unavailable in this Codex session because the in-app
  browser is not provisioned; this is a remaining operational-acceptance
  dependency.

## Remaining steps

1. Migrate the legacy Factory Chat assertions to the approved Runtime event and Reflection / Knowledge Integration contract, then rerun the full Release Gate suite.
2. Complete the UI operational acceptance in a provisioned browser session.
3. Record final results and Product Owner review handoff.

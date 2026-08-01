# Issue #19 — Orki COO evidence

## Factory Development Mode record

- Repository: `zsambokia/ai-bridge`
- Branch at start: `agent/issue-17-conversational-po`
- Baseline: `4277f8b77d480f3f4523c144af886a00c80f540f`
- Execution profile: Product Owner Factory Development Mode
- Date: 2026-08-01

## Current-state audit and negative evidence

Before the change, Factory Chat contained a fixed `DISCOVERY_QUESTIONS` array
and `_finish_discovery` generated a plan only after the fixed answer sequence.
The browser composer was a single-line input and its panels did not implement
the required conversation-only scrolling contract.  These source-level facts
are retained as negative evidence; the legacy helpers remain in
`projects/factory_chat.py` for historical traceability but are no longer used
by the live message endpoint.

The audited runtime route is now:

```text
Factory Chat POST /message
  -> projects.factory_chat._reply_to_message
  -> projects.factory_orki.reply
  -> select_model_provider
  -> ExecutionProvider query and credential resolution
  -> server-side provider invocation
  -> FactoryMission update / canonical FactoryPlan artifact
  -> one-time approval / repository service / Project Registry
```

## Provider-resolution proof

The local provider registry was inspected without exposing credentials.

| Provider | Role | Status | Result |
| --- | --- | --- | --- |
| `openai` | `MODEL_API` | enabled, `ACTIVE` | selected for Orki model inference |
| `codex-cli` | `EXECUTION_AGENT` | enabled, `ACTIVE` | correctly excluded: it is not `MODEL_API` and has no `MODEL_INFERENCE` capability |

`select_model_provider` accepts only an enabled, `ACTIVE` provider whose role
is `MODEL_API` and capabilities include `MODEL_INFERENCE`.  The browser never
contacts the provider: invocation is in `projects.factory_orki` after the
server resolves the configured provider and credential binding.

One real server-side OpenAI call completed successfully:

```text
provider: openai
model: gpt-4.1-mini
timestamp: 2026-08-01T11:23:26.450686+00:00
prompt/context hash: 2c56e8bb1d92ed1458960c354160c2afe4a1199949e941bb01ed17127f5b6f61
response hash: 01fc5ba345a5fbb966dbf753b65ecdc2e4aa76f8070bc2e68a040006959516c9
latency: 1901 ms
usage: input 44, output 17, total 61
result: success
```

No fixture generated this response, and no credential value is recorded here.

## Repository operational proof

Created private disposable repository (retained pending Product Owner review):

- URL: https://github.com/zsambokia/ai-bridge-issue-19-proof-20260801
- owner: `zsambokia`
- visibility: `PRIVATE`
- default branch: `main`
- initial commit and remote main revision:
  `74493181162db9238788f54ac3d21563841b0ed9`
- Project Registry: `issue-19-repository-proof-20260801` ->
  `zsambokia/ai-bridge-issue-19-proof-20260801`, onboarding `READY`

The server-side service first checked authenticated GitHub identity and
repository existence, then created the repository, initialized the local
workspace, committed README and `.gitignore`, pushed `main`, and persisted the
registry link.  A second invocation returned `created=False` with the same
commit, proving retry idempotency.  No existing repository was overwritten.

## Verification run

```text
python manage.py migrate --settings=bridge.settings.local        PASS (0045 applied)
python manage.py check --settings=bridge.settings.test           PASS
python -m ruff check <Issue #19 source and tests>                PASS
python manage.py test --settings=bridge.settings.test            PASS: 44 tests, 4 skipped
```

The browser suite includes COO response persistence, plan controls, fixed
three-column desktop layout, conversation-only scrolling, multiline send,
Shift+Enter newline and empty-send protection.

## Modern Conversational UX correction — 2026-08-01

The original Plan approval controls were embedded after the long Plan preview,
so they could be outside a normal 100% browser viewport.  The pending Plan now
has a dedicated `Terv elkészült` card at the top of the fixed Mission panel.
It presents the three Product Owner decisions without requiring zoom or a
conversation-pane scroll:

- `Jóváhagyom` invokes the canonical server-side approval continuation.
- `Módosítást kérek` and `Elutasítom` retain their required-reason forms and
  invoke their canonical server-side operations.
- An unambiguous natural-language approval (`Jóváhagyom`, `ok, mehet`, and
  equivalent normalized forms) invokes that same approval continuation; it is
  recorded in the durable conversation transcript and does not invoke the
  provider to infer a decision.

The Composer is an accessible multiline textarea: Enter submits, Shift+Enter
inserts a newline, IME composition cannot submit, whitespace-only messages are
rejected, and one in-flight interaction disables the textarea and action
buttons.  During that interval the UI exposes an `Orki gondolkodik…` live
status with the actual server-side stage currently known to the browser.

Conversation auto-scroll follows new content only when the reader was already
near the bottom.  The Projects panel, Mission panel, and Composer remain fixed
on desktop; only the Conversation message region scrolls.  Draft text remains
in session storage for safe refresh restoration.

The current provider adapter returns a complete server response rather than a
token stream.  The UI deliberately does not fabricate streaming.  Native
incremental rendering remains conditional on a server-side provider streaming
protocol and will use the same server-owned request path when that capability
is added.

### Correction validation

```text
python manage.py test projects.tests.test_factory_chat \
  projects.tests.test_factory_chat_browser_e2e --verbosity 1
PASS: 36 tests, 4 intentionally skipped

python -m ruff check projects/factory_chat.py \
  projects/tests/test_factory_chat.py \
  projects/tests/test_factory_chat_browser_e2e.py
PASS
```

The Chromium suite now covers textarea keyboard behavior, duplicate-send
protection, the temporary Composer lock, and the visible thinking state while
a delayed server response is in flight.  Its response transport is mocked only
for browser interaction determinism; the real provider evidence above remains
the provider-path proof.

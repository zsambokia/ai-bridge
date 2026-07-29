# Provider activity fidelity acceptance results

Scope: `bridge:ai-bridge:sprint:b138a008-a53c-42ed-a836-462c885cffbe`
Proposal: version `1`, hash `da41810c2c5092154bd9d89b3f995c8ec41efc65bed1eb17e7bc442733d541d9`

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| Structured Codex activity is retained as typed, redacted data | PASS | `test_codex_activity_projection_retains_redacted_structured_provider_output` |
| A JSON scalar cannot crash the reader | PASS | `test_codex_activity_projection_accepts_a_json_string_without_stopping` covers the reported top-level JSON string followed by a completion event. |
| A per-line projection failure does not stop subsequent activity | PASS | `test_codex_activity_projection_continues_after_an_unexpected_projection_error` |
| stdout and stderr remain distinguishable | PASS | The adapter starts independent readers and retains `source_stream`, `stdout`, and `stderr`. |
| Provider event ids are idempotent per run | PASS | `ExecutionProgressEvent.provider_event_id` has a conditional unique constraint and `add_event` returns an existing event. |
| Output is bounded and secrets are redacted before persistence and views | PASS | `redact_value`, `bounded_text`, and provider projection tests. |
| Activity, Provider Output, and Raw Events are separately readable | PASS | `execution.list_events` accepts `ACTIVITY`, `PROVIDER_OUTPUT`, and `RAW_EVENTS`. |
| Full automated gate | PASS | See `MACHINE_RESULTS.md`. |

The fix is deliberately fail-safe: provider data is not executed, and unknown or
invalid lines become bounded, redacted observational events. No production run
or contract was modified during validation.
